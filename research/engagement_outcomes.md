# Realistic Air-to-Air Engagement Outcomes

## Question
What are all the realistic outcomes of an air-to-air engagement beyond the binary kill/destroyed model? What data exists for missile Pk, damage rates, disengagement, countermeasures, attrition, and electronic warfare effects?

## Summary
Real air combat engagements have far more outcomes than "one side destroyed." Historical data shows that missile misses are the most common outcome of any shot, damage-without-destruction occurs 4-14x more often than kills, and many engagements end with disengagement rather than a kill. Modern BVR missile Pk is 0.4-0.6 in real combat (far below manufacturer claims of 0.8-0.9), and countermeasures, maneuvering, and EW further reduce effectiveness. Confidence: MEDIUM - based on publicly available combat data, RAND models, NATO reports, and CSBA analysis.

## Findings

---

### 1. Complete Taxonomy of Engagement Outcomes

An air-to-air engagement can end in any of these outcomes (for EACH side independently):

| Outcome | Description | Frequency Estimate |
|---|---|---|
| **Hard Kill** | Aircraft destroyed (fireball, structural failure, crew killed) | Rare per shot; ~2-5% of combat sorties |
| **Soft Kill / Mission Kill** | Aircraft still flying but combat-ineffective (radar destroyed, weapons jammed, critical system damaged) | More common than hard kill |
| **Damage - RTB** | Aircraft damaged, pilot breaks off and returns to base for repair | 4-14x more common than destruction |
| **Forced Abort** | Aircraft must abort mission due to threat, but takes no damage (e.g., forced to jettison weapons, burn fuel evading) | Very common |
| **Missile Evasion** | Missile fired but evaded via maneuver, countermeasures, or both | Most common outcome of any missile shot |
| **Mutual Disengagement** | Both sides break off, neither achieves objective | Common in BVR; ~30-50% of encounters |
| **Deterrence / Denial** | Enemy turns back without shots fired; defending side achieves "air denial" | Common; many intercepts end here |
| **Fuel-Forced RTB** | One or both sides must return to base due to fuel state (bingo fuel) | Frequent in extended CAP/intercept missions |
| **No Engagement** | Sortie launched, no contact with enemy | The MOST common outcome by far |

**Critical insight**: The vast majority of combat sorties result in NO engagement at all. In the Gulf War, of 100,000+ coalition sorties, fewer than 100 resulted in air-to-air engagements.

---

### 2. Missile Pk (Probability of Kill) Data

#### Historical Missile Pk by Type and Conflict

| Missile | Conflict | Shots | Kills | Pk | Notes |
|---|---|---|---|---|---|
| AIM-7 Sparrow | Vietnam (early) | ~600 | ~56 | 0.08-0.10 | Poor reliability, ROE constraints |
| AIM-9B Sidewinder | Vietnam (early) | ~175 | ~28 | 0.16 | Rear-aspect only |
| AIM-9E Sidewinder | Vietnam (1972) | 30 | 3 | 0.10 | Against maneuvering MiGs |
| AIM-7E Sparrow | Vietnam (1972) | 149 | 20 | 0.13 | LINEBACKER I period |
| AIM-9L Sidewinder | Falklands (1982) | 27 | 19 | 0.70 | All-aspect; non-maneuvering targets |
| AIM-7M Sparrow | Gulf War (1991) | ~71 | ~23 | 0.32 | Improved reliability |
| AIM-120 AMRAAM | Various (1990s-2000s) | 13 | 6 | 0.46 | Operational BVR Pk |
| R-73 / R-27 | Various | Limited data | Limited | 0.3-0.5 est. | Russian missiles, less open data |

**Sources**: CSBA "Trends in Air-to-Air Combat"; DoD historical missile performance data; USAF combat records.

#### Pk by Range Zone

| Range Zone | Estimated Pk (Modern AAM) | Why |
|---|---|---|
| Maximum range (Rmax) | 0.10-0.25 | Missile at energy limits, target has max evasion time |
| Long BVR (70-80% Rmax) | 0.25-0.40 | Target can maneuver, countermeasures effective |
| Medium BVR (optimal) | 0.40-0.60 | Best kinematic zone, missile has energy for endgame maneuver |
| Short range / WVR | 0.50-0.80 | Minimal evasion time, high closure geometry |
| No-escape zone (NEZ) | 0.70-0.90 | Target cannot outmaneuver missile kinematically |

