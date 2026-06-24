#!/usr/bin/env python3
"""Independent single-map vote resolution for eascape0101 (s1) / Escapists201 (s2).

Checked weekly (systemd timer, Monday 07:00 UTC). Each server runs its own
poll -- quorum is just one vote, the top-voted candidate wins the cycle.
Every check ends the cycle (calendar-reset model, not cumulative): the tally
is cleared and the cycle number bumped regardless of outcome, so a vote never
carries over into next week.

Zero votes that week falls back to map_polls.json's per-server
"zero_vote_mode":
  - "keep":     leave the current map alone, just restart the poll.
  - "simulate": fabricate a plausible-looking random tally and pick a winner
                from it, so the rotation keeps moving even with no real votes.

A real swap edits each instance's GenericModule.kvp: the winning map's mod is
added (add-only -- never removes an existing terrain mod, since unused ones
are harmless) and App.AppSettings.CustomMission is repointed at the winning
map's missionConf. This replaces the old shared 3-slot cumulative pool +
in-game Vote-For-Escapist system (see archived map-vote-system-v1 memory).

Usage: single-map-vote.py [--dry-run]
"""
import json
import os
import random
import re
import sqlite3
import subprocess
import sys
import time

DATA_DIR     = "/opt/horselab-status/data"
DB_PATH      = os.path.join(DATA_DIR, "votes.db")
CATALOG_PATH = os.path.join(DATA_DIR, "map_catalog.json")
POLLS_PATH   = os.path.join(DATA_DIR, "map_polls.json")
LOG_PATH     = "/root/single-map-vote.log"

INSTANCE_BASE = {
    "eascape0101":  "/home/amp/.ampdata/instances/eascape0101",
    "Escapists201": "/home/amp/.ampdata/instances/Escapists201",
}

MOD_INSERT_ANCHOR = '{ \\"modId\\": \\"5AAAC70D754245DD\\", \\"name\\": \\"Server Admin Tools\\" }'

DRY_RUN = "--dry-run" in sys.argv


def log(msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}]{' [DRY-RUN]' if DRY_RUN else ''} {msg}"
    print(line)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_catalog():
    with open(CATALOG_PATH, encoding="utf-8") as f:
        return {m["id"]: m for m in json.load(f)["maps"]}


def load_polls():
    with open(POLLS_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_polls(polls):
    if DRY_RUN:
        log("(dry-run, not writing map_polls.json)")
        return
    with open(POLLS_PATH, "w", encoding="utf-8") as f:
        json.dump(polls, f, indent=2)


def get_tally(server, cycle_id):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT map_id, COUNT(*) FROM map_votes WHERE server = ? AND cycle_id = ? GROUP BY map_id",
        (server, cycle_id),
    ).fetchall()
    conn.close()
    return dict(rows)


def clear_cycle(server, cycle_id):
    if DRY_RUN:
        return
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM map_votes WHERE server = ? AND cycle_id = ?", (server, cycle_id))
    conn.commit()
    conn.close()


def pick_simulated_winner(catalog, current_map_id):
    eligible = [m for m in catalog.values() if m.get("eligible") and m["id"] != current_map_id]
    if not eligible:
        return None, {}
    winner = random.choice(eligible)
    fake_tally = {winner["id"]: random.randint(1, 4)}
    extras = random.sample([m for m in eligible if m["id"] != winner["id"]],
                            k=min(2, len(eligible) - 1))
    for m in extras:
        fake_tally[m["id"]] = random.randint(1, fake_tally[winner["id"]])
    return winner["id"], fake_tally


