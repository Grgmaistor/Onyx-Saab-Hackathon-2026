# Aircraft Performance Data for Simulation Parameters

## Question
What are realistic performance parameters (speed, combat radius, fuel capacity, fuel burn rate, weapons load, turnaround/rearm/maintenance times) for the four aircraft categories in the Boreal Passage simulation, based on real-world military aircraft?

## Summary
Comprehensive performance data gathered for Combat Plane (based on JAS 39 Gripen, F-16, F-35A), Bomber (based on Su-34, F-15E, B-1B), UAV (based on MQ-9 Reaper, Bayraktar TB2, Bayraktar Akinci), and Drone Swarm (based on Switchblade 600, Shahed-136). Data cross-referenced from manufacturer specs, military fact sheets, Wikipedia, and defense publications. Confidence: MEDIUM -- most individual aircraft specs are well-documented, but composite simulation values require judgment calls on weighting and simplification.

## Findings

---

### 1. Combat Plane Category

#### JAS 39 Gripen (C/E variants)

| Parameter | Value | Source |
|---|---|---|
| Max speed | Mach 2.0 (2,130 km/h at altitude) | [Wikipedia](https://en.wikipedia.org/wiki/Saab_JAS_39_Gripen) |
| Supercruise (Gripen E) | Mach 1.2 (1,470 km/h) with A2A load | [Wikipedia](https://en.wikipedia.org/wiki/Saab_JAS_39_Gripen) |
| Cruise speed (subsonic) | ~900-950 km/h (est. Mach 0.8-0.85) | Derived from typical fighter cruise |
| Combat radius (internal fuel, A2A) | ~800 km (Gripen C) | [Key Aero forum / Saab data](https://www.key.aero/forum/modern-military-aviation/101768-modern-fighters-combat-radius) |
| Combat radius (with external tanks) | 1,300 km (Gripen E, 6x AAMs + tanks) | [Wikipedia](https://en.wikipedia.org/wiki/Saab_JAS_39_Gripen) |
| Internal fuel capacity | 3,000 kg (Gripen C); ~4,200 kg (Gripen E, +40%) | [Wikipedia](https://en.wikipedia.org/wiki/Saab_JAS_39_Gripen), [Saab](https://www.saab.com/products/gripen-e-series) |
| Fuel burn rate (cruise) | ~1,100 kg/h | [Defense Issues](https://defenseissues.wordpress.com/2016/10/01/dassault-rafale-vs-saab-gripen/) |
| Hardpoints | 8 (Gripen C), 10 (Gripen E) | [Wikipedia](https://en.wikipedia.org/wiki/Saab_JAS_39_Gripen) |
| Typical A2A loadout | 4-6 AAMs (2x IRIS-T/AIM-9 + 2-4x AMRAAM/Meteor) + gun | [MilitaryFactory](https://www.militaryfactory.com/aircraft/detail.php?aircraft_id=67) |
| Turnaround time (A2A, refuel+rearm) | <10 minutes (1 tech + 5 conscripts) | [Wikipedia](https://en.wikipedia.org/wiki/Saab_JAS_39_Gripen), [Saab](https://www.saab.com/newsroom/stories/2020/august/gripen-designed-for-dispersed-air-basing-system) |
| Turnaround time (A2G, full load) | ~20 minutes | [Saab](https://www.saab.com/newsroom/stories/2020/august/gripen-designed-for-dispersed-air-basing-system) |
| Maintenance hours per flight hour | ~10 MMH/FH (Gripen C); reportedly lower for E | [Saab](https://www.saab.com/newsroom/stories/2020/november/how-gripen-can-be-cost-effective) |

#### F-16 Fighting Falcon (Block 50/52)

| Parameter | Value | Source |
|---|---|---|
| Max speed | Mach 2.0+ (2,120 km/h) | [USAF Fact Sheet](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104505/f-16-fighting-falcon/) |
| Cruise speed | ~850-900 km/h (Mach 0.8) | Standard fighter cruise profile |
| Combat radius (internal fuel, A2G hi-lo-hi) | ~550 km (with 6x 500lb bombs) | [Wikipedia](https://en.wikipedia.org/wiki/General_Dynamics_F-16_Fighting_Falcon) |
| Combat radius (A2A, internal fuel) | ~600-700 km (estimated lighter A2A load) | Derived from range data |
| Internal fuel capacity | 3,249 kg (7,162 lb) | [F-16.net](https://www.f-16.net/f-16_versions_article9.html) |
| Fuel burn rate (cruise) | ~1,360 kg/h (~3,000 lb/h) | [F-16.net forum](https://www.f-16.net/forum/viewtopic.php?t=1102), [flyajetfighter.com](https://www.flyajetfighter.com/fighter-aircraft-fuel-consumption/) |
| Typical A2A loadout | 6x AIM-9 Sidewinder or mix of AIM-9 + AIM-120 AMRAAM + gun | [Wikipedia](https://en.wikipedia.org/wiki/General_Dynamics_F-16_Fighting_Falcon) |
| Turnaround time (ICT) | 45 minutes max | [DVIDSHUB](https://www.dvidshub.net/news/479043/f-16-integrated-combat-turns-enable-ace-northern-strike-24-2) |
| Mission capable rate | 88% (highest of US fighters) | [USAF Fact Sheet](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104505/f-16-fighting-falcon/) |

#### F-35A Lightning II

| Parameter | Value | Source |
|---|---|---|
| Max speed | Mach 1.6 (1,960 km/h) | [USAF Fact Sheet](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/478441/f-35a-lightning-ii/) |
| Cruise speed | ~850-900 km/h (Mach 0.8); Mach 1.2 dash for 240 km | [Wikipedia](https://en.wikipedia.org/wiki/Lockheed_Martin_F-35_Lightning_II) |
| Combat radius | 1,093 km (590 nmi) on internal fuel | [USAF](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/478441/f-35a-lightning-ii/), [Wikipedia](https://en.wikipedia.org/wiki/Lockheed_Martin_F-35_Lightning_II) |
| Internal fuel capacity | 8,278 kg (18,250 lb) | [Wikipedia](https://en.wikipedia.org/wiki/Lockheed_Martin_F-35_Lightning_II) |
| Fuel burn rate (cruise, Mach 0.75 @ 40kft) | ~1,800 kg/h (~4,000 lb/h) | [F-16.net forum USAF presentation data](https://www.f-16.net/forum/viewtopic.php?f=22&t=53517) |
| Internal weapons (stealth config) | 4x AIM-120 AMRAAM (2 per bay) | [Wikipedia](https://en.wikipedia.org/wiki/Lockheed_Martin_F-35_Lightning_II) |
| Full weapons load (non-stealth) | Up to 10 stations, 22,000 lb total | [Wikipedia](https://en.wikipedia.org/wiki/Lockheed_Martin_F-35_Lightning_II) |
| Turnaround time (standard) | ~3 hours (current) | [Air & Space Forces Magazine](https://www.airandspaceforces.com/maintainers-hot-ict-f-35/) |
| Turnaround time (hot ICT goal) | 25-30 minutes (under development) | [Air & Space Forces Magazine](https://www.airandspaceforces.com/maintainers-hot-ict-f-35/) |
| Maintenance hours per flight hour | 5.2 MMH/FH | [Wikipedia](https://en.wikipedia.org/wiki/Lockheed_Martin_F-35_Lightning_II) |

#### Composite "Combat Plane" Simulation Values

Weighted toward the Gripen (since this is a SAAB project) but informed by all three:

| Parameter | Simulation Value | Rationale |
|---|---|---|
| **Cruise speed** | 950 km/h | Gripen supercruise ~1,470 km/h but normal cruise ~900; F-16/F-35 cruise ~850-900; 950 represents typical operational speed |
| **Combat radius** | 800 km | Gripen C internal fuel ~800 km; F-16 ~600 km; F-35 ~1,093 km; weighted toward Gripen |
| **Internal fuel capacity** | 3,400 kg | Gripen C ~3,000; Gripen E ~4,200; F-16 ~3,249; averaged toward Gripen E baseline |
| **Fuel burn rate** | ~1,200 kg/h | Gripen ~1,100; F-16 ~1,360; F-35 ~1,800; weighted toward Gripen |
| **Fuel burn rate per km** | ~1.26 kg/km | 1,200 kg/h / 950 km/h |
| **A2A weapons load** | 6 missiles | Gripen 4-6; F-16 up to 6; F-35 4 internal / 8+ total |
| **Refuel time** | 10 minutes | Gripen designed for <10 min turnaround |
| **Rearm time** | 15 minutes | Gripen A2A rearm included in 10 min; allow slightly more for full loadout |
| **Maintenance turnaround** | 30 minutes | Between-sortie inspection; Gripen optimized for rapid turnaround |

---

### 2. Bomber Category

#### Su-34 Fullback

| Parameter | Value | Source |
|---|---|---|
| Max speed | Mach 1.6 (1,900 km/h at altitude) | [Wikipedia](https://en.wikipedia.org/wiki/Sukhoi_Su-34) |
| Max speed (sea level) | Mach 1.0 (1,300 km/h) | [Airforce Technology](https://www.airforce-technology.com/projects/su34/) |
| Cruise speed | ~900-950 km/h (est. Mach 0.8) | Derived from typical fighter-bomber cruise |
| Combat radius | 1,100 km (standard); 1,500 km (with drop tanks) | [Wikipedia](https://en.wikipedia.org/wiki/Sukhoi_Su-34), [Army Recognition](https://www.armyrecognition.com/military-products/air/bomber/su-34-fullback-sukhoi) |
| Internal fuel capacity | 12,100 kg | [Wikipedia](https://en.wikipedia.org/wiki/Sukhoi_Su-34) |
| Ferry range | 4,000 km | [Wikipedia](https://en.wikipedia.org/wiki/Sukhoi_Su-34) |
| Fuel burn rate (cruise, estimated) | ~3,000 kg/h | Derived: 12,100 kg / ~4h endurance at combat load |
| Weapons load | 8,000 kg on 12 hardpoints + 30mm gun | [Wikipedia](https://en.wikipedia.org/wiki/Sukhoi_Su-34), [MilitaryFactory](https://www.militaryfactory.com/aircraft/detail.php?aircraft_id=697) |
| A2A self-defense | R-73 (AA-11) short-range + R-77 (AA-12) BVR | [Wikipedia](https://en.wikipedia.org/wiki/Sukhoi_Su-34) |

#### F-15E Strike Eagle

| Parameter | Value | Source |
|---|---|---|
| Max speed | Mach 2.5+ (>2,650 km/h) | [USAF Fact Sheet](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104499/f-15e-strike-eagle/) |
| Cruise speed | ~900 km/h | Standard subsonic cruise |
| Combat radius | ~1,270 km (790 mi) depending on loadout | [USAF Fact Sheet](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104499/f-15e-strike-eagle/) |
| Internal fuel capacity | 5,858 kg (12,915 lb); 10,100 kg with CFTs | [Wikipedia](https://en.wikipedia.org/wiki/McDonnell_Douglas_F-15E_Strike_Eagle) |
| Fuel burn rate (cruise) | ~2,727 kg/h (~900 gal/h clean) | [SimpleFlying](https://simpleflying.com/how-many-miles-per-gallon-f-15/) |
| Weapons load | 4x AIM-9 + 4x AIM-120 (A2A) + bombs/PGMs on 9 hardpoints | [Wikipedia](https://en.wikipedia.org/wiki/McDonnell_Douglas_F-15E_Strike_Eagle) |
| Range (with CFTs + ext tanks) | 4,445 km (2,762 mi) | [USAF Fact Sheet](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104499/f-15e-strike-eagle/) |

#### B-1B Lancer (Heavy Bomber Reference)

| Parameter | Value | Source |
|---|---|---|
| Max speed | Mach 1.25 (1,530 km/h) | [USAF Fact Sheet](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104500/b-1b-lancer/) |
| Speed at low altitude | Mach 0.92 (~1,130 km/h) | [Wikipedia](https://en.wikipedia.org/wiki/Rockwell_B-1_Lancer) |
| Combat radius | 5,556 km (3,000 nmi) without refueling | [USAF Fact Sheet](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104500/b-1b-lancer/) |
| Weapons load | 34,019 kg (75,000 lb) across 3 internal bays | [Wikipedia](https://en.wikipedia.org/wiki/Rockwell_B-1_Lancer) |
| Note | Too large for this simulation's "bomber" category -- serves as upper bound reference | -- |

#### Composite "Bomber" Simulation Values

Based primarily on Su-34 and F-15E as fighter-bomber archetypes:

| Parameter | Simulation Value | Rationale |
|---|---|---|
| **Cruise speed** | 750 km/h | Lower than combat plane due to heavier loadout; Su-34 and F-15E cruise ~900 but operationally slower when loaded |
| **Combat radius** | 1,100 km | Su-34 ~1,100; F-15E ~1,270; averaged |
| **Internal fuel capacity** | 9,000 kg | Su-34 ~12,100; F-15E ~5,858 (or ~10,100 with CFTs); compromise value |
| **Fuel burn rate** | ~2,800 kg/h | Su-34 ~3,000; F-15E ~2,727; averaged |
| **Fuel burn rate per km** | ~3.73 kg/km | 2,800 kg/h / 750 km/h |
| **A2G weapons load** | 8 munitions | Mix of PGMs, bombs; Su-34 up to 12 hardpoints, F-15E up to 9 |
| **A2A self-defense** | 2-4 missiles | Both carry short/medium range AAMs for self-defense |
| **Refuel time** | 30 minutes | Larger fuel tanks, more ground crew needed |
| **Rearm time** | 45 minutes | Complex ordnance loading; heavier munitions |
| **Maintenance turnaround** | 60 minutes | Heavier airframe, more systems to inspect |

---

### 3. UAV Category

#### MQ-9 Reaper

| Parameter | Value | Source |
|---|---|---|
| Max speed | 482 km/h (260 kts) | [USAF Fact Sheet](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104470/mq-9-reaper/) |
| Cruise speed (max endurance) | 278-315 km/h (150-170 kts) | [GA-ASI](https://www.ga-asi.com/remotely-piloted-aircraft/mq-9a) |
| Combat radius | ~1,850 km (1,150 mi) without external tanks | [Wikipedia](https://en.wikipedia.org/wiki/General_Atomics_MQ-9_Reaper) |
| Endurance | 27 hours (standard); 14 hours fully loaded; 42 hours with ext tanks + light load | [Wikipedia](https://en.wikipedia.org/wiki/General_Atomics_MQ-9_Reaper) |
| Fuel capacity | 1,769 kg (3,900 lb) | [Wikipedia](https://en.wikipedia.org/wiki/General_Atomics_MQ-9_Reaper) |
| Fuel burn rate (estimated) | ~65 kg/h | Derived: 1,769 kg / 27h endurance |
| Weapons load | 4x AGM-114 Hellfire + 2x GBU-12 (500lb) or AIM-9; ~1,361 kg external stores | [USAF Fact Sheet](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104470/mq-9-reaper/) |
| Max payload | 1,746 kg total | [GA-ASI](https://www.ga-asi.com/remotely-piloted-aircraft/mq-9a) |
| Ceiling | 15,240 m (50,000 ft) | [USAF Fact Sheet](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104470/mq-9-reaper/) |

#### Bayraktar TB2

| Parameter | Value | Source |
|---|---|---|
| Max speed | 220 km/h (120 kts) | [Wikipedia](https://en.wikipedia.org/wiki/Bayraktar_TB2) |
| Cruise speed | ~130 km/h | [MilitaryFactory](https://www.militaryfactory.com/aircraft/detail.php?aircraft_id=1679) |
| Operational range | 300 km (line of sight); 150 km (effective) | [Wikipedia](https://en.wikipedia.org/wiki/Bayraktar_TB2) |
| Endurance | 27 hours | [Wikipedia](https://en.wikipedia.org/wiki/Bayraktar_TB2) |
| Fuel capacity | 300 liters (~240 kg) | [Wikipedia](https://en.wikipedia.org/wiki/Bayraktar_TB2) |
| Fuel burn rate (estimated) | ~9 kg/h | Derived: 240 kg / 27h |
| Weapons load | Up to 150 kg; 4x MAM-L or MAM-C smart munitions | [Wikipedia](https://en.wikipedia.org/wiki/Bayraktar_TB2) |
| Ceiling | 8,230 m (27,000 ft) | [Wikipedia](https://en.wikipedia.org/wiki/Bayraktar_TB2) |

#### Bayraktar Akinci

| Parameter | Value | Source |
|---|---|---|
| Max speed | ~360 km/h (est.) | [Wikipedia](https://en.wikipedia.org/wiki/Baykar_Bayraktar_Ak%C4%B1nc%C4%B1) |
| Endurance | 20+ hours | [Wikipedia](https://en.wikipedia.org/wiki/Baykar_Bayraktar_Ak%C4%B1nc%C4%B1) |
| Payload | 1,350 kg | [Wikipedia](https://en.wikipedia.org/wiki/Baykar_Bayraktar_Ak%C4%B1nc%C4%B1) |
| MTOW | 5,500 kg | [Wikipedia](https://en.wikipedia.org/wiki/Baykar_Bayraktar_Ak%C4%B1nc%C4%B1) |
| Ceiling | 13,752 m (45,118 ft) | [Wikipedia](https://en.wikipedia.org/wiki/Baykar_Bayraktar_Ak%C4%B1nc%C4%B1) |
| Weapons | SOM cruise missiles (250 km range), PGMs, MAM series | [Wikipedia](https://en.wikipedia.org/wiki/Baykar_Bayraktar_Ak%C4%B1nc%C4%B1) |

#### Composite "UAV" Simulation Values

Based primarily on MQ-9 Reaper (most representative armed MALE UAV) with Akinci influence:

| Parameter | Simulation Value | Rationale |
|---|---|---|
| **Cruise speed** | 300 km/h | MQ-9 ~300 km/h cruise; Akinci ~300-360; TB2 much slower at 130 |
| **Combat radius** | 700 km | MQ-9 ~1,850 km but limited by comms; Akinci data-link limited; practical operational radius scaled for theater |
| **Fuel capacity** | 1,500 kg | MQ-9 ~1,769 kg; scaled slightly down for composite |
| **Fuel burn rate** | ~60 kg/h | MQ-9 ~65 kg/h; turboprop efficiency |
| **Fuel burn rate per km** | ~0.20 kg/km | 60 kg/h / 300 km/h |
| **Weapons load** | 4 munitions | MQ-9 carries 4x Hellfire + 2x bombs; simplified to 4 guided munitions |
| **Refuel time** | 30 minutes | Turboprop UAV; simpler than jet but still requires ground handling |
| **Rearm time** | 20 minutes | Smaller munitions, fewer hardpoints |
| **Maintenance turnaround** | 45 minutes | Less complex than manned fighters but still requires pre-flight checks |

---

### 4. Drone Swarm Category

#### Switchblade 600

| Parameter | Value | Source |
|---|---|---|
| Dash speed | 185 km/h (115 mph) | [ArmyRecognition](https://www.armyrecognition.com/military-products/army/unmanned-systems/unmanned-aerial-vehicles/switchblade-600-loitering-munition) |
| Range | 80 km total (40 km out + 40 min loiter) | [DefenseFeeds](https://defensefeeds.com/military-tech/army/army-uavs/switchblade-600/) |
| Endurance | 40+ minutes | [AeroVironment datasheet](https://www.avinc.com/images/uploads/product_docs/Switchblade600_Datasheet.pdf) |
| Warhead | Javelin-class ATGM warhead | [Wikipedia](https://en.wikipedia.org/wiki/AeroVironment_Switchblade) |
| Type | One-way attack / loitering munition | -- |

#### Shahed-136 (Geran-2)

| Parameter | Value | Source |
|---|---|---|
| Speed | 185 km/h (115 mph) | [Wikipedia](https://en.wikipedia.org/wiki/HESA_Shahed_136) |
| Range | 1,000-2,500 km (estimates vary) | [Wikipedia](https://en.wikipedia.org/wiki/HESA_Shahed_136), [drone-warfare.com](https://drone-warfare.com/research/shahed-136/) |
| Warhead | 30-50 kg (66-110 lb) | [Wikipedia](https://en.wikipedia.org/wiki/HESA_Shahed_136) |
| Type | One-way attack drone / kamikaze | -- |
| Swarm capability | Launched in salvos from multi-rail launchers | [Various](https://min.news/en/military/55826f15f6fb083852b74a8a3325c6fe.html) |
| Unit cost | ~$20,000-50,000 (estimated) | [drone-warfare.com](https://drone-warfare.com/research/shahed-136/) |

#### Composite "Drone Swarm" Simulation Values

A "swarm unit" in the simulation represents a coordinated group of small drones (10-20 individual units) operating as one entity:

| Parameter | Simulation Value | Rationale |
|---|---|---|
| **Cruise speed** | 180 km/h | Switchblade ~185; Shahed-136 ~185; small drone typical speed |
| **Combat radius** | 200 km | Switchblade ~40 km; Shahed up to 2,500 km but one-way; 200 km as recoverable swarm radius |
| **"Fuel" capacity (endurance proxy)** | 200 units | Represents energy budget of swarm; unitless for simulation |
| **Fuel burn rate** | 1.0 per km | Linear depletion model for simplicity |
| **Weapons load** | 15 munitions | Represents ~15 attack-capable drones per swarm unit |
| **Refuel/recharge time** | 60 minutes | Battery recharge or fuel replenishment for recoverable types |
| **Rearm time** | 30 minutes | Replace expended drone elements |
| **Maintenance turnaround** | 20 minutes | Simple systems, minimal inspection |

---

### 5. Supplementary Data

#### Squadron / Base Sizes

| Organization | Typical Size | Source |
|---|---|---|
| NATO fighter squadron | 12-24 aircraft | [Wikipedia - Squadron (aviation)](https://en.wikipedia.org/wiki/Squadron_(aviation)) |
| USAF fighter squadron | 18-24 aircraft | [AeroCorner](https://aerocorner.com/blog/how-many-planes-squadron/) |
| RAF Typhoon/F-35 squadron | 12-16 aircraft | [DefenseAdvancement](https://www.defenseadvancement.com/resources/raf-squadrons/) |
| Swedish Gripen division (flygdivision) | 12-16 aircraft | Typical Swedish Air Force unit |
| **Simulation recommendation** | 12-18 per base | Reasonable for single-base operations |

#### Radar Detection Ranges

| System Type | Detection Range (fighter-size target) | Source |
|---|---|---|
| Ground-based S-band (e.g., GM400) | 390-515 km | [Wikipedia - Ground Master 400](https://en.wikipedia.org/wiki/Ground_Master_400) |
| Ground-based VHF/UHF (counter-stealth) | ~300 km | [flyajetfighter.com](https://www.flyajetfighter.com/how-radars-detect-stealth-aircraft-today/) |
| AWACS (E-3 Sentry, high alt target) | 400-520 km | [Wikipedia - AEW&C](https://en.wikipedia.org/wiki/Airborne_early_warning_and_control) |
| AWACS (E-3, low alt target) | ~370 km (200 nmi) | [USAF Fact Sheet](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104504/e-3-sentry-awacs/) |
| Fighter AESA radar (APG-68 vs 1m2 RCS) | ~70 km (38 nmi) | [Wikipedia - AN/APG-68](https://en.wikipedia.org/wiki/AN/APG-68) |
| Fighter AESA radar (APG-81, est.) | 150-200 km (estimated) | Estimated from aperture size and power |
| **Simulation: ground radar** | 400 km | Conservative mid-range for ground-based radar |
| **Simulation: fighter radar** | 100-150 km | Depends on target RCS; simplified |

---

## Recommended Simulation Parameters (Final)

These are the values recommended for `_TYPE_DEFAULTS` in `backend/src/domain/entities/aircraft.py`:

### Combat Plane
```
speed_kmh = 950.0
fuel_capacity = 3400.0      # kg
fuel_burn_rate = 1.26        # kg per km traveled
combat_radius_km = 800       # informational, derived from fuel_capacity / fuel_burn_rate
refuel_time_minutes = 10.0
ammo_capacity = 6            # air-to-air missiles
rearm_time_minutes = 15.0
maintenance_time_minutes = 30.0
```

### Bomber
```
speed_kmh = 750.0
fuel_capacity = 9000.0      # kg
fuel_burn_rate = 3.73        # kg per km traveled
combat_radius_km = 1100      # informational
refuel_time_minutes = 30.0
ammo_capacity = 8            # strike munitions (bombs/missiles)
rearm_time_minutes = 45.0
maintenance_time_minutes = 60.0
```

### UAV
```
speed_kmh = 300.0
fuel_capacity = 1500.0      # kg
fuel_burn_rate = 0.20        # kg per km traveled
combat_radius_km = 700       # informational
refuel_time_minutes = 30.0
ammo_capacity = 4            # guided munitions
rearm_time_minutes = 20.0
maintenance_time_minutes = 45.0
```

### Drone Swarm
```
speed_kmh = 180.0
fuel_capacity = 200.0       # abstract energy units
fuel_burn_rate = 1.0         # units per km traveled
combat_radius_km = 200       # informational
refuel_time_minutes = 60.0
ammo_capacity = 15           # individual attack drones in swarm
rearm_time_minutes = 30.0
maintenance_time_minutes = 20.0
```

---

## Sources

1. [Saab JAS 39 Gripen - Wikipedia](https://en.wikipedia.org/wiki/Saab_JAS_39_Gripen) -- Primary specs for Gripen C/E variants including speed, fuel, hardpoints, turnaround time
2. [Saab - Gripen Dispersed Air Basing](https://www.saab.com/newsroom/stories/2020/august/gripen-designed-for-dispersed-air-basing-system) -- 10-minute turnaround with conscript crew
3. [Saab - Gripen Cost Effectiveness](https://www.saab.com/newsroom/stories/2020/november/how-gripen-can-be-cost-effective) -- Maintenance hours per flight hour
4. [F-16 Fighting Falcon - USAF Fact Sheet](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104505/f-16-fighting-falcon/) -- Official USAF specifications
5. [General Dynamics F-16 - Wikipedia](https://en.wikipedia.org/wiki/General_Dynamics_F-16_Fighting_Falcon) -- Combat radius, fuel capacity, weapons
6. [F-16.net - Block 50/52](https://www.f-16.net/f-16_versions_article9.html) -- Detailed internal fuel data
7. [DVIDSHUB - F-16 ICT](https://www.dvidshub.net/news/479043/f-16-integrated-combat-turns-enable-ace-northern-strike-24-2) -- 45-minute integrated combat turn
8. [F-35A Lightning II - USAF Fact Sheet](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/478441/f-35a-lightning-ii/) -- Official specifications
9. [Lockheed Martin F-35 - Wikipedia](https://en.wikipedia.org/wiki/Lockheed_Martin_F-35_Lightning_II) -- Fuel capacity, weapons, performance
10. [Air & Space Forces - F-35 Hot ICT](https://www.airandspaceforces.com/maintainers-hot-ict-f-35/) -- 3-hour standard turnaround, 25-min hot ICT goal
11. [Sukhoi Su-34 - Wikipedia](https://en.wikipedia.org/wiki/Sukhoi_Su-34) -- Fuel capacity, combat radius, weapons
12. [Su-34 - Airforce Technology](https://www.airforce-technology.com/projects/su34/) -- Speed, range data
13. [F-15E Strike Eagle - USAF Fact Sheet](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104499/f-15e-strike-eagle/) -- Combat radius, weapons, range
14. [McDonnell Douglas F-15E - Wikipedia](https://en.wikipedia.org/wiki/McDonnell_Douglas_F-15E_Strike_Eagle) -- Fuel capacity with CFTs
15. [B-1B Lancer - USAF Fact Sheet](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104500/b-1b-lancer/) -- Payload, range (upper bound reference)
16. [B-1B Lancer - Wikipedia](https://en.wikipedia.org/wiki/Rockwell_B-1_Lancer) -- Speed, weapons capacity
17. [MQ-9 Reaper - USAF Fact Sheet](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104470/mq-9-reaper/) -- Speed, ceiling, weapons
18. [General Atomics MQ-9 - Wikipedia](https://en.wikipedia.org/wiki/General_Atomics_MQ-9_Reaper) -- Endurance, fuel capacity, payload
19. [GA-ASI MQ-9A Product Page](https://www.ga-asi.com/remotely-piloted-aircraft/mq-9a) -- Cruise speed, payload capacity
20. [Bayraktar TB2 - Wikipedia](https://en.wikipedia.org/wiki/Bayraktar_TB2) -- Speed, endurance, fuel capacity, weapons
21. [Bayraktar Akinci - Wikipedia](https://en.wikipedia.org/wiki/Baykar_Bayraktar_Ak%C4%B1nc%C4%B1) -- Payload, endurance, ceiling
22. [Switchblade 600 - ArmyRecognition](https://www.armyrecognition.com/military-products/army/unmanned-systems/unmanned-aerial-vehicles/switchblade-600-loitering-munition) -- Speed, range, warhead
23. [AeroVironment Switchblade - Wikipedia](https://en.wikipedia.org/wiki/AeroVironment_Switchblade) -- Range, endurance
24. [HESA Shahed 136 - Wikipedia](https://en.wikipedia.org/wiki/HESA_Shahed_136) -- Speed, range, warhead weight
25. [Shahed-136 Research](https://drone-warfare.com/research/shahed-136/) -- Cost, production data
26. [Squadron (aviation) - Wikipedia](https://en.wikipedia.org/wiki/Squadron_(aviation)) -- Squadron sizes NATO/USAF
27. [Ground Master 400 - Wikipedia](https://en.wikipedia.org/wiki/Ground_Master_400) -- Ground radar detection ranges
28. [AEW&C - Wikipedia](https://en.wikipedia.org/wiki/Airborne_early_warning_and_control) -- AWACS detection ranges
29. [AN/APG-68 - Wikipedia](https://en.wikipedia.org/wiki/AN/APG-68) -- Fighter radar range data
30. [RAND Sortie Rate Model](https://www.rand.org/content/dam/rand/pubs/monograph_reports/MR1028/MR1028.appb.pdf) -- Sortie generation methodology
31. [Fighter Aircraft Fuel Consumption - flyajetfighter.com](https://www.flyajetfighter.com/fighter-aircraft-fuel-consumption/) -- Comparative fuel burn rates
32. [Defense Issues - Rafale vs Gripen](https://defenseissues.wordpress.com/2016/10/01/dassault-rafale-vs-saab-gripen/) -- Gripen fuel consumption data

## Methodology

Research was conducted using web searches across multiple query patterns for each aircraft type. For each aircraft, the following data points were targeted: cruise speed, max speed, combat radius, internal fuel capacity, fuel burn rate, weapons loadout, and turnaround/maintenance times.

**Search strategy:**
- Started with manufacturer and official military fact sheets (Saab, USAF, GA-ASI)
- Cross-referenced with Wikipedia articles (which aggregate multiple sources)
- Checked specialized defense publications and forums (F-16.net, Key Aero, Air & Space Forces Magazine)
- Used forum discussions and defense analysis sites for turnaround time data (often not in official specs)
- Derived fuel burn rates mathematically where direct data was unavailable (fuel capacity / endurance)

**Key derivation methods:**
- Fuel burn rate per km = (fuel burn rate per hour) / (cruise speed in km/h)
- Combat radius estimated as ~40% of ferry range when not directly available
- Su-34 fuel burn estimated from internal fuel capacity divided by approximate endurance at combat load

**Limitations of methodology:**
- Fuel burn rates vary enormously with altitude, speed, and load; cruise estimates represent optimistic mid-altitude values
- Turnaround times in practice depend on ground crew training, equipment availability, and maintenance state
- Many precise specifications are classified, especially for F-35A and Su-34

## Confidence Assessment

- **Overall confidence**: MEDIUM
- **HIGH confidence data points**: Max speeds, fuel capacities, weapons stations, Gripen turnaround time (well-documented by Saab)
- **MEDIUM confidence data points**: Combat radii (vary significantly by profile), fuel burn rates (estimated from endurance data), UAV operational parameters
- **LOW confidence data points**: Drone swarm parameters (largely speculative/emerging technology), Su-34 fuel burn rate (derived), F-35A quick-turn time (still under development)
- **Limitations**:
  - Real fuel burn rates depend on mission profile (altitude, speed, load) and can vary 2-3x
  - Turnaround times assume well-trained crews with proper equipment; degraded conditions could double these
  - Drone swarm is an emerging concept; no standardized platform exists yet
  - Bomber category combines very different aircraft types (Su-34 tactical vs B-1B strategic)
  - All "per km" burn rates assume constant cruise speed, which is unrealistic for combat missions
- **Recommendations**:
  - Run sensitivity analysis with parameters +/- 25% to identify which values most affect simulation outcomes
  - Consider making fuel burn rate speed-dependent (higher at low altitude / high speed)
  - Consider adding external fuel tank option that extends range but reduces weapons capacity
  - Validate that combat radii make sense within the 1,667 km x 1,300 km theater dimensions

## Applied In
- `backend/src/domain/entities/aircraft.py` -- Used for `_TYPE_DEFAULTS` dictionary values (speed_kmh, fuel_capacity, fuel_burn_rate, refuel_time_minutes, ammo_capacity, rearm_time_minutes, maintenance_time_minutes)
- `Development/DOMAIN.md` -- Referenced in aircraft type specifications tables
- `scenario/boreal_passage.json` -- Theater dimensions inform combat radius selection

## Last Updated
2026-04-17
