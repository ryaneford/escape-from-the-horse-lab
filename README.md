# escape-from-the-horse-lab

Setup, settings, and operational automation for the HorseLab community's two
Arma Reforger Escapists servers ("Escape from the Horse Lab!" #1 and #2),
running under AMP (CubeCoders) on a single Debian host.

This repo exists so the whole setup can be rebuilt from scratch on a fresh
server without re-deriving everything by hand. See **[SETUP.md](SETUP.md)**
for the full step-by-step guide.

Also covers mod-specific notes that apply to any HorseLab instance on the
same host, even non-Escapists ones — see **[DYNAMICLOOT.md](DYNAMICLOOT.md)**
for getting the [DynamicLoot](https://github.com/wyqydsyq/DynamicLoot) addon
actually spawning loot (it's a no-op without a second companion mod).

## What's in here

- `scripts/` — the three automation scripts that run via systemd timers:
  - `escapists-faction-rotate.py` — daily player/occupying faction rotation, collision-checked against the in-game setup menu's own compatibility rules.
  - `single-map-vote.py` — weekly per-server map vote resolution (reads votes from a SQLite DB maintained by the [horselab-status](https://github.com/ryaneford/horselab-status) site, swaps the active map mod + mission file).
  - `escapistsplus-modlist-sync.py` — rewrites an instance's full mod list safely (used for one-shot bulk mod-list changes).
- `systemd/` — the `.service`/`.timer` unit pairs for the two timers above.
- `config/` — the current known-good mod list for each server, plus example map-catalog/poll-state JSON for the map vote system.

## Requirements

- Arma Reforger dedicated server **1.7.0.54 or later**. Several mods that
  used to crash the server together (Escapists Plus + YobananaboY Weapon
  Pack in particular) work correctly as of 1.7.0.54, which fixed a
  stack-overflow bug in "complex hierarchies/overrides of config files" —
  exactly the bug class behind those crashes. Confirmed live and crash-free
  on both servers as of 2026-06-24.
- AMP 2.8+ managing the instances (`ampinstmgr` CLI available to root).
- Both instances' data under `/home/amp/.ampdata/instances/<instance-id>/`.

See SETUP.md for the full walkthrough.
