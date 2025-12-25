# Escapists – Mission Header Parameters (Values + Effects)

> ⚠️ **DISCLAIMER (Read First)**
>
> This is a **community reference** for Escapists mission header parameters in Arma Reforger dedicated servers.
> It summarizes **supported values** and the **practical effect** of each value as described in the Escapists docs.
>
> **Upstream reference (source of truth):**
> https://github-wiki-see.page/m/igorkis-scrts/A4-Escapists-Docs/wiki/Dedicated-Server-Info (Mission Header parameters section)

---

## Notes for Dedicated Servers

- **Booleans and enums must be numeric** (e.g. `1/0`, `0/2/4`, etc.). Strings like `false` or enum names won’t be recognized.
- Mission header values are **read at scenario start** → changes require a **server restart**.
- Any parameter you omit uses Escapists **default value**.

---

## Parameters (Supported Values + What They Do)

### `m_bUseSetupMenu`
**Description:** Handover start menu to the first logged-in admin; bypasses other mission header settings while enabled.

| Value | Effect |
|---:|---|
| 1 | Server waits for an admin to `#login` and start the run via setup menu. Mission header settings are effectively bypassed (except this flag). |
| 0 | Server auto-starts Escapists when the first player joins, using mission header + defaults. |

**Default:** 1

---

### `m_sOccupyingFaction`
**Description:** Main antagonist faction key.

Supported values:
- `US` – Occupiers are US forces
- `USSR` – Occupiers are USSR forces
- `RANDOM` – Randomized per run

**Default:** `US`

**Notes:** Can be expanded by compatibility packs (e.g., mods adding `UK`).

---

### `m_sPlayerFaction`
**Description:** Player faction key.

Supported values:
- `US` – Players are US
- `USSR` – Players are USSR
- `RANDOM` – Randomized per run

**Default:** `USSR`

**Notes:** Should not be the same as the occupying faction; should not use `CIV`/`FIA` keys.

---

### `m_sInsurgentFaction`
**Description:** Insurgent faction key.

Supported values:
- `FIA` – FIA insurgents
- `RANDOM` – Randomized

**Default:** `FIA`

**Notes:** Vanilla Escapists supports FIA only; other insurgent factions require dependency mods.

---

### `m_sCivilianFaction`
**Description:** Civilian faction key.

Supported values:
- `CIV` – Vanilla civilians
- `RANDOM` – Randomized

**Default:** `CIV`

**Notes:** Vanilla Escapists supports CIV only; more requires dependency mods.

---

### `m_eAiSkill`
**Description:** AI skill level (primarily accuracy; tactical behavior impact is limited).

| Value | Label | Effect |
|---:|---|---|
| 10 | newbie | Lowest enemy accuracy/reaction. |
| 20 | rookie | Easier firefights; forgiving for casual groups. |
| 50 | regular | Baseline; fair but dangerous. |
| 70 | veteran | Significantly higher hit rate; punishes exposure. |
| 80 | expert | Very lethal; small mistakes become deaths. |

**Default:** 50

---

### `m_eHealthType`
**Description:** Player survivability (increases “tankiness” via blood pool, hit zones, resilience, regen scales, etc.).

| Value | Effect |
|---:|---|
| 0 | Default survivability. |
| 2 | Slightly increased survivability (~small buff). |
| 4 | Moderately increased survivability (bigger buff). |

**Default:** 0

---

### `m_sStartingWeather`
**Description:** Starting weather preset.

Supported values:
- `Clear` – Clear skies
- `Cloudy` – Light cloud cover
- `Overcast` – Heavy cloud cover
- `Rainy` – Rain conditions
- `Random` – Randomized per run (docs examples sometimes use `RANDOM` casing)

**Default:** `Clear`

---

### `m_iStartHours`
**Description:** Starting time of day (hours).

Supported values: **0 to 24**  
**Default:** 8

**Practical tips:**
- Daylight-focused servers often use **9–12**.
- If `m_bRandomStartingTime` is enabled, this value is bypassed.

---

### `m_fTimeAccelerationDay`
**Description:** Daytime time acceleration multiplier.

Supported range: **0.1 to 12.0** (2 decimal places)  
**Default:** 1.0

**Effect:** Higher values make daytime pass faster (shorter real-time days).

---

### `m_fTimeAccelerationNight`
**Description:** Nighttime time acceleration multiplier.

Supported range: **0.1 to 12.0** (2 decimal places)  
**Default:** 1.0

**Effect:** Higher values make nighttime pass faster (shorter real-time nights).

---

### `m_fDisabledLocationsRatio`
**Description:** Ratio of random locations disabled (removed) before the run starts.

Supported range: **0.1 to 1.0** (2 decimal places)  
**Default:** 0.3

**Effect model:**
- Higher value → more locations removed → threats concentrate into fewer areas → runs feel more oppressive.
- Some locations (cities, start areas, patrol locations) are ignored by the randomizer.

---

### `m_iCivilianPresence`
**Description:** Whether civilians can be present in cities.

| Value | Effect |
|---:|---|
| 0 | No civilians present. |
| 1 | Civilians present. |

**Default:** 1

---

### `m_iInsurgency`
**Description:** Insurgent faction presence and relations.

