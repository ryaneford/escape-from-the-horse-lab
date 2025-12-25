# Escapists – Mission Header Parameters Reference (Community Guide)

> ⚠️ **DISCLAIMER**
>
> This document is an **unofficial, community-written reference** for the *Escapists* game mode
> in Arma Reforger.
>
> It is based on public documentation, observed behavior, and practical server administration
> experience.
>
> It is **not** authoritative, **not guaranteed accurate for all versions**, and **not endorsed**
> by Bohemia Interactive or the Escapists mod authors.
>
> Primary upstream reference:
> https://github.com/igorkis-scrts/A4-Escapists-Docs/wiki/Dedicated-Server-Info#mission-header-parameters

---

## Purpose of This README

This README exists to:

- Explain **what each mission header parameter does**
- Group parameters by **practical function**
- Highlight **which settings are safe to tune**
- Warn about settings that can destabilize gameplay or performance

It is intended for **dedicated server admins**, not mission makers.

---

## How Mission Headers Work in Escapists

Mission headers are **read once at scenario start**.

- Changes require a **server restart**
- Values do **not adapt dynamically**
- Poor combinations can cause runaway AI, empty worlds, or soft-locks

Always change values incrementally and test with real players.

---

## Core Mode & Factions

| Parameter | Description |
|---------|-------------|
| `m_bUseSetupMenu` | Enables or disables the in-game setup menu. Dedicated servers usually set this to `0`. |
| `m_sOccupyingFaction` | Faction controlling the island at mission start. |
| `m_sPlayerFaction` | Player faction assignment. |
| `m_sInsurgentFaction` | Primary hostile faction; strongly affects equipment and difficulty. |
| `m_sCivilianFaction` | Civilian faction used for ambient population. |

---

## AI & Combat Model

| Parameter | Description |
|---------|-------------|
| `m_eAiSkill` | Global AI skill level (0–100). Higher values increase accuracy and reaction speed. |
| `m_eHealthType` | Health model selection; higher values are more punishing and realistic. |

Increasing AI skill and spawn density at the same time can overwhelm players.

---

## Time & Weather

| Parameter | Description |
|---------|-------------|
| `m_sStartingWeather` | Initial weather preset. |
| `m_bRandomStartingTime` | Enables random mission start times. |
| `m_iStartHours` | Fixed start hour (24h clock) if random time is disabled. |
| `m_fTimeAccelerationDay` | Time multiplier during daytime. |
| `m_fTimeAccelerationNight` | Time multiplier during nighttime. |

---

## Chaos & Difficulty Control

These parameters define how intense Escapists feels moment-to-moment.

| Parameter | Description |
|---------|-------------|
| `m_fDisabledLocationsRatio` | Percentage of locations disabled; higher values concentrate enemies. |
| `m_fCharacterSpawnChance` | Probability of enemy AI spawning at eligible locations. |
| `m_fVehicleSpawnChance` | Chance of vehicles spawning, driving escalation and reinforcement. |
| `m_iAmbientEventsFrequency` | Frequency of ambient events such as patrols or skirmishes. |

These are the safest difficulty levers.

---

## World Density & Insurgency

| Parameter | Description |
|---------|-------------|
| `m_fStaticLocationChance` | Likelihood of static locations being active. |
| `m_iCivilianPresence` | Civilian population density. |
| `m_iInsurgency` | Overall insurgent activity level. |

---

## Loot & Environment Interaction

| Parameter | Description |
|---------|-------------|
| `m_fItemSpawnChance` | Loot spawn probability in the world. |
| `m_fMapItemChance` | Chance for items to appear on the map. |
| `m_fCarAlarmChance` | Chance of vehicle alarms triggering and attracting enemies. |

---

## Player Experience & Rules

| Parameter | Description |
|---------|-------------|
| `m_eStartType` | Player spawn behavior at mission start. |
| `m_bUseWithstand` | Enables down-but-not-out mechanics. |
| `m_bUseSpectator` | Enables spectator mode after death. |
| `m_bNotHideLocationMarkers` | Controls visibility of map location markers. |
| `m_bSilentSupports` | Suppresses support notifications when enabled. |

---

## Server Lifecycle

| Parameter | Description |
|---------|-------------|
| `m_iEmptyServerRestartTimeout` | Time in seconds before the server restarts when empty. |

---

## Tuning Guidance

- Change one category at a time
- Prefer adjusting Chaos & Difficulty Control first
- Avoid modifying AI skill unless spawn rates are stable
- Restart the server after every change

---

## Final Notes

Escapists difficulty comes from threat concentration, not raw numbers.

If your server feels:
- Empty → lower disabled locations
- Overwhelming → reduce ambient events first
- Unstable → check AI limits and persistence settings

---

## License

This document is community-generated and provided for educational use.
