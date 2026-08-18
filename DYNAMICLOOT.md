# Enabling DynamicLoot

How to get the [DynamicLoot](https://github.com/wyqydsyq/DynamicLoot) addon
actually spawning loot on a HorseLab instance, and what its settings mean.
Verified live on `EscapetheVanillaLab01` (a vanilla Combat Ops / Conflict
instance, mission `26_CombatOpsEveron.conf` — **not** an Escapists server)
on 2026-08-18.

## What it does

Reads loot items from faction EntityCatalogs and weights rarity by an
inverse of each item's arsenal supply cost (cheap items common, expensive
items rare), automatically picking up modded gear too. Ships as both a
standalone loot spawner and a framework other mods can build on.

## The gotcha: it's a no-op until you add a second mod

The base `DynamicLoot` addon (modId `66B2F0B008DC590F`) registers its
`DL_LootSystem` into every game mode automatically — its `addon.gproj`
carries a `SystemModuleSettings` merge into `Configs/Systems/
BaseGameModeSystems.conf`, which `SCR_BaseGameMode` (and therefore every
game mode, not just Conflict) loads. So wiring is automatic; you don't need
to touch the mission file.

But per upstream's own README, **loot spawning is disabled by default** so
the addon can double as a dependency-only library for other mods. Confirmed
this by inspecting the packed addon directly (`strings` on `data.pak`
turns up readable config text for Reforger's `.conf` format) — the
addon's own default `DL_LootSystem.conf` merge does not set
`enableLootSpawning` at all, so it's off. Live symptom: the addon loads
fine, zero crashes, but a full 25-minute play session produced zero
`DL_LootContainer`/`DL_LootSpawn` log lines in `script.log`.

The fix is a second, separately-subscribed addon called
**`Escapists-DynamicLoot`** (modId `66FC3E70881A5CD8`, despite the name —
it's a generic `DL_LootSystem` config override, not tied to the Escapists
gamemode). It depends on `DynamicLoot` and re-overrides the same
`BaseGameModeSystems.conf` merge with:

```
DL_LootSystem {
  enableLootSpawning 1
  maxLootItemsPerContainer 8
  ammoMultiplier 6
  attachmentMultiplier 0.8
  rareItemTypesMultiplier 0.6
}
```

Confirmed via the same `strings`-on-`data.pak` technique against a copy of
this addon already in use on `Test01`/`Escapists201`/`eascape0101`.

**Load order matters**: `Escapists-DynamicLoot` must load *after*
`DynamicLoot` so its override wins the merge (see `mod-goal` note in the
horselab-hub — "Mod must be added LAST in load order on both servers" was
written for a different mod but the same Enfusion merge-order mechanism
applies here). Append it to the end of the `mods` list, not the middle.

## Applying it to an instance

Same `GenericModule.kvp` surgery as `escapistsplus-modlist-sync.py` (see
[SETUP.md § Critical AMP/KVP rules](SETUP.md#1-critical-ampkvp-rules--read-this-before-touching-any-config)
— stop the instance first, back up the KVP, keep `App.AppSettings=...` on
one physical line with literal `\n` escapes, `chown -R amp:amp` after
editing, restart, then verify):

1. Make sure `DynamicLoot` (`66B2F0B008DC590F`) is already in the instance's
   mod list.
2. Append `{ "modId": "66FC3E70881A5CD8", "name": "Escapists-DynamicLoot" }`
   as the **last** entry in `App.AppSettings`'s `mods` field inside
   `GenericModule.kvp`.
3. `ampinstmgr -r <instance>` (or stop/edit/start per the KVP rules above
   if you want the safer stop-first ordering).
4. Verify: `AReforgerMaster/addons/Escapists-DynamicLoot_66FC3E70881A5CD8/`
   exists, the regenerated `Configs/serverconfig.json` lists both mods with
   `Escapists-DynamicLoot` last, and the newest `console.log` shows no
   addon/mod errors.
5. Loot containers are trigger-spawned (`DL_LootContainerTrigger`) near
   player proximity, not at mission start — `script.log` won't show
   `DL_LootContainer`/`DL_LootSpawn` lines until someone actually walks
   near a spawn point in-game. Confirm loot is present by playtesting, not
   just by log-watching.

## Tuning

To change the numbers above (`maxLootItemsPerContainer`, `ammoMultiplier`,
`attachmentMultiplier`, `rareItemTypesMultiplier`) beyond what
`Escapists-DynamicLoot` ships with, you'd need Arma Reforger Tools
(Workbench) to build your own systems-config override addon per upstream's
README — there's no headless/text way to edit a packed `.conf` file's
values in place. Riding on the existing `Escapists-DynamicLoot` override is
the path of least resistance unless those specific values need to change.