def edit_kvp_for_swap(kvp_path, winner):
    content = open(kvp_path, encoding="utf-8").read()
    applied = []

    if winner.get("modId"):
        if f'\\"modId\\": \\"{winner["modId"]}\\"' in content:
            applied.append(f"mod already present: {winner['modName']}")
        else:
            c = content.count(MOD_INSERT_ANCHOR)
            if c != 1:
                log(f"  [ABORT] {kvp_path}: anchor for adding {winner['modName']} found {c}x, expected 1")
                return None
            new_entry = f'{{ \\"modId\\": \\"{winner["modId"]}\\", \\"name\\": \\"{winner["modName"]}\\" }},\\n  {MOD_INSERT_ANCHOR}'
            content = content.replace(MOD_INSERT_ANCHOR, new_entry, 1)
            applied.append(f"added mod {winner['modName']}")

    pattern = r'"CustomMission":"[^"]*"'
    matches = re.findall(pattern, content)
    if len(matches) != 1:
        log(f"  [ABORT] {kvp_path}: CustomMission pattern found {len(matches)}x, expected 1")
        return None
    replacement = f'"CustomMission":"{winner["missionConf"]}"'
    content = re.sub(pattern, replacement, content, count=1)
    applied.append(f"CustomMission -> {winner['missionConf']}")

    if not DRY_RUN:
        with open(kvp_path, "w", encoding="utf-8") as f:
            f.write(content)
    return applied


def run(cmd):
    if DRY_RUN:
        log(f"(dry-run, would run) {cmd}")
        return
    subprocess.run(cmd, shell=True, check=True)


def apply_swap(instance_id, winner):
    base = INSTANCE_BASE[instance_id]
    kvp_path = os.path.join(base, "GenericModule.kvp")

    backup = f"{kvp_path}.bak-singlemapvote-{time.strftime('%Y%m%d-%H%M%S')}"
    run(f"cp -p '{kvp_path}' '{backup}'")
    log(f"{instance_id}: backed up KVP to {backup}")

    run(f"su - amp -c 'ampinstmgr --StopInstance {instance_id}'")

    applied = edit_kvp_for_swap(kvp_path, winner)

    if applied is None:
        log(f"{instance_id}: KVP edit aborted, restarting with no changes")
        run(f"su - amp -c 'ampinstmgr --StartInstance {instance_id}'")
        return False

    log(f"{instance_id}: {applied}")
    run("chown -R amp:amp /home/amp/.ampdata/")
    run(f"su - amp -c 'ampinstmgr --StartInstance {instance_id}'")
    return True


def resolve_server(server_key, poll, catalog):
    instance_id = poll["instance_id"]
    cycle = poll.get("cycle_id", "1")
    current_map_id = poll.get("current_map")
    real_tally = get_tally(server_key, cycle)

    if real_tally:
        winner_id = max(real_tally, key=lambda k: real_tally[k])
        tally_used = real_tally
        kind = "real"
    elif poll.get("zero_vote_mode", "simulate") == "simulate":
        winner_id, tally_used = pick_simulated_winner(catalog, current_map_id)
        kind = "simulated"
        if winner_id is None:
            log(f"{server_key}: no eligible candidates to simulate, keeping current map")
            winner_id, tally_used, kind = current_map_id, {}, "no-op"
    else:
        log(f"{server_key}: zero votes, mode=keep -- keeping current map, restarting poll")
        winner_id, tally_used, kind = current_map_id, {}, "kept"

    winner = catalog.get(winner_id) if winner_id else None
    swapped = False
    if winner and winner_id != current_map_id:
        log(f"{server_key}: cycle {cycle} winner ({kind}): {winner['name']} (tally: {tally_used})")
        swapped = apply_swap(instance_id, winner)
        if not swapped:
            log(f"{server_key}: swap aborted, NOT updating current_map -- will retry next check")
            return
    else:
        log(f"{server_key}: cycle {cycle} -- staying on current map ({kind}, tally: {tally_used})")

    clear_cycle(server_key, cycle)
    new_cycle = str(int(cycle) + 1)
    poll["cycle_id"] = new_cycle
    poll["last_resolved"] = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    if swapped:
        poll["current_map"] = winner_id
        poll["last_result"] = f"{kind}: switched to {winner['name']} (tally: {tally_used})"
    else:
        poll["last_result"] = f"{kind}: no change ({(winner or {}).get('name', 'current map')})"
    log(f"{server_key}: cycle {cycle} complete -- now on cycle {new_cycle}")


def main():
    catalog = load_catalog()
    polls = load_polls()
    for server_key, poll in polls.items():
        resolve_server(server_key, poll, catalog)
    save_polls(polls)
    return 0


if __name__ == "__main__":
    sys.exit(main())
