# Military Air Base Logistics

## Question
What are realistic parameters for military air base operations in a simulation: base aircraft capacity by base type, fuel storage and resupply rates, aircraft turnaround times, and sortie generation rates?

## Summary
Comprehensive logistics data for air base operations, covering capacity (forward operating bases through major command bases), JP-8 fuel storage and resupply, turnaround times across quick/standard/full maintenance cycles, and sortie generation rates for F-16, F-35, and JAS 39 Gripen. Confidence: MEDIUM -- based on published military data, manufacturer specifications, and operational records, but some values are approximations from publicly available sources rather than classified planning documents.

---

## Findings

### 1. Base Aircraft Capacity

#### Fighter Squadron Size
- **USAF standard fighter squadron**: 18-24 aircraft (typically organized as 4 flights of 4-6 aircraft)
- **USAF bomber squadron**: ~12 aircraft
- **A full-strength fighter squadron (24 jets)** requires ~30 pilots and ~480 maintenance personnel plus admin/intel/logistics staff
- **Squadrons per wing**: A wing typically contains 1-3 flying squadrons in its operations group

#### Forward Operating Base (FOB) / Austere Airstrip
- **Aircraft capacity**: 4-12 aircraft (typically a single flight or detachment)
- **Characteristics**: Limited or no hardened shelters, minimal taxiway/hangar space, temporary fuel storage, austere maintenance capability
- **Example**: Andersen NW Field (Guam) -- under 8,000 ft runway, deep jungle, no permanent airfield controls, operated F-16s and F-35s during exercises
- **USAF ACE concept**: "Hub and spoke" model where spokes are temporary dispersed sites hosting small numbers of combat aircraft with multi-capable airmen
- **Swedish dispersed model**: Road bases on civilian highways, designed for flights of 4-6 Gripens with minimal ground crew

| Parameter | FOB Value |
|---|---|
| Max aircraft | 4-12 |
| Squadrons | 0 (detachment/flight only) |
| Runway length | 6,000-8,000 ft (may be road strip) |
| Ground crew | 20-60 (multi-capable) |
| Hardened shelters | 0 |

#### Main Operating Base (MOB)
- **Aircraft capacity**: 48-72 aircraft (2-3 squadrons)
- **Characteristics**: Standard runway (10,000+ ft), taxiways, hardened shelters, permanent fuel infrastructure, full maintenance capability
- **Typical structure**: One wing with operations group (2-3 flying squadrons), maintenance group, mission support group, medical group
- **Personnel**: 2,000-5,000

| Parameter | MOB Value |
|---|---|
| Max aircraft | 48-72 |
| Squadrons | 2-3 |
| Runway length | 10,000+ ft |
| Ground crew | 1,000-2,500 (maintenance) |
| Hardened shelters | 24-48 |

#### Major Command Base
- **Aircraft capacity**: 72-150+ aircraft (3-6+ squadrons, possibly multiple wings)
- **Characteristics**: Multiple runways, extensive hardened shelters, large fuel reserves, depot-level maintenance, command and control facilities
- **Examples**: Large USAF bases like Langley, Nellis, Kadena

| Parameter | Major Base Value |
|---|---|
| Max aircraft | 72-150+ |
| Squadrons | 3-6+ |
| Runways | 2+ |
| Ground crew | 3,000-6,000+ (maintenance) |
| Hardened shelters | 48-100+ |

### 2. Fuel Storage and Resupply

#### Fuel Storage Capacity by Base Type

| Base Type | Storage Capacity (gallons) | Storage Capacity (liters) | Storage Capacity (metric tons) |
|---|---|---|---|
| Forward Operating Base | 50,000-500,000 | 190,000-1,900,000 | 150-1,500 |
| Main Operating Base | 1,000,000-5,000,000 | 3,800,000-19,000,000 | 3,000-15,000 |
| Major Command Base | 5,000,000-66,000,000 | 19,000,000-250,000,000 | 15,000-200,000 |
| Strategic Reserve (e.g. Red Hill) | 250,000,000 (250M gal) | ~950,000,000 | ~750,000 |