**Key modeling insight**: The "advertised" Pk of 0.8-0.9 applies only in the no-escape zone against a non-maneuvering target with no countermeasures. Real-world BVR Pk is 0.3-0.5 for modern missiles.

#### Salvo Doctrine (Shots Per Engagement)

Standard doctrine is **shoot-shoot-look** (fire 2, assess, fire again if needed):
- Typical BVR engagement: 2-4 missiles fired per target
- Missiles fired per kill (historical average): 2-8 depending on era and missile type
- Vietnam era: ~7-10 shots per kill
- Gulf War era: ~2-3 shots per kill
- Modern doctrine assumes 2 missiles per target for adequate engagement Pk

**Engagement Pk with salvo**:
- Single shot Pk = 0.5 --> 2-missile salvo Pk = 1 - (0.5)^2 = 0.75
- Single shot Pk = 0.4 --> 2-missile salvo Pk = 1 - (0.6)^2 = 0.64
- Single shot Pk = 0.3 --> 3-missile salvo Pk = 1 - (0.7)^3 = 0.66

---

### 3. Damage Without Destruction

#### Damage-to-Kill Ratios (Historical)

| Aircraft/Conflict | Damaged | Destroyed | Ratio |
|---|---|---|---|
| A-10 (Gulf War) | 70 | 5-6 | ~12-14:1 |
| F-4 Phantom (Vietnam) | ~400 est. | ~100 | ~4:1 |
| General (Vietnam era) | -- | -- | ~4:1 average |
| All coalition (Gulf War) | 97 incidents | 39 combat losses | ~2.5:1 |

**Key finding**: For every aircraft destroyed in combat, 4 to 14 more are damaged but survive. The simulation should model damage as the MORE LIKELY outcome of a hit.

#### Types of Survivable Battle Damage

