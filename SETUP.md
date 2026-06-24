# Setup Guide

Rebuilding the HorseLab Arma Reforger Escapists setup from scratch (or
recovering after a reinstall). Follow in order.

## 0. Prerequisites

- Debian host with AMP (CubeCoders) installed, `ampinstmgr` available to root.
- Two Arma Reforger dedicated server instances created in AMP. This guide
  assumes instance IDs `eascape0101` (Server 1) and `Escapists201` (Server 2)
  — substitute your own instance IDs throughout (they're hardcoded in
  `INSTANCE_BASE` near the top of each script).
- Reforger build **1.7.0.54 or later**. Older builds have a stack-overflow
  bug in nested config overrides that crashes several mods used here
  (Escapists Plus's dependency closure in particular). Check your build via
  AMP's update button or `steamapps/appmanifest_1874900.acf`'s `buildid`.
- Root access to `/home/amp/.ampdata/instances/<id>/GenericModule.kvp` for
  each instance.

## 1. Critical AMP/KVP rules — read this before touching any config

These are not optional. Breaking them silently wipes the instance's admin
list, password, and mod list back to factory defaults on next start, with
no visible error — it still boots, just empty.

1. **Never edit a `GenericModule.kvp` while the instance is running.** Stop
   it first via `ampinstmgr --StopInstance <id>`.
2. **`App.AppSettings=...` must stay one physical line.** The `mods` and
   `missionHeader` fields are JSON-in-a-string blobs using the literal
   two-character escape `\n` (backslash + n) for line breaks *inside the
   string*. If a real newline byte ends up in that span, AMP silently
   regenerates the whole `App.AppSettings` block to defaults on next start.
   Every script in `scripts/` asserts no real newline made it into a write
   before saving, for exactly this reason — keep that pattern if you write
   more tooling against this file.
3. **After any edit as root, `chown -R amp:amp /home/amp/.ampdata/`.**
   AMP runs as the `amp` user and can't write its own config otherwise.
4. **Always back up the KVP before editing** (`cp -p`) and **verify by
   re-reading the file after the restart completes** — don't trust "it
   booted" alone, since a wiped-to-defaults instance boots fine too.

## 2. Mod list

`config/mod-list-s1.txt` and `config/mod-list-s2.txt` are the current
known-good lists (60 and 59 mods respectively, captured live 2026-06-24) —
identical except each server's own active-map submod. Install via AMP's web
UI mod list field, or use `scripts/escapistsplus-modlist-sync.py`:

```bash
# mods_file is a JSON array of [modId, name] pairs, e.g.:
#   [["644D0C978D83F91E", "Escapists Plus"], ...]
python3 scripts/escapistsplus-modlist-sync.py <instance_id> mods_file.json
```

This script backs up, stops the instance, rewrites only the `mods` field
(leaving everything else untouched), chowns, restarts, and re-verifies the
mod count survived the restart.

**Don't add Rayzis Optics or anything from the Prontos family
(Prontos Hub/Attachments/SA80/AR15s/Legacy Brit Kit/Fix for Warfare) or
YobananaboY Weapon Pack alongside Escapists Plus** unless you've confirmed
on a test instance first — this combination caused an EntityCatalog
infinite-recursion crash historically. It may be fixed by 1.7.0.54's
stack-overflow fix, but hasn't been re-verified as of this writing.

## 3. missionHeader baseline

The `missionHeader` field (also inside `GenericModule.kvp`'s
`App.AppSettings`) controls per-round Escapists settings. Baseline values in
use on both servers:

| Field | Value | Why |
|---|---|---|
| `m_iStartHours` | `20` | Round always starts at 8 PM (dusk). Integer hours only, no minutes — 20 is the closest to "20:00–20:15." |
| `m_bRandomStartingTime` | `0` | Disabled, so the fixed start hour above actually applies. |
| `m_fTimeAccelerationDay` / `m_fTimeAccelerationNight` | `2.22` (both) | 60÷27 ≈ 2.22 — an in-game hour passes in ~27 real minutes, day and night equally. |
| `m_iCivilianPresence` | `0` | Disabled for CPU/performance reasons (civilian AI was a measurable resource cost). Replaces the older `m_sCivilianFaction` field after the AMP 2.8 / Reforger update. |
| `m_sInsurgentFaction` | `FIA` | Only supported non-RANDOM value besides `RANDOM` itself. |

`m_sPlayerFaction`/`m_sOccupyingFaction` are managed by the faction rotation
script (next section) — don't set these manually if the timer is active, it
will overwrite them daily.

## 4. Faction rotation

Player and occupying faction are rotated daily so rounds don't always feel
like the same matchup. The full *why* behind every faction key is in the
docstring of `scripts/escapists-faction-rotate.py` — read it before
touching `COMPATIBILITY`.

**The short version:** the in-game manual faction setup menu (set
`m_bUseSetupMenu: 1` temporarily on a test instance to access it) is the
only reliable source of truth for which faction keys exist and which
pairings the game considers valid. Mod filenames and engine-level
`FactionKey` constants found via `strings`-scanning `.pak` files are *not*
reliable — this was learned the hard way (`RHS_ION` looked plausible from
static analysis but turned out to be wired into nothing; the real "Soviet
Army (Naval Infantry)" key is `USSR_NI`). Even the menu's own allowed-pairs
list isn't fully sufficient: it permits `NATO` vs `RHS_USAF` even though
both visually present as the same US-aligned side in practice — that
required a manual override on top of the menu data after we hit it live.

**To extend the faction pool:** put a test instance in manual setup mode,
try every relevant pairing in-game, watch for a same-side feel, and update
`COMPATIBILITY` in the script to match — don't guess from mod content
alone.

Install:
```bash
cp scripts/escapists-faction-rotate.py /root/
cp systemd/escapists-faction-rotate.{service,timer} /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now escapists-faction-rotate.timer
python3 /root/escapists-faction-rotate.py --dry-run   # sanity check first
```

Runs daily at 05:00 UTC, restarts both instances to apply (missionHeader
changes only take effect on restart).

## 5. Map vote system

Each server runs an independent single-map weekly vote, resolved by
`scripts/single-map-vote.py`. It depends on the
[horselab-status](https://github.com/ryaneford/horselab-status) site for
the actual vote collection (a `votes.db` SQLite table the public site
writes to) plus two JSON files it reads/writes:

- `map_catalog.json` — the full list of available maps (id, display name,
  mission `.conf` path, and optional required mod). See
  `config/map_catalog.example.json` for the current 17-map catalog.
- `map_polls.json` — per-server poll state (current map, cycle number,
  zero-vote fallback mode). See `config/map_polls.example.json`.

Both files live at `/opt/horselab-status/data/` in the current deployment —
adjust `DATA_DIR` near the top of the script if horselab-status lives
elsewhere on a fresh install.

Install:
```bash
cp scripts/single-map-vote.py /root/
cp systemd/single-map-vote.{service,timer} /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now single-map-vote.timer
python3 /root/single-map-vote.py --dry-run   # sanity check first
```

Runs weekly, Monday 07:00 UTC (intentionally before the faction rotation's
daily 05:00 UTC slot the next morning won't collide, and before any other
daily restart routine you run).

`zero_vote_mode` per server in `map_polls.json`:
- `"keep"` — no votes that week, leave the current map alone.
- `"simulate"` — fabricate a plausible tally and pick a winner anyway, so
  rotation keeps moving even with no real votes.

The map-mod insert uses an anchor string (`MOD_INSERT_ANCHOR` in the
script, currently the "Server Admin Tools" mod entry) to know where to
splice a new map mod into the `mods` list — make sure whatever mod you use
as the anchor is present in every instance's mod list.

## 6. Verifying everything after a fresh install

1. `systemctl list-timers escapists-faction-rotate.timer single-map-vote.timer` — confirm both are enabled with sane next-run times.
2. `python3 /root/escapists-faction-rotate.py --dry-run` and `python3 /root/single-map-vote.py --dry-run` — confirm no errors, sane proposed values.
3. Start each instance, check AMP's console output / RCON-auth status for crash signatures (EntityCatalog NULL-pointer or stack-overflow errors are the historical failure mode here).
4. Log in and confirm: round starts at dusk, faction pairing isn't the same side twice, map matches `current_map` in `map_polls.json`.