Notes:
- Typical POL complexes feature 2x 50,000-gallon above-ground storage tanks as a baseline
- Collapsible tactical tanks range from a few hundred gallons up to 210,000 gallons each
- Army Tactical Petroleum Terminal: up to 1,080,000 gallons per fuel unit (3 units)
- Defense Fuel Support Point Ozol: 1,000,000 barrels (42M gallons) in 12 underground tanks

#### Fuel Resupply Rates

| Method | Rate | Notes |
|---|---|---|
| Single fuel truck (M970) | 5,000 gal/delivery | Standard military fuel tanker |
| Large fuel truck | 5,000-12,000 gal/delivery | Civilian-grade tankers |
| Hydrant refueling system | ~1 aircraft/hour (large) | Fixed base infrastructure |
| Pipeline (NATO CEPS-type) | Continuous, thousands of gal/hr | Fixed infrastructure, vulnerable to attack |
| C-17 airlift | ~90,000 lbs fuel/sortie | Enough for ~6 F-35A refuels |
| KC-135 aerial refueling | Up to 1,000 gal/min (boom) | Air-to-air; 3,785 L/min |

#### Fuel Consumption Per Sortie

| Aircraft Type | Fuel Burn (gal/hr) | Fuel Burn (L/hr) | Typical Sortie Duration | Fuel Per Sortie (gal) |
|---|---|---|---|---|
| F-16 (cruise) | 800 | 3,028 | 1.5-3 hrs | 1,200-2,400 |
| F-16 (afterburner) | 2,400+ | 9,000+ | N/A (intermittent) | -- |
| F-35A (cruise) | 1,300-1,500 | 5,000-5,700 | 2-2.5 hrs | 2,600-3,750 |
| F-35A (afterburner) | 4,000+ | 15,000+ | N/A (intermittent) | -- |
| Gripen C/E (cruise) | ~550-700 | ~2,100-2,650 | 1.5-2.5 hrs | 825-1,750 |
| B-52 (cruise) | 2,400-3,300 | 9,000-12,500 | 8-16 hrs | 19,200-52,800 |
| B-1B (cruise) | ~3,000 | ~11,350 | 6-10 hrs | 18,000-30,000 |

Notes:
- Gripen is notably fuel-efficient; cost per flight hour ~$4,700 (lowest among Western fighters as of 2012 study)
- Gripen internal fuel: ~3,400 kg (~7,500 lbs); refuel rate: 600+ liters/min
- F-16 internal fuel: ~7,000 lbs (~3,175 kg)
- B-1B at full afterburner: ~250,000 lbs/hr (extreme case, sea level)
- JP-8 density: ~6.7 lbs/gal (~0.8 kg/L)

### 3. Aircraft Turnaround Times

#### Quick Turnaround (Hot Pit Refueling)
- **Definition**: Refueling with engines running, minimal or no rearming
- **Typical time**: 13-20 minutes
- **Best recorded**: ~13 minutes (USAF gold standard)
- **Gripen air-to-air mission**: 10 minutes (1 technician + 5 conscripts) -- SAAB published specification
- **Gripen air-to-ground mission**: 20 minutes (same crew)
- **Notes**: Aircraft keeps engines running; dramatically faster than cold turnaround; essential for Agile Combat Employment (ACE) doctrine

#### Standard Turnaround (Refuel + Rearm + Basic Checks)
- **RAND model breakdown** (total ~180 minutes / 3 hours):
  - Land and taxi: 10 min
  - Make aircraft safe for ground ops: 5 min
  - Shut down systems: 2 min
  - Post-flight inspection/debrief: 15 min
  - Re-arm: 50 min
  - Service: 20 min
  - Refuel: 30 min
  - Pre-flight inspection: 15 min
  - Start-up and taxi: 10 min
  - Other: ~23 min
- **Non-hot refuel/re-arm shortcut**: ~30-60 minutes (without full inspection cycle)
- **C-130 FARP operation**: Under 60 minutes (refuel + rearm F-15/F-35 from C-130)

