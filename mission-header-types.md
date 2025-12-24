# 🎯 Escapists PvE Mission Header Tuning Guide

This document is intended for **server admins** tuning the *Escapists* PvE game mode on Arma Reforger dedicated servers.

It explains **how to scale chaos and difficulty safely**, based on live server testing, without causing AI runaway or performance instability.

---

## Baseline Configuration (Current)

These are the relevant baseline mission header values currently in use:

```json
"m_fDisabledLocationsRatio": 0.22,
"m_fStaticLocationChance": 0.65,

"m_iAmbientEventsFrequency": 30,

"m_fItemSpawnChance": 0.55,
"m_fCharacterSpawnChance": 0.50,
"m_fMapItemChance": 0.45,

"m_fCarAlarmChance": 0.55,
"m_fVehicleSpawnChance": 0.55
```

**Observed behavior**
- Stable and predictable
- Low failure rate
- Can feel tame for experienced Escapists players
- Suitable for learning or very casual groups

---

## Parameters That Actually Control Chaos

Only a few mission header values meaningfully affect how dangerous Escapists feels:

| Parameter | Effect |
|--------|-------|
| `m_fDisabledLocationsRatio` | Concentrates threats (most impactful) |
| `m_fCharacterSpawnChance` | Frequency of enemy contact |
| `m_fVehicleSpawnChance` | Escalation and reinforcement potential |
| `m_iAmbientEventsFrequency` | Background pressure and unpredictability |

> Escapists chaos comes from **less empty space**, not raw spawn spam.

---

## Comparison: Baseline vs Chaos Steps

| Parameter | Baseline | Step 1 – Hotter | Step 2 – Oppressive | Step 3 – Brutal |
|--------|---------:|----------------:|--------------------:|----------------:|
| `m_fCharacterSpawnChance` | 0.50 | 0.68 | 0.75 | 0.82 |
| `m_fVehicleSpawnChance` | 0.55 | 0.65 | 0.70 | 0.75 |
| `m_fDisabledLocationsRatio` | 0.22 | 0.30 | 0.40 | 0.50 |
| `m_iAmbientEventsFrequency` | 30 | 90 | 110 | 130 |
| `m_fItemSpawnChance` | 0.55 | 0.55 | 0.55 | 0.55 |
| `m_fMapItemChance` | 0.45 | 0.45 | 0.45 | 0.45 |
| `m_fStaticLocationChance` | 0.65 | 0.65 | 0.65 | 0.65 |
| `m_fCarAlarmChance` | 0.55 | 0.55 | 0.55 | 0.55 |

Only the four chaos-driver values change between steps.

---

## Step Presets (Drop-In Overrides)

Replace only these values in your existing mission header.

### Step 1 — Noticeably Hotter (Recommended First)

```json
"m_fCharacterSpawnChance": 0.68,
"m_fVehicleSpawnChance": 0.65,
"m_fDisabledLocationsRatio": 0.30,
"m_iAmbientEventsFrequency": 90
```

**Feel**
- More frequent engagements
- Fewer safe routes
- Still forgiving for casual players

---

### Step 2 — Oppressive Escapists

```json
"m_fCharacterSpawnChance": 0.75,
"m_fVehicleSpawnChance": 0.70,
"m_fDisabledLocationsRatio": 0.40,
"m_iAmbientEventsFrequency": 110
```

**Feel**
- Constant pressure
- Retreats often trigger new fights
- Team coordination required

---

### Step 3 — Brutal / Survival Mode

```json
"m_fCharacterSpawnChance": 0.82,
"m_fVehicleSpawnChance": 0.75,
"m_fDisabledLocationsRatio": 0.50,
"m_iAmbientEventsFrequency": 130
```

**Feel**
- Very few safe areas
- Continuous threat density
- Escape often fails

---

## Time-of-Day Recommendation

For servers that want **strict daytime gameplay** (no NVGs):

```json
"m_bRandomStartingTime": 0,
"m_iStartHours": 10
```

Leaving random start time enabled can still result in early/late low-light starts.

---

## Recommended Admin Workflow

1. Start with **Step 1**
2. Run several sessions
3. Collect player feedback
4. Move to Step 2 only if players still feel comfortable

Avoid jumping directly to Step 3 unless requested.

---

## Key Takeaway

> Escapists difficulty is controlled by **threat concentration**, not raw spawn counts.

If AI limits, cleanup systems, and replication are already tuned, these changes are **safe, reversible, and scalable**.