| Value | Meaning | Practical Effect |
|---:|---|---|
| 0 | Disabled | No insurgency layer. |
| 1 | HostileToOccupants | Insurgents fight occupiers; can create AI-vs-AI encounters. |
| 2 | HostileToEscapees | Insurgents primarily fight players. |
| 3 | HostileToEveryone | Insurgents fight occupiers and players. |
| 4 | UseDefaultFactionSettings | Uses faction config “Friendly Faction Ids” (recommended default). |

**Default:** 4

---

### `m_iAmbientEventsFrequency`
**Description:** Ambient event tick interval (seconds per “tick”).

Supported range: **-1 to 240**  
**Default:** 45

**Effect model:**
- This is an **interval** for “coin flips.”
- Higher value → ticks happen less often → ambient events are rarer.
- Lower value → ticks more frequent → more ambient activity.
- Completing “Defend the Radio” can increase event frequency (lower the tick value) about 2× unless already very small.

---

### `m_fStaticLocationChance`
**Description:** Chance static locations are present (separate randomizer from dynamic locations).

Supported range: **0.1 to 1.0** (2 decimal places)  
**Default:** 0.35

**Examples:** Radio stations, hospitals-in-buildings, control towers, etc.

---

### `m_fItemSpawnChance`
**Description:** Chance items spawn on storages and horizontal surfaces.

Supported range: **0.1 to 1.0** (2 decimal places)  
**Default:** 0.45

---

### `m_fCharacterSpawnChance`
**Description:** Chance characters spawn on character spawn points.

Supported range: **0.1 to 1.0** (2 decimal places)  
**Default:** 0.35

**Effect:** Higher value increases encounter frequency, but is still bounded by AI limits and scenario systems.

---

### `m_fMapItemChance`
**Description:** Chance map items are present in enemy character loadouts.

Supported range: **0.1 to 1.0** (2 decimal places)  
**Default:** 0.3

**Effect:** Higher values increase availability of map intel from enemies.

---

### `m_fCarAlarmChance`
**Description:** Chance ambient cars have armed alarms.

Supported range: **0.1 to 1.0** (2 decimal places)  
**Default:** 0.4

**Effect:** Alarms can attract patrols or light vehicles to investigate (adds “chaos spikes”).

---

### `m_fVehicleSpawnChance`
**Description:** Chance vehicles spawn on vehicle spawn points (location spawners).

Supported range: **0.1 to 1.0** (2 decimal places)  
**Default:** 0.35

**Notes:** Applies to vehicle spawn points **on locations**; ambient vehicle spawns use a modified vanilla system.

---

### `m_eStartType`
**Description:** Starting player conditions.

| Value | Meaning | Effect |
|---:|---|---|
| 0 | Random | Start type randomized. |
| 2 | Hideout | Start at a hideout start. |
| 4 | Prison | Start from a prison scenario. |
| 8 | Helicrash | Start at a helicopter crash. |

**Default:** 0

---

### `m_bRandomStartingTime`
**Description:** Randomize start time (bypasses `m_iStartHours`).

| Value | Effect |
|---:|---|
| 1 | Start time randomized. |
| 0 | Start time fixed (uses `m_iStartHours`). |

**Default:** 0

---

### `m_bUseWithstand`
**Description:** Allow self-use of epinephrine while unconscious (“withstand”).

| Value | Effect |
|---:|---|
| 1 | Players can use epinephrine on themselves while unconscious (if they have it). |
| 0 | No self-withstand; recovery requires treatment or teammate epinephrine. |

**Default:** 0

---

### `m_bNotHideLocationMarkers`
**Description:** Show location types immediately instead of “?” icons.

| Value | Effect |
|---:|---|
| 1 | Location types visible from the start. |
| 0 | Location types hidden behind question mark icons until discovered. |

**Default:** 0

---

### `m_bUseSpectator`
**Description:** Enter spectator mode while unconscious.

| Value | Effect |
|---:|---|
| 1 | Spectator mode is used while unconscious (unless withstand is enabled and epinephrine is available). |
| 0 | No spectator mode behavior. |

**Default:** 1

---

### `m_bSilentSupports`
**Description:** Suppress notifications for upcoming enemy supports.

| Value | Effect |
|---:|---|
| 1 | Support notifications suppressed. |
| 0 | Support notifications shown. |

**Default:** 0

---

### `m_iEmptyServerRestartTimeout`
**Description:** Grace period (seconds) to rejoin an in-progress session before forced restart (dedicated only).

Supported range: **1 to 10000**  
**Default:** 900

**Effect:** When server becomes empty, the timer starts. If no one rejoins before it expires, the server restarts.

---

## Practical “Tuning” Advice (Safe Order)

1. Adjust **`m_fDisabledLocationsRatio`** (concentrates danger)
2. Adjust **`m_iAmbientEventsFrequency`** (controls event tick rate)
3. Adjust **`m_fCharacterSpawnChance`** (encounter frequency)
4. Adjust **`m_fVehicleSpawnChance`** (escalation)

Avoid changing AI skill and spawn rates at the same time until you have a stable baseline.

---

## Attribution

Supported values and baseline descriptions are sourced from the Escapists docs mirror:
https://github-wiki-see.page/m/igorkis-scrts/A4-Escapists-Docs/wiki/Dedicated-Server-Info