#### Full Maintenance Turnaround
- **F-15/F-16 maintenance**: 3.4 hours of maintenance time per sortie + 0.64 hours per flight hour
- **F-35A maintenance**: 3.8 maintenance man-hours per flight hour (MMH/FH)
- **F-35B maintenance**: 7.7 MMH/FH
- **Full phase inspection**: 4-6+ hours (historical: aircraft spent 4-6 hours cooling in hangar before servicing)
- **Daily preventive maintenance**: 30-60 minutes

#### JAS 39 Gripen Turnaround (Detailed)

| Turnaround Type | Time | Crew Required | Notes |
|---|---|---|---|
| Air-to-air quick turn | 10 min | 1 tech + 5 conscripts | SAAB published spec |
| Air-to-ground quick turn | 20 min | 1 tech + 5 conscripts | SAAB published spec |
| Gripen E air-to-air | 15 min | Limited ground crew | Gripen E series |
| Engine replacement | < 60 min | Standard crew | Design feature |
| Hot refueling | Supported | -- | Engine running during refuel |

Gripen design philosophy: maintenance-friendly layout; many subsystems require little or no maintenance; operational availability exceeds 85%.

### 4. Sortie Generation Rates

#### Published Sortie Rates Per Aircraft Per Day

| Aircraft | Surge Rate | Sustained Rate | Notes/Source |
|---|---|---|---|
| F-35A | 3.4/day (initial surge) | 2.0/day (wartime sustained) | USAF KPP; 2.5-hr avg sortie duration |
| F-35B | 4.0/day (surge) | -- | USAF KPP requirement |
| F-35C | 3.0/day (surge) | -- | USAF KPP requirement |
| F-16 (Desert Storm avg) | 1.3/day (campaign avg) | -- | 13,500 sorties / 249 aircraft / 42 days |
| Gripen | 6-8/day (surge) | 4-6/day (sustained) | 14 aircraft producing 112 sorties/day = 8/sortie/aircraft |
| Generic 4th gen | 2-3/day (surge) | 1-1.5/day (sustained) | Industry rule of thumb |

Notes:
- Desert Storm F-16 average of 1.3/day was a campaign average including stand-down days, weather delays, and the fact that not all aircraft flew every day
- Peak single-day rates were likely 2-3 sorties per aircraft during intense operations
- Gripen's 8 sorties/day figure assumes 24-hour operations with shift crews and road-base dispersed operations, leveraging the 10-minute turnaround
- F-35 operational availability: 54% (F-35A/B) to 58% (F-35C) fleet-wide; forward deployments achieve 80-87%
- Gripen operational availability: >85%

#### Factors Affecting Sortie Rate
1. Turnaround time (dominant factor)
2. Aircraft availability / mission capable rate
3. Pilot availability and crew rest requirements
4. Fuel availability
5. Weapons availability
6. Weather
7. Maintenance backlog
8. Base damage / runway repair time

---

## Sources

