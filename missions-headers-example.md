# Escapists PvE – Mission Header Example (Reference Only)

> ⚠️ **IMPORTANT – THIS IS ONLY AN EXAMPLE**
>
> This repository **does not provide a recommended or optimal configuration**.
>
> The contents here exist solely as a **documented example** to help server admins understand
> how Escapists mission header parameters are structured and how difficulty tuning works.
>
> **Do NOT blindly copy values into production servers.**
> Always test and tune for your own community.

---

## What This Repository Is

This repository contains:

- A **well-organized example** `missionHeader`
- Plain-English explanations of **each parameter**
- Guidance on **safe vs risky tuning**
- A reference layout that makes Escapists difficulty easier to reason about

---

## What This Repository Is NOT

This repository is **not**:

- An official Escapists configuration
- A guaranteed balanced setup
- A one-size-fits-all solution
- Endorsed by mod authors

Think of this as **documentation**, not a preset.

---

## Example Mission Header (Annotated)

> 📝 This example includes comments for clarity and is **NOT JSON-valid**.
>
> Remove comments before using any values in a real `serverconfig.json`.

```jsonc
"missionHeader": {

  "m_bUseSetupMenu": 0,

  "m_sOccupyingFaction": "RANDOM",
  "m_sPlayerFaction": "RANDOM",
  "m_sInsurgentFaction": "FIA",
  "m_sCivilianFaction": "CIV",

  "m_eAiSkill": 50,
  "m_eHealthType": 2,

  "m_sStartingWeather": "Random",
  "m_bRandomStartingTime": 0,
  "m_iStartHours": 10,

  "m_fTimeAccelerationDay": 1.75,
  "m_fTimeAccelerationNight": 2.75,

  "m_fDisabledLocationsRatio": 0.22,
  "m_fCharacterSpawnChance": 0.50,
  "m_fVehicleSpawnChance": 0.55,
  "m_iAmbientEventsFrequency": 30,

  "m_fStaticLocationChance": 0.65,
  "m_iCivilianPresence": 1,
  "m_iInsurgency": 2,

  "m_fItemSpawnChance": 0.55,
  "m_fMapItemChance": 0.45,
  "m_fCarAlarmChance": 0.55,

  "m_eStartType": 0,
  "m_bUseWithstand": 1,
  "m_bUseSpectator": 1,
  "m_bNotHideLocationMarkers": 0,
  "m_bSilentSupports": 0,

  "m_iEmptyServerRestartTimeout": 1800
}
```

---

## Chaos Control (Most Important Concept)

These four values are responsible for most of the perceived difficulty:

| Setting | What It Controls |
|------|------------------|
| `m_fDisabledLocationsRatio` | Forces players into fewer safe routes |
| `m_fCharacterSpawnChance` | Frequency of enemy contact |
| `m_fVehicleSpawnChance` | Escalation and reinforcement |
| `m_iAmbientEventsFrequency` | Background pressure and unpredictability |

---

## Admin Guidance

- Adjust **only one block at a time**
- Prefer changing Chaos Control values first
- Restart the server after mission header changes
- Gather player feedback before escalating difficulty

---

## Final Reminder

This repository exists to **explain**, not prescribe.

Your server. Your players. Your responsibility.