Aircraft can sustain and survive:
- **Engine damage**: Single-engine loss on twin-engine aircraft; partial thrust loss
- **Hydraulic system damage**: Reduced or manual flight controls
- **Fuel system hits**: Fuel leaks (self-sealing tanks limit but don't eliminate leaks)
- **Structural damage**: Holes in wings/fuselage up to several square feet (aircraft-dependent)
- **Avionics damage**: Loss of radar, EW suite, communications
- **Weapons system damage**: Loss of weapons pylons, fire control, weapon release mechanisms
- **Flight surface damage**: Partial loss of stabilizer, rudder, aileron

#### Effects of Battle Damage on Combat Capability

| Damage Level | Speed Impact | Weapons | Mission Capable? | Repair Time |
|---|---|---|---|---|
| Light (holes, minor systems) | 0-5% reduction | Fully capable | Yes, may continue | Hours (same-day turnaround) |
| Moderate (engine/system hits) | 10-30% reduction | Partially degraded | Mission kill - RTB | 1-3 days |
| Heavy (structural/multi-system) | 30-50%+ reduction | Severely degraded | Survival flight only - RTB | Days to weeks |
| Catastrophic (but survivable) | Barely flyable | None | Emergency RTB only | Weeks to depot-level |

#### Battle Damage Repair Times

- **Light damage (field repair)**: 2-8 hours, same maintenance crew
- **Moderate damage (ABDR team)**: 12-72 hours, specialized ABDR team required
- **Heavy damage (depot)**: 1-4 weeks, may require evacuation to rear area
- **Normal turnaround (undamaged)**: 2-4 hours (refuel, rearm, inspect) for fighter aircraft
- **Israeli Air Force achieved**: 7-10 minute turnaround for hot refuel/rearm (combat surge)

---

### 4. Disengagement and Breaking Off

#### Reasons Pilots Disengage

1. **Bingo fuel**: Pre-calculated fuel state requiring immediate RTB. Non-negotiable.
2. **Winchester**: Out of air-to-air weapons. Must RTB or request tanker/rearm.
3. **Defensive situation**: Energy disadvantage, outnumbered, being targeted. "Bugout" to survive.
4. **Threat warning**: RWR indicates missile launch or radar lock from unknown source.
5. **Mission priority**: Primary mission (e.g., strike escort) takes precedence over kill.
6. **GCI/AWACS directive**: Ground control orders disengagement.
7. **ROE constraints**: Rules of engagement prevent continued prosecution.
8. **Damage sustained**: Aircraft damaged, capability reduced, pilot elects to preserve aircraft.

#### Tactical Modes (from combat modeling research)

| Mode | Condition | Behavior |
|---|---|---|
| **Aggressive** | Energy/positional advantage, weapons available | Press attack, close for kill |
| **Neutral** | Roughly equal situation | Maneuver for advantage, look for opportunity |
| **Defensive** | Energy/positional disadvantage | Break turn, dispense countermeasures, try to reverse |
| **Evasive** | Under immediate missile threat | Maximum defensive maneuver, countermeasures |
| **Disengagement** | Fuel/weapons/damage threshold met | Break contact, extend, RTB |

#### Air Denial vs Air Superiority

A defender "wins" by achieving **air denial** -- forcing the attacker to:
- Abort the strike mission (even without shooting anything down)
- Jettison weapons to maneuver defensively
- Burn fuel in evasive maneuvers, reducing effective range
- Disengage due to unexpected resistance

This is a critical modeling insight: **successful defense does not require kills**. Forcing mission abort is a valid outcome.

---

### 5. Force-on-Force Engagement Dynamics

#### Lanchester's Laws in Air Combat

**Lanchester's Linear Law** (guerrilla/WVR): Attrition proportional to force ratio. A 2:1 advantage gives roughly 2:1 kill advantage.

**Lanchester's Square Law** (aimed fire/BVR): Combat power proportional to SQUARE of numbers. A 2:1 numerical advantage gives roughly 4:1 combat power advantage. This is because each unit can concentrate fire.

**Practical implication for simulation**: In BVR combat, numerical superiority matters enormously. A 4-ship flight vs a 2-ship flight has roughly 4x the combat power, not 2x.

#### Exchange Ratios (Historical)

| Conflict | US/Coalition : Enemy | Context |
|---|---|---|
| Korean War (F-86 vs MiG-15) | 1.8:1 to 5:1 | Revised downward from initial 10:1 claims |
| Vietnam (overall) | ~2.5:1 | US: 137 kills / 64 losses (USAF) |
| Arab-Israeli Wars (1967-82) | 20:1 to 80:1 | Israeli technological/training advantage |
| Falklands (1982) | 23:1 (Argentine losses) | Sea Harrier + AIM-9L advantage |
| Gulf War (1991) | 33:1 | Coalition air superiority dominant |
| Iran-Iraq War (1980-88) | ~3:1 (Iran advantage) | ~1000 engagements total |

#### Percentage of Sorties Resulting in Engagement

| Conflict | Total Sorties | Air-to-Air Engagements | % |
|---|---|---|---|
| Gulf War | 100,000+ | ~60-80 air-to-air events | <0.1% |
| Vietnam (USAF) | ~400,000 | ~400 engagements | ~0.1% |
| Typical modern campaign | Thousands | Tens | 0.1-1% |

**Modeling insight**: Most sorties will not result in air-to-air combat. The simulation should model sortie generation, patrol coverage, and interception probability rather than assuming every flight results in combat.

---

### 6. Electronic Warfare Effects

#### EW Impact on Engagement Outcomes

| EW Capability | Effect on Combat | Survival Multiplier |
|---|---|---|
| **RWR (Radar Warning Receiver)** | Detects enemy radar lock; triggers evasive action | 1.5-2x survival increase |
| **Noise jamming** | Degrades enemy radar range/accuracy | Reduces enemy detection range 30-60% |
| **Deceptive jamming** | Creates false targets, breaks lock | Can reduce missile Pk by 30-50% |
| **DRFM (Digital RF Memory)** | Creates precise false returns | Can completely defeat older radar seekers |
| **Towed decoy** | Diverts radar-guided missiles to expendable target | Estimated 50-80% effectiveness vs semi-active missiles |
| **IRCM (Infrared CM)** | Directed energy defeats IR seekers | Reduces IR missile Pk significantly |

#### Soft Kill vs Hard Kill

- **Hard kill**: Physical destruction of the aircraft
- **Soft kill**: Rendering the aircraft combat-ineffective through non-kinetic means:
  - Blinding radar through jamming (aircraft cannot detect or target enemies)
  - Burning through/damaging avionics via directed energy
  - Denying sensor data through electronic attack
  - Forcing pilot to focus on EW response rather than mission

#### Countermeasure Effectiveness

| Countermeasure | vs. Old Missiles | vs. Modern Missiles |
|---|---|---|
| **Chaff** (radar) | HIGH (effective against pulse-Doppler, conical scan) | LOW (modern monopulse/AESA seekers reject chaff via Doppler discrimination) |
| **Flares** (IR) | HIGH (early IR seekers easily fooled) | LOW-MEDIUM (imaging IR seekers use scene matching, spectral discrimination) |
| **Maneuver + chaff/flares** | VERY HIGH | MEDIUM (combination still significantly degrades Pk) |
| **ECM jamming** | HIGH | MEDIUM (modern seekers have ECCM, home-on-jam modes) |
| **Towed decoy** | N/A (not yet deployed) | MEDIUM-HIGH (effective against semi-active and some active seekers) |
| **Combined (maneuver + CM + ECM)** | VERY HIGH | MEDIUM-HIGH (best achievable defense) |

**Modeling recommendation**: Against modern missiles, individual countermeasures reduce Pk by 15-30%. Combined defensive response (maneuver + expendables + ECM) can reduce effective Pk by 40-60%.

---

### 7. Sortie Attrition Rates

#### Per-Sortie Loss Rates by Conflict

| Conflict | Aircraft/Side | Per-Sortie Loss Rate | Context |
|---|---|---|---|
| Vietnam (USAF, all causes) | F-105 | ~0.4% | 382 of 833 lost over years of combat |
| Vietnam (USAF, all causes) | All types | ~0.1-0.2% | Across all sortie types |
| Gulf War (Coalition) | All types | ~0.04% (1 in 2,500) | 39 combat losses / 100,000+ sorties |
| Gulf War (USAF only) | All types | ~0.048% | 14 losses / 29,300 sorties |
| Falklands (Argentine) | All types | ~1-2% | ~100 combat losses / ~500 attack sorties |
| Russia-Ukraine (Russia) | All types | Estimated 0.1-0.3% | Based on ~84-130 losses and estimated sortie counts |
| WWII (Luftwaffe, 1944) | All types | ~2-4% per mission | Unsustainable; led to collapse |
| WWII (USAAF bombers) | B-17/B-24 | ~2-4% per mission | Required 25 missions for tour completion |

#### Combat Ineffectiveness Thresholds

| Loss Rate (per sortie) | Effect on Air Force |
|---|---|
| <0.05% (1 in 2,000) | Sustainable indefinitely (Gulf War coalition level) |
| 0.1-0.5% (1 in 200-1000) | Sustainable for weeks-months; requires replacement pipeline |
| 0.5-1% (1 in 100-200) | Significant strain; squadron-level attrition visible in days |
| 1-2% (1 in 50-100) | Unsustainable; air force becomes combat-ineffective in weeks |
| 2-5% (1 in 20-50) | Crisis; combat capability collapses rapidly (WWII Luftwaffe levels) |
| >5% | Catastrophic; force destroyed in days |

**Historical threshold**: An air force typically becomes "combat ineffective" when cumulative losses reach 20-30% of initial strength without adequate replacement. At 2% per-sortie loss rate with 2 sorties/day, a squadron of 20 aircraft loses ~1 aircraft/day and becomes ineffective in 2-3 weeks.

#### Ukraine Conflict Data (2022-2026)

- Russia has lost 10%+ of pre-war combat aircraft inventory (~84-130 confirmed to combat)
- Ukraine has lost 100+ fixed-wing aircraft (35 MiG-29, 19 Su-27, 20 Su-24, 22 Su-25, 4 F-16, 1 Mirage 2000)
- Russian VKS losing 30-60 airframes/year from combat + accident + accelerated wear
- Daily sortie rates dropped substantially from initial ~300/day to much lower sustained levels
- Both sides primarily lose aircraft to ground-based air defense, not air-to-air combat

---

## Simulation Modeling Recommendations

Based on this research, the simulation should replace the binary kill/destroyed model with:

### Proposed Engagement Resolution Model

```
1. DETECTION PHASE
   - Does the interceptor detect the target? (affected by EW, radar, GCI)
   - Does the target detect the interceptor? (RWR, AWACS support)
   - If target detects threat early: may abort/disengage before shots fired

2. ENGAGEMENT DECISION
   - Fuel state check (bingo = forced RTB)
   - Weapons state check (winchester = forced RTB)
   - Tactical situation assessment (outnumbered? energy state?)
   - ROE check
   - Decision: engage, disengage, or deter

3. WEAPONS EMPLOYMENT
   - Range zone determines base Pk
   - Salvo size (typically 2 missiles)
   - Countermeasure effectiveness reduces Pk
   - EW effects reduce Pk
   - Target maneuver reduces Pk

4. OUTCOME RESOLUTION (per missile)
   Roll against adjusted Pk:
   - Miss (most likely): No effect
   - Hit: Roll damage severity:
     - 20-30%: Hard kill (destroyed)
     - 30-40%: Heavy damage (RTB, days to repair)
     - 20-30%: Moderate damage (mission kill, RTB, hours-days repair)
     - 10-20%: Light damage (may continue or RTB, hours repair)

5. POST-ENGAGEMENT
   - Surviving aircraft: fuel/weapons state check
   - Damaged aircraft: reduced performance for RTB
   - Both sides assess: continue, disengage, or RTB
   - Aircraft returning damaged: repair time before next sortie
```

### Key Parameters for the Simulation

| Parameter | Suggested Default | Range | Source Confidence |
|---|---|---|---|
| Base Pk (BVR, optimal range) | 0.45 | 0.30-0.60 | MEDIUM |
| Base Pk (BVR, max range) | 0.15 | 0.10-0.25 | MEDIUM |
| Base Pk (WVR) | 0.65 | 0.50-0.80 | MEDIUM |
| Missiles per engagement | 2 | 1-4 | HIGH |
| CM effectiveness (vs modern AAM) | -0.15 Pk | -0.10 to -0.30 | LOW |
| EW effectiveness (if equipped) | -0.20 Pk | -0.10 to -0.30 | LOW |
| Maneuver effectiveness | -0.10 Pk | -0.05 to -0.20 | LOW |
| Hit -> Hard Kill probability | 0.25 | 0.15-0.35 | MEDIUM |
| Hit -> Mission Kill probability | 0.35 | 0.25-0.45 | MEDIUM |
| Hit -> Damage (flyable) probability | 0.30 | 0.20-0.40 | MEDIUM |
| Hit -> Light damage probability | 0.10 | 0.05-0.20 | LOW |
| Sorties resulting in engagement | 0.005 | 0.001-0.02 | MEDIUM |
| Light damage repair time | 4 hours | 2-8 hours | MEDIUM |
| Moderate damage repair time | 24 hours | 12-72 hours | MEDIUM |
| Heavy damage repair time | 120 hours | 72-336 hours | MEDIUM |

---

## Sources

1. [CSBA - Trends in Air-to-Air Combat: Implications for Future Air Superiority](https://csbaonline.org/uploads/documents/Air-to-Air-Report-.pdf) -- Comprehensive analysis of historical BVR/WVR Pk data, missile performance trends, and future air combat implications
2. [RAND - Air Combat Model Engagement and Attrition Processes (N-3566)](https://www.rand.org/pubs/notes/N3566.html) -- High-level design for theater-level air combat attrition modeling with qualitative factors
3. [Coalition Fixed-Wing Combat Aircraft Attrition in Desert Storm](https://www.rjlee.org/air/ds-aaloss/) -- Detailed breakdown of Desert Storm losses by aircraft type and cause
4. [Post-World War II Air-to-Air Combat Losses (Wikipedia)](https://en.wikipedia.org/wiki/Post%E2%80%93World_War_II_air-to-air_combat_losses) -- Comprehensive list of air-to-air losses across all post-WWII conflicts
5. [PBS Frontline - Air Force Performance in Operation Desert Storm](https://www.pbs.org/wgbh/pages/frontline/gulf/appendix/whitepaper.html) -- USAF Desert Storm sortie and loss statistics
6. [AIM-120 AMRAAM (Wikipedia)](https://en.wikipedia.org/wiki/AIM-120_AMRAAM) -- Operational Pk data and combat history
7. [NATO RTO-EN-AVT-156: Epidemiology of Battle-Damaged Fixed-Wing Aircraft](https://apps.dtic.mil/sti/tr/pdf/ADA571693.pdf) -- Damage-to-kill ratios, repair categories, survivability data
8. [NATO RTO-EN-AVT-156: Design of Repair of Battle-Damaged Fixed-Wing Aircraft](https://apps.dtic.mil/sti/pdfs/ADA571702.pdf) -- Repair time categories, ABDR procedures
9. [Air & Space Forces Magazine - Aircraft Battle Damage Repair](https://www.airandspaceforces.com/air-force-aircraft-battle-damage-repair/) -- Modern ABDR teams and repair capabilities
10. [Lanchester's Laws (Wikipedia)](https://en.wikipedia.org/wiki/Lanchester's_laws) -- Square law and linear law for force-on-force modeling
11. [Air-to-Air Combat Modeling Using Lanchester Equations (DTIC)](https://apps.dtic.mil/sti/tr/pdf/ADA546639.pdf) -- Application of Lanchester equations to air combat
12. [RAND - The Russian Air Force Is Hollowing Itself Out](https://www.rand.org/pubs/commentary/2024/03/the-russian-air-force-is-hollowing-itself-out-air-defenses.html) -- Russian VKS attrition data from Ukraine conflict
13. [RAND - The Uncounted Losses to Russia's Air Force](https://www.rand.org/pubs/commentary/2023/08/the-uncounted-losses-to-russias-air-force.html) -- Imputed losses from accelerated wear
14. [Aerospace Global News - Four Years of War: Counting Russian and Ukrainian Aircraft Losses](https://aerospaceglobalnews.com/news/how-many-aircraft-losses-russia-ukraine/) -- Aircraft loss counts by type for both sides
15. [2951 CLSS - A-10 Gulf War Battle Damage](https://www.2951clss-gulfwar.com/about-gulf-war-a10s.html) -- Detailed A-10 damage/loss statistics
16. [HistoryNet - The Vietnam Air War's Great Kill-Ratio Debate](https://www.historynet.com/great-kill-ratio-debate/) -- Vietnam-era missile Pk and kill ratio analysis
17. [Basic Fighter Maneuvers (Wikipedia)](https://en.wikipedia.org/wiki/Basic_fighter_maneuvers) -- Tactical maneuvering, energy management, disengagement doctrine
18. [Chaff Countermeasure (Wikipedia)](https://en.wikipedia.org/wiki/Chaff_(countermeasure)) -- Chaff effectiveness against different radar types
19. [Flare Countermeasure (Wikipedia)](https://en.wikipedia.org/wiki/Flare_(countermeasure)) -- Flare effectiveness against different IR seekers
20. [Radar Jamming and Deception (Wikipedia)](https://en.wikipedia.org/wiki/Radar_jamming_and_deception) -- EW techniques and their effects on combat

## Methodology
Research conducted using web search across military publications, RAND Corporation reports, NATO RTO documents, DTIC archives, CSBA studies, and historical combat data compilations. Cross-referenced multiple sources for key data points (missile Pk, attrition rates, damage ratios). Where specific data was unavailable (particularly for modern systems where data is classified), ranges were estimated based on historical trends and publicly available analysis.

Search queries used:
- "air-to-air missile probability of kill Pk modern BVR AIM-120 AMRAAM real combat data"
- "RAND air combat attrition model sortie loss rate Gulf War Vietnam historical data"
- "fighter aircraft battle damage repair combat damage survivability mission kill"
- "air combat disengagement bugout decision fuel state pilot engagement break off doctrine"
- "electronic warfare jamming effect air combat soft kill radar warning receiver"
- "Lanchester laws air combat numerical superiority exchange ratio"
- "shoot-look-shoot doctrine missiles fired per engagement"
- "chaff flares countermeasures effectiveness against air-to-air missiles"
- "Ukraine war air combat losses fighter aircraft attrition rate"

## Confidence Assessment
- **Overall confidence**: MEDIUM
- **High confidence areas**: Historical missile Pk data (well-documented); Gulf War attrition rates (extensively studied); damage-to-kill ratios (NATO studies); Lanchester's laws (mathematical basis well-established)
- **Medium confidence areas**: Countermeasure effectiveness (specific values classified); modern missile Pk (limited open-source data on AIM-120D/PL-15/Meteor); EW multipliers (highly situation-dependent)
- **Low confidence areas**: Exact damage severity distributions (limited public data on what percentage of hits cause each damage level); modern Russian missile performance; specific repair times by damage category
- **Limitations**: Much real performance data is classified. Modern conflict data (Ukraine) is incomplete and contested. Pk values are highly scenario-dependent (range, altitude, aspect, ECM environment, target type). Historical data may not reflect current technology.
- **Recommendations**: Run sensitivity analysis across parameter ranges. Allow these parameters to be configurable per scenario. Consider implementing the engagement as a multi-step probabilistic process rather than a single die roll.

## Applied In
- `backend/src/domain/entities/aircraft.py` -- Will inform damage model and engagement outcomes
- `backend/src/domain/services/` -- Will inform engagement resolution service
- `Development/DOMAIN.md` -- Should be updated with engagement outcome model
- `research/combat_probabilities.md` -- Supersedes/extends the existing combat probability estimates

## Last Updated
2026-04-17