1. [Squadron (aviation) - Wikipedia](https://en.wikipedia.org/wiki/Squadron_(aviation)) -- Squadron size data (12-24 aircraft depending on type)
2. [AeroCorner - How Many Aircraft in a Squadron](https://aerocorner.com/blog/how-many-planes-squadron/) -- Squadron composition details
3. [SAAB Gripen Wikipedia](https://en.wikipedia.org/wiki/Saab_JAS_39_Gripen) -- Gripen turnaround times, fuel capacity, dispersed operations
4. [SAAB Official Tweet on Turnaround Time](https://x.com/Saab/status/1706296323186512184) -- 10-minute turnaround with limited crew
5. [SAAB Gripen E-series Product Page](https://www.saab.com/products/gripen-e-series) -- Gripen E 15-minute turnaround, >85% availability
6. [SAAB Dispersed Operations Story](https://www.saab.com/newsroom/stories/2024/september/dispersed-operations-with-gripen) -- Road-base operations, 112 sorties/day from 14 aircraft
7. [DVIDSHUB - 103d Rapid Refueling](https://www.dvidshub.net/news/543957/103d-provides-rapid-fighter-jet-refueling-rearming-record-time-with-c-130h) -- C-130 FARP refueling F-15/F-35 in under 60 minutes
8. [DVIDSHUB - 78th LRS Hot Pit Refueling](https://www.dvidshub.net/news/561128/78th-lrs-powers-air-superiority-with-hot-pit-refueling) -- 13-minute hot pit turnaround, 60-minute standard
9. [SimpleFlying - Hot Pit Refueling](https://simpleflying.com/hot-pit-refueling-us-air-force-rapid-fuel-sites/) -- USAF expanding hot pit sites for ACE
10. [FlyAJetFighter - Fuel Consumption](https://www.flyajetfighter.com/fighter-aircraft-fuel-consumption/) -- F-16: 800 gal/hr, F-35: 1,500 gal/hr
11. [F-16.net - Desert Storm Legacy](https://www.f-16.net/varia_article3.html) -- 13,500 sorties, 249 aircraft, sortie duration data
12. [PBS Frontline - Air Force Performance in Desert Storm](https://www.pbs.org/wgbh/pages/frontline/gulf/appendix/whitepaper.html) -- Desert Storm air campaign statistics
13. [Air & Space Forces Magazine - Generating Sorties](https://www.airandspaceforces.com/article/1188usafe/) -- Sortie generation in USAFE operations
14. [Mike's Defense Talk - Sortie Generation Rate](https://www.mikesdefensetalk.com/post/the-overwhelming-importance-of-sortie-generation-rate) -- F-35 surge/sustained sortie rates
15. [FlightGlobal - F-35B Sortie Rate](https://www.flightglobal.com/usaf-f-35b-cannot-generate-enough-sorties-to-replace-a-10/105388.article) -- F-35B 4 sorties/day KPP
16. [Red Hill Fuel Storage - Wikipedia](https://en.wikipedia.org/wiki/Red_Hill_Underground_Fuel_Storage_Facility) -- Strategic fuel reserve example
17. [GlobalSecurity - Bulk Fuel Storage](https://www.globalsecurity.org/military/library/policy/army/fm/5-482/ch72.htm) -- Military fuel storage standards
18. [Defense Logistics Agency FY2024 MILCON](https://comptroller.defense.gov/Portals/45/Documents/defbudget/fy2024/budget_justification/pdfs/07_Military_Construction/9-Defense_Logistics_Agency.pdf) -- DLA fuel facility specifications
19. [Boeing B-52 Stratofortress - Wikipedia](https://en.wikipedia.org/wiki/Boeing_B-52_Stratofortress) -- B-52 fuel consumption data
20. [Air University - Forward Arming and Refueling Points](https://www.airuniversity.af.edu/Portals/10/ASPJ/journals/Volume-28_Issue-5/F-Davis.pdf) -- FARP doctrine for fighters
21. [Air & Space Forces - Austere Airfield Operations](https://www.airandspaceforces.com/f-35s-f-16s-to-operate-from-austere-airfield-on-guam-during-cope-north/) -- FOB exercise data
22. [Structure of the USAF - Wikipedia](https://en.wikipedia.org/wiki/Structure_of_the_United_States_Air_Force) -- Wing/squadron organizational structure
23. [Air & Space Forces - F-35 Reliability 2023](https://www.airandspaceforces.com/f-35-reliability-maintainability-availability-2023/) -- F-35 MMH/FH and availability rates
24. [Defense Daily - F-35 Maintenance Rates](https://www.defensedaily.com/u-s-f-35-maintenance-man-hours-per-flight-hour-rate-improves-since-2018-but-mission-capable-rates-lag/air-force/) -- F-35A: 3.8 MMH/FH, F-35B: 7.7 MMH/FH
25. [Aerial Refueling - Wikipedia](https://en.wikipedia.org/wiki/Aerial_refueling) -- KC-135 boom: 1,000 gal/min
26. [Air & Space Forces - Cargo Fuel Planes](https://www.airandspaceforces.com/air-force-cargo-fuel/) -- C-17 fuel delivery: 90,000 lbs per sortie

---

## Methodology

Research conducted via web search on 2026-04-17 using multiple search queries covering:
- Military air base capacity and organization (USAF, Swedish Air Force)
- JP-8 fuel storage specifications from Defense Logistics Agency and military facility data
- Aircraft turnaround times from SAAB manufacturer data, USAF operational reports, and DVIDSHUB press releases
- Sortie generation rates from Desert Storm historical data, USAF Key Performance Parameters, and SAAB marketing/operational data
- Fuel consumption from aircraft specification databases and manufacturer data

Data was cross-referenced across multiple sources where possible. Values that appeared in both manufacturer specifications and independent operational reports were given higher confidence.

---

## Confidence Assessment

- **Overall confidence**: MEDIUM
- **High confidence items**:
  - Gripen turnaround times (manufacturer-published, widely cited, consistent across sources)
  - Squadron sizes (well-documented USAF standard)
  - F-16 Desert Storm sortie data (official records)
  - Fuel consumption rates for F-16, F-35, B-52 (widely published)
- **Medium confidence items**:
  - Base capacity ranges (varies significantly by specific installation)
  - Fuel storage ranges (varies by base; specific installations well-documented but ranges are estimates)
  - F-35 sortie rates (KPP values are targets; actual operational rates may differ)
  - Standard turnaround time breakdown (RAND model, may not reflect all aircraft types)
- **Low confidence items**:
  - FOB capacity (highly variable, depends on specific austere site)
  - B-1B fuel consumption at cruise (limited public data, converted from pounds)
  - Sustained sortie rates (rarely published; dependent on logistics chain)
- **Limitations**:
  - Most data is from USAF; other air forces may operate differently
  - Wartime vs. peacetime sortie rates differ significantly
  - Base capacity is not just about ramp space but also maintenance, fuel, weapons, and personnel
  - Many specific values are classified; public estimates may not reflect actual planning factors
- **Recommendations**:
  - For simulation defaults, use the mid-range values from the tables above
  - Implement configurable parameters so values can be tuned during scenario design
  - Run sensitivity analysis on turnaround time (dominant factor in sortie generation)
  - The Gripen's 10-minute turnaround should be a distinctive gameplay feature given this is a SAAB project

---

## Simulation Default Recommendations

For the Boreal Passage simulation, recommended default values:

| Parameter | Default | Min | Max | Unit |
|---|---|---|---|---|
| FOB capacity | 8 | 4 | 12 | aircraft |
| MOB capacity | 54 | 36 | 72 | aircraft |
| Major base capacity | 96 | 72 | 150 | aircraft |
| FOB fuel storage | 200,000 | 50,000 | 500,000 | gallons |
| MOB fuel storage | 2,000,000 | 1,000,000 | 5,000,000 | gallons |
| Quick turnaround (fighter) | 15 | 10 | 25 | minutes |
| Quick turnaround (Gripen) | 10 | 10 | 15 | minutes |
| Standard turnaround (fighter) | 120 | 60 | 180 | minutes |
| Full maintenance turnaround | 360 | 240 | 480 | minutes |
| Fighter sortie fuel (gallons) | 1,800 | 1,000 | 3,500 | gallons |
| Bomber sortie fuel (gallons) | 25,000 | 18,000 | 50,000 | gallons |
| Fighter surge sorties/day | 3 | 2 | 8 | sorties |
| Fighter sustained sorties/day | 1.5 | 1 | 3 | sorties |
| Fuel truck delivery | 6,000 | 5,000 | 12,000 | gallons |

---

## Applied In
- `scenario/boreal_passage.json` -- Base capacity and fuel storage configuration
- `backend/src/domain/entities/` -- Aircraft turnaround time and fuel consumption attributes
- `backend/src/domain/value_objects/` -- Base type definitions and capacity limits
- `Development/DOMAIN.md` -- Reference tables for logistics parameters

## Last Updated
2026-04-17
