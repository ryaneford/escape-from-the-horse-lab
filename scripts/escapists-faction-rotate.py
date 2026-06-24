#!/usr/bin/env python3
"""Daily safe faction rotation for eascape0101 / Escapists201.

The Escapists missionHeader documentation (A4-Escapists-Docs wiki) is explicit:
m_sPlayerFaction "should not be the same as the occupying faction" -- and that
exclusion is NOT enforced by the engine when both fields are independently set
to the native "RANDOM" keyword. So this script does the randomization itself,
guaranteeing player != occupying, and writes the literal resolved FactionKey
values into missionHeader instead of ever using "RANDOM" for these two fields.

Faction compatibility (corrected 2026-06-24, second correction same day):
the previous version picked player/occupying independently from two flat
pools, which only guaranteed the two keys weren't identical -- it didn't
know that several *different* keys still represent the same real-world side
(e.g. RHS_USAF and NATO both read in-game as US-aligned content). That
produced a live "USAF vs US Army" same-side round on S1.

Fixed by replacing the flat pools with COMPATIBILITY, a directional
occupying-key -> [allowed player keys] map read directly off Ryan's own
in-game manual-setup-menu testing (Test01, m_bUseSetupMenu=1) on
2026-06-24 -- i.e. exactly the choices the game's own menu offers for each
occupying selection, not inferred from mod filenames or engine constants
(both proved unreliable earlier this same investigation). This is
deliberately NOT assumed symmetric -- the menu itself isn't (e.g. RHS_USAF
is an allowed player choice when occupying=USSR, but RHS_USAF's own row
doesn't offer USSR's reverse menu the same way), so pick_pair() always
selects occupying first, then samples player from that occupying's own
list, exactly mirroring how the in-game menu is actually driven.

One additional manual override on top of the raw menu data: RHS_USAF is
removed from NATO's allowed-player list. The menu technically permits this
pairing, but it produces a same-side-presenting round in practice (NATO's
catalog reads as US-aligned content, confirmed live 2026-06-24) -- the menu
checks faction IDs, not visual/thematic overlap, so this case needs a
manual carve-out the menu itself won't catch. Add further carve-outs here
if Ryan reports more of these from actual play.

Run daily via systemd timer. Restarts both instances to apply (missionHeader
changes only take effect on restart, same as every other AMP config edit).
Usage: escapists-faction-rotate.py [--dry-run]
"""
import os
import random
import re
import subprocess
import sys
import time

INSTANCE_BASE = {
    "eascape0101":  "/home/amp/.ampdata/instances/eascape0101",
    "Escapists201": "/home/amp/.ampdata/instances/Escapists201",
}

# occupying key -> allowed player keys, straight from the in-game setup menu.
COMPATIBILITY = {
    "US":       ["EDF", "RHS_AFRF", "USSR"],
    "UK":       ["EDF", "RHS_AFRF", "USSR"],
    "EDF":      ["US", "UK", "RHS_USAF", "RHS_AFRF", "USSR"],
    "RHS_USAF": ["EDF", "RHS_AFRF", "USSR"],
    "RHS_AFRF": ["US", "UK", "EDF", "RHS_USAF"],
    "NATO":     ["EDF", "RHS_AFRF", "USSR"],  # RHS_USAF manually excluded, see module docstring
    "USSR":     ["US", "UK", "EDF"],
    "USSR_NI":  ["US", "UK", "EDF", "RHS_USAF", "RHS_AFRF"],
}

LOG_PATH = "/root/escapists-faction-rotate.log"
DRY_RUN = "--dry-run" in sys.argv


def log(msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}]{' [DRY-RUN]' if DRY_RUN else ''} {msg}"
    print(line)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def pick_pair():
    occupying = random.choice(list(COMPATIBILITY.keys()))
    player = random.choice(COMPATIBILITY[occupying])
    return player, occupying


def run(cmd):
    if DRY_RUN:
        log(f"(dry-run, would run) {cmd}")
        return
    subprocess.run(cmd, shell=True, check=True)


def edit_kvp(kvp_path, player, occupying):
    content = open(kvp_path, encoding="utf-8").read()

    player_pattern = r'\\"m_sPlayerFaction\\": \\"[^"]*\\"'
    occ_pattern = r'\\"m_sOccupyingFaction\\": \\"[^"]*\\"'

    if len(re.findall(player_pattern, content)) != 1 or len(re.findall(occ_pattern, content)) != 1:
        log(f"  [ABORT] {kvp_path}: expected exactly 1 match each for player/occupying patterns")
        return None

    content = re.sub(player_pattern, f'\\\\"m_sPlayerFaction\\\\": \\\\"{player}\\\\"', content, count=1)
    content = re.sub(occ_pattern, f'\\\\"m_sOccupyingFaction\\\\": \\\\"{occupying}\\\\"', content, count=1)

    if not DRY_RUN:
        with open(kvp_path, "w", encoding="utf-8") as f:
            f.write(content)
    return True


def rotate_instance(instance_id):
    base = INSTANCE_BASE[instance_id]
    kvp_path = os.path.join(base, "GenericModule.kvp")
    player, occupying = pick_pair()

    backup = f"{kvp_path}.bak-factionrotate-{time.strftime('%Y%m%d-%H%M%S')}"
    run(f"cp -p '{kvp_path}' '{backup}'")
    log(f"{instance_id}: backed up to {backup}")

    run(f"su - amp -c 'ampinstmgr --StopInstance {instance_id}'")
    ok = edit_kvp(kvp_path, player, occupying)
    if not ok:
        log(f"{instance_id}: edit aborted, restarting with no changes")
        run(f"su - amp -c 'ampinstmgr --StartInstance {instance_id}'")
        return

    log(f"{instance_id}: rotated -- player={player}, occupying={occupying}")
    run("chown -R amp:amp /home/amp/.ampdata/")
    run(f"su - amp -c 'ampinstmgr --StartInstance {instance_id}'")


def main():
    for instance_id in INSTANCE_BASE:
        rotate_instance(instance_id)


if __name__ == "__main__":
    main()
