# Air Defense Intercept Doctrine and Engagement Realism

## Question
How do real-world air defense interceptions work? What are the escalation procedures, rules of engagement, deterrence effects, BVR engagement mechanics, multi-wave defense coordination, asymmetric defense strategies, and Swedish-specific doctrine? How should these inform simulation design beyond the current "all engagements result in one side destroyed" model?

## Summary
Real-world air defense is a multi-layered process where most interceptions never result in combat. Engagements follow an escalation ladder (detect -> identify -> intercept -> shadow/escort -> warn -> engage), with combat being the last resort governed by strict Rules of Engagement. Even in wartime, BVR missile exchanges have historical kill probabilities of 40-77% depending on conditions, missiles can be evaded, and pilots frequently disengage rather than fight to destruction. Swedish doctrine specifically optimizes for asymmetric defense through dispersed basing (BAS 90), rapid turnaround, and attrition-based denial strategy. Confidence: MEDIUM - based on open-source military doctrine, NATO publications, historical combat data, and defense analysis.

## Findings

### 1. Air Defense Intercept Procedures

#### The Intercept Chain: Detection to Engagement

Air defense follows a strict procedural chain with multiple decision points before any weapons employment:

**Phase 1 - Detection**: Surveillance radars (ground-based or AWACS) detect an unidentified track. Modern radar enables detection at hundreds of kilometers, giving significant warning time. NATO's Air Surveillance and Control System (NASOC) and equivalent national systems continuously monitor airspace.

**Phase 2 - Classification & Identification**: The track is classified as friendly, neutral, or unknown. IFF (Identification Friend or Foe) transponder interrogation is the first step. If IFF fails or is not present, the track becomes a "bogey" (unknown) requiring further investigation.

**Phase 3 - Scramble / Alert Launch**: If the track warrants investigation, QRA (Quick Reaction Alert) fighters are scrambled. Alert states determine response time:
- **Alpha Scramble / Alert 5**: Pilots in cockpit, aircraft armed and fueled, airborne within 5 minutes. Used during heightened tension.
- **Alert 15**: Pilots at ready room near aircraft, airborne within 15 minutes. Standard peacetime NATO QRA posture.
- **Alert 30/60**: Pilots on base, longer response times. Lower threat levels.

Most NATO QRA bases maintain Alert 15 as the standard posture. During the Baltic Air Policing mission (running since 2004), NATO nations rotate responsibility for maintaining QRA fighters at bases in Estonia, Latvia, and Lithuania.

**Phase 4 - Intercept**: Fighters are vectored toward the target by ground-controlled interception (GCI) or AWACS controllers. The intercept itself is NOT combat -- it is a rendezvous with the unknown aircraft for identification purposes. Interceptors approach from a position of advantage and establish visual or radar contact.

**Phase 5 - Visual Identification (VID)**: The interceptor flies close enough to visually identify the aircraft type, markings, nationality, and armament state. VID is required in most peacetime ROE before any further action. Pilots photograph the target aircraft. This is the most common outcome of NATO scrambles -- a VID pass followed by escort.

**Phase 6 - Escort / Shadow**: If the aircraft is identified as non-hostile but non-compliant (e.g., Russian military aircraft flying near NATO airspace without transponder), interceptors shadow or escort it through the area. Shadowing means following from behind; escorting means flying in formation alongside.

**Phase 7 - Warning & Deterrence**: If the aircraft is hostile or violating airspace, interceptors attempt communication on guard frequency (121.5 MHz), use ICAO visual signals (wing rocking, flashing lights), and attempt to divert the aircraft.

**Phase 8 - Engagement**: Only as a last resort, and only with explicit authorization from national command authority under applicable ROE.

#### Critical Insight for Simulation
The vast majority of real-world interceptions end at Phase 5 or 6. NATO conducted approximately 300-570 scrambles per year against Russian aircraft (2022-2024), and NONE resulted in combat. Interception and engagement are fundamentally different things.

**Simulation implication**: The simulation should model interception as a separate state from engagement. Aircraft entering an intercept zone should not automatically fight. The decision to engage should be a separate strategic choice governed by ROE settings.

### 2. Rules of Engagement and Escalation Ladder

#### Weapons Control Orders

NATO uses three standard weapons control statuses that govern when air defense systems (including fighters) may fire:

| Status | Definition | When Used |
|---|---|---|
| **Weapons Free** | Fire at any target not positively identified as friendly | Active wartime, heavy attack in progress |
| **Weapons Tight** | Fire only at targets positively identified as hostile per ROE | Standard wartime posture, heightened tension |
| **Weapons Hold** | Fire only in self-defense or on explicit formal orders | Peacetime, de-escalation, friendly aircraft in area |

#### Escalation Ladder

The escalation ladder in air defense typically follows this progression:

1. **Passive Detection** - Radar tracking only, no response
2. **Active Tracking** - Lock-on with fire control radar (detected by target's RWR)
3. **Alert Scramble** - QRA fighters launched
4. **Intercept** - Fighters close for identification
5. **Shadow/Escort** - Continuous monitoring alongside intruder
6. **Warning** - Radio warnings, visual signals, show of force
7. **Warning Shots** - Across the bow (extremely rare, political decision)
8. **Weapons Free / Engagement** - Authorized to fire

#### ROE by Threat Level

| Threat Level | Typical Posture | Weapons Status | Engagement Authority |
|---|---|---|---|
| Peacetime | QRA Alert 15 | Weapons Hold | National command only |
| Heightened Tension | QRA Alert 5, increased CAP | Weapons Hold / Tight | Senior military command |
| Crisis | Full alert, dispersal | Weapons Tight | Theater commander |
| Wartime | Full operations | Weapons Tight / Free | Mission commander (delegated) |

**Simulation implication**: The simulation should model ROE as a configurable parameter. A "peacetime" scenario where intercepts almost never lead to combat behaves very differently from a "wartime" scenario with Weapons Free. The current simulation's assumption of automatic combat on contact is only realistic under Weapons Free conditions.

### 3. Deterrence and Non-Kinetic Effects

#### Combat Air Patrol (CAP)

A Combat Air Patrol is a defensive flight pattern where fighters orbit a designated area, ready to intercept incoming threats. CAP is the backbone of Defensive Counter Air (DCA) operations.

**How CAP deters**: The mere presence of armed fighters on station forces the attacker to:
- Allocate escort fighters to protect strike packages (reducing strike capacity)
- Route around defended zones (increasing fuel consumption, exposure time)
- Abort missions when intercepted before reaching targets
- Accept risk of engagement losses (deterring all but the most critical missions)

#### Defensive Counter Air (DCA) vs. Offensive Counter Air (OCA)

| Concept | Definition | Key Methods |
|---|---|---|
| **DCA** | Protect own territory from enemy air attack | CAP, point defense, area defense, GCI |
| **OCA** | Attack enemy air capability at source | Airfield strikes, SEAD/DEAD, fighter sweeps |

DCA is inherently defensive and reactive. It seeks to deny the enemy the use of airspace over friendly territory. OCA is proactive -- attacking the enemy's ability to generate sorties.

#### Air Superiority Spectrum

The doctrine defines degrees of air control (from NATO AAP-06):

| Level | Definition | Implication |
|---|---|---|
| **Air Supremacy** | Complete dominance, enemy incapable of effective air operations | Rare, requires total defeat of enemy air force |
| **Air Superiority** | Sufficient dominance to conduct operations without prohibitive interference | Standard goal for offensive side |
| **Air Parity** | Neither side has control, both experience significant interference | Contested environment, high attrition |
| **Air Denial** | Cannot achieve superiority but prevent enemy from achieving it | Defender's realistic goal when outnumbered |

**Air denial** is the critical concept for the Boreal Passage scenario. A smaller air force (Country X/North) may not be able to achieve air superiority over the strait, but can maintain enough capability to prevent the enemy from operating freely -- making their attacks costly and their objectives unachievable.

**Simulation implication**: The simulation should model deterrence effects. A CAP zone should reduce the probability that enemy strike aircraft successfully reach their targets, even without direct engagement. Enemy AI should factor in the presence of defenders when deciding whether to commit to an attack.

### 4. What Actually Happens in Engagements

#### BVR Engagement Sequence

Modern air-to-air combat follows a structured sequence, not a single dice roll:

**Phase 1 - Detection & Lock**: The fighter with better radar/lower RCS detects first. Detection advantage is critical -- the first to detect typically gets the first shot.

**Phase 2 - First Shot**: Pilot climbs and accelerates to maximize missile energy, then fires BVR missile (e.g., AIM-120 AMRAAM, Meteor, R-77). First shot at extreme range has LOW kill probability.

**Phase 3 - Defend**: The target, warned by its Radar Warning Receiver (RWR), executes defensive maneuvers:
- **Cranking**: Turn perpendicular while maintaining own radar lock (preserves counter-attack option)
- **Notching**: Turn perpendicular to threat radar to exploit Doppler clutter rejection
- **Going Cold**: Turn 180 degrees and dive to maximize distance and deplete missile energy
- **Chaff/Flares**: Expendable countermeasures against radar and IR guided missiles
- **ECM (Electronic Countermeasures)**: Jamming to degrade missile guidance

**Phase 4 - BDA (Battle Damage Assessment) / Recommit**: If missile misses, the attacker must decide: recommit for another pass or disengage. This decision depends on fuel state, ammo remaining, threat environment, and mission priority.

**Phase 5 - Merge / WVR**: If BVR exchanges fail to resolve the engagement and aircraft close to within visual range (~10-20 km), a Within Visual Range (WVR) dogfight may develop. This is what most people think of as "air combat" but it is actually the failure mode of BVR tactics.

#### Missile Kill Probabilities (Pk)

Historical data from the AIM-120 AMRAAM:
- **Overall operational Pk**: 59% (10 kills from 17 shots) to 77% (10 kills from 13 shots), depending on how engagements are counted
- **Under ideal conditions** (non-maneuvering target, short range, no ECM): 60-90%
- **Typical operational mix** (some maneuvering, medium range): 40-70%
- **Adverse conditions** (heavy ECM, high-g maneuvers, long-range shot): 20-50%
- **Within the No Escape Zone (NEZ)**: Pk approaches 80-90% as the target cannot outmaneuver the missile even at maximum performance

These numbers mean that a single missile exchange often does NOT result in a kill. In a realistic BVR engagement:
- First shot at long range: ~30-50% Pk
- Defender evades, recommits
- Second shot at closer range: ~50-70% Pk
- Possible third exchange or merge to WVR

#### Engagement Outcomes Beyond Kill/Survive

Real engagements have multiple possible outcomes:

1. **Kill** - Missile hits, aircraft destroyed
2. **Mission Kill** - Aircraft damaged, forced to abort/RTB but not destroyed
3. **Evasion & Disengage** - Defender evades missile, breaks contact, retreats
4. **Mutual Disengage** - Both sides run low on fuel/ammo, break off
5. **Deterred/Turned Back** - Attacker sees defender, aborts mission without shots fired
6. **Fuel Critical Abort** - Defender must RTB due to fuel regardless of tactical situation

**Simulation implication**: The current binary "attacker wins or defender wins, loser destroyed" model misses significant realism. The simulation should model:
- Multi-round engagements with per-round Pk
- Evasion and countermeasures reducing effective Pk
- Disengagement as a valid outcome (aircraft retreats, mission disrupted but aircraft survives)
- Ammo depletion forcing RTB (already partially modeled)
- "Mission kill" -- attacker forced to jettison bombs and flee, failing to reach target even if not destroyed

### 5. Multi-Wave Attack Defense

#### The Air Defense Battle Sequence

When facing a sustained air campaign, air defense follows a layered response:

1. **Outer Layer - Early Warning**: AWACS and long-range radar detect incoming raid at 300-500+ km
2. **Threat Assessment**: Command center determines raid size, composition, likely targets
3. **Force Allocation**: Decide how many fighters to scramble vs. hold in reserve
4. **Fighter Assignment**: GCI/AWACS vectors specific fighters to specific threat groups
5. **Engagement Layer**: Fighters intercept at maximum range from defended assets
6. **Inner Layer**: Point defense SAMs and remaining fighters protect high-value targets
7. **Reconstitution**: Surviving fighters RTB, refuel, rearm for next wave

#### AWACS Coordination

AWACS aircraft serve as airborne command posts, providing:
- 360-degree radar coverage out to 400+ km
- Real-time tracking of hundreds of aircraft simultaneously
- Fighter control -- vectoring interceptors to optimal engagement positions
- Deconfliction -- preventing friendly fire in complex multi-aircraft scenarios
- Battle management -- deciding when to commit reserves, when to disengage

#### Force Packaging (Attacker Side)

Attackers organize into "force packages" containing:
- **Strike aircraft**: The bombers/attackers carrying the payload
- **Escort fighters**: Protecting the strike aircraft
- **SEAD/DEAD aircraft**: Suppressing/destroying enemy air defenses
- **ECM/EW aircraft**: Providing electronic warfare support
- **Tankers**: Air-to-air refueling for extended range

The defender must determine which aircraft in the package are the primary threat (strike aircraft) and which are escorts, then allocate forces accordingly. Engaging the escorts while strike aircraft reach their targets is a failure even if the air-to-air battle is "won."

#### Reserve Management

The critical question for the defender facing multiple waves:

- **Commit too many to Wave 1**: No reserves for Wave 2, enemy achieves air superiority
- **Hold too many in reserve**: Wave 1 breaks through, targets are hit
- **Optimal strategy**: Commit enough to attrit and disrupt each wave while maintaining a viable reserve. Accept some leakage in exchange for sustainable defense.

**Simulation implication**: The strategy interface should allow managing reserve allocation. A good strategy holds some aircraft back rather than scrambling everything at the first contact. The simulation should model wave-based attacks and test strategies that balance immediate response vs. reserve retention.

### 6. Asymmetric Defense (Outnumbered Defender)

This is the core scenario for Boreal Passage. How does a smaller air force survive and defend effectively?

#### Historical Model: Sweden vs. Soviet Union

During the Cold War, Sweden maintained one of the world's largest air forces (peaking at ~1,000 combat aircraft in 50 squadrons in the 1950s) specifically to counter Soviet numerical superiority. Even so, they would have been outnumbered in a conflict. Their strategy was not to win air superiority but to make invasion prohibitively costly.

#### Force Multipliers for the Defender

1. **Dispersed Basing (BAS 90)**: Spread aircraft across many small bases so no single strike can destroy significant capability. Sweden planned for ~200 dispersed bases including highway strips.

2. **Rapid Turnaround**: The Gripen was specifically designed for 10-minute turnaround (refuel, rearm for air-to-air) by a team of 1 technician + 5 conscripts, on a highway strip. This means each aircraft generates more sorties per day than the attacker's aircraft. A force of 100 Gripens with 10-minute turnaround can generate as many daily sorties as a much larger force with 60-minute turnaround.

3. **Short Takeoff**: Gripen operates from 500m road strips, making it nearly impossible to eliminate all operating surfaces. The attacker would need to crater every viable road section in the country.

4. **Interior Lines**: The defender operates closer to base, spending less fuel on transit, allowing more time on station and more sorties per day.

5. **Terrain Knowledge**: Defenders exploit terrain for masking, ambush positions, and radar shadow.

6. **Integrated Air Defense**: Combining fighters with ground-based SAMs, radar networks, and C2 infrastructure creates a layered defense that is harder to suppress than any single component.

7. **Attrition Math**: Even unfavorable exchange ratios favor the defender if the attacker must sustain operations. If the defender loses 1 aircraft for every 2 attackers lost, but the defender can regenerate sorties faster, the attacker's force degrades over time.

#### Air Denial Strategy

The outnumbered defender's realistic goal is air denial, not air superiority:

- Accept that the enemy will have some freedom of action
- Focus on making every enemy sortie costly
- Prioritize defending the highest-value assets (capital, key bases)
- Use "economy of force" -- minimum defenders at secondary targets, concentration at primary
- Force the attacker to expend escort fighters, reducing their strike capacity
- Exploit defensive advantage: the defender chooses when and where to engage

**Simulation implication**: The simulation should model sortie generation rate as a critical factor. An aircraft that lands, refuels in 10 minutes, and launches again is worth much more than one that takes 60 minutes. The BAS 90 concept of dispersed basing should be modelable -- smaller bases with faster turnaround trading capacity for survivability.

### 7. Swedish Air Force Doctrine (Flygvapnet)

#### BAS 90 (Flygbassystem 90)

Developed in the 1970s-80s as an evolution of BAS 60, BAS 90 was Sweden's answer to the lessons of the Six-Day War (where Israel destroyed the Egyptian Air Force on the ground) and the growing Soviet cruise missile and cluster munition threat.

**Key features**:
- Each air base had a main runway plus multiple "kortbana" (short runways, 800m x 17m) in the surrounding area
- Ground crews were fully motorized ("rorlig klargorning" / mobile turnaround), carrying fuel, ammo, tools in vehicles
- Aircraft could disperse to any of dozens of pre-prepared positions along highway strips
- Positions were camouflaged into the surrounding landscape
- Each position had hardened communications links back to the main base
- The system was designed so that losing the main runway did not mean losing the base's operational capability

#### Gripen's Design for BAS 90

The JAS 39 Gripen was purpose-built for this doctrine:
- **Self-contained**: Internal APU, automated diagnostics, minimal ground support equipment needed
- **10-minute air-to-air turnaround**: Refuel, rearm, inspect by small team
- **20-minute air-to-ground turnaround**: Longer due to weapons loading
- **500m runway requirement**: Operable from reinforced road sections
- **"Airborne within 5 minutes"**: From alert state, comparable to NATO Alpha Scramble

#### Swedish Total Defense Concept

Sweden's "totalforsvar" (total defense) integrates military and civilian resources. For air operations, this means:
- Civilian infrastructure (roads, fuel depots) is pre-designated for military use
- Conscript ground crews are trained during peacetime for wartime dispersed operations
- The entire Swedish road network is a potential basing system
- Redundant C2 (command and control) ensures operations continue even if main headquarters are destroyed

#### Differences from NATO Doctrine

| Aspect | NATO Approach | Swedish Approach |
|---|---|---|
| Basing | Large, fixed airbases | Dispersed, road-based, mobile |
| Turnaround | 45-90 min typical | 10-20 min |
| Ground crew | Professional, specialized | Small mixed teams (1 tech + conscripts) |
| Runway req. | 2000-3000m | 500-800m |
| C2 | Centralized (CAOC) | Decentralized, autonomous wing-level |
| Strategy | Air superiority | Air denial through attrition |
| Logistics | Large supply chains | Pre-positioned, distributed |

**Simulation implication**: Country X (North) in the Boreal Passage scenario can be modeled on Swedish doctrine. Smaller bases with faster turnaround, dispersed positioning, and an air denial strategy. The simulation should allow strategies that exploit these characteristics -- rapid sortie generation, dispersal to avoid base destruction, and selective engagement rather than seeking decisive battle.

## Simulation Design Recommendations

Based on this research, the current simulation model should be enhanced with:

### Priority 1: Engagement Outcome Model (Replace Binary Kill)
- Model engagements as multi-round BVR exchanges with per-round Pk
- Add "disengage" as an outcome (aircraft survives but mission disrupted)
- Add "mission kill" (bomber forced to jettison payload, fails to strike target)
- Add "deterred/turned back" when interceptors are present near targets

### Priority 2: Escalation / ROE System
- Add configurable ROE levels (Weapons Hold / Tight / Free)
- Model "intercept without engage" as a valid action
- Add deterrence effects from fighter presence in zones

### Priority 3: Sortie Generation Rate
- Model turnaround time as the critical force multiplier
- Allow rapid-turnaround bases (Gripen/BAS 90 style)
- Sortie rate = f(turnaround_time, base_capacity, fuel_availability)

### Priority 4: Multi-Wave Defense
- Allow strategies to hold reserves
- Model attacker force packaging (strike + escort + SEAD)
- Test reserve allocation strategies across waves

### Priority 5: Air Denial Mechanics
- Model CAP zones with deterrence radius
- Enemy strike aircraft should factor defender presence in routing
- "Air denial score" metric: what percentage of enemy sorties fail to reach targets

## Sources

1. [NATO Air Policing](https://www.nato.int/en/what-we-do/deterrence-and-defence/nato-air-policing) -- NATO official description of air policing mission and QRA procedures
2. [Quick Reaction Alert - Wikipedia](https://en.wikipedia.org/wiki/Quick_Reaction_Alert) -- Overview of QRA alert states and procedures
3. [NATO Allied Air Command - Scramble Reports](https://ac.nato.int/archive/2022/nato-jets-scramble-in-response-to-russian-aircraft-over-baltic-and-black-sea) -- Real-world scramble and intercept examples
4. [Weapons Tight - Wikipedia](https://en.wikipedia.org/wiki/Weapons_Tight) -- NATO weapons control orders definitions
5. [FM 44-8 Chapter 2 - U.S. Army Air Defense](https://www.globalsecurity.org/military/library/policy/army/fm/44-8/ch2.htm) -- Weapons control statuses and ROE framework
6. [USAF AFDP 3-01 Counterair Operations (2023)](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-01/3-01-AFDP-COUNTERAIR.pdf) -- Official USAF doctrine on DCA, OCA, air superiority
7. [JAPCC - Defensive Counter-Air Operations](https://www.japcc.org/chapters/c-uas-defensive-counter-air-operations/) -- Joint Air Power Competence Centre on DCA
8. [BVR Combat Principles and Execution](https://basicsaboutaerodynamicsandavionics.wordpress.com/2026/01/16/important-characteristics-bvr-combat/) -- Detailed BVR engagement phases and outcomes
9. [AIM-120 AMRAAM - Wikipedia](https://en.wikipedia.org/wiki/AIM-120_AMRAAM) -- Historical kill probability data
10. [AIM-120 AMRAAM - USAF Fact Sheet](https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104576/aim-120-amraam/) -- Official specifications
11. [AIM-120 AMRAAM Pk Discussion - DefenceTalk](https://www.defencetalk.com/military/forums/t/aim-120-amraam-pk.12615/) -- Community analysis of operational Pk data
12. [Bas 90 - Wikipedia](https://en.wikipedia.org/wiki/Bas_90) -- Swedish dispersed basing system overview
13. [Saab - Gripen Designed for Dispersed Air Basing](https://www.saab.com/newsroom/stories/2020/august/gripen-designed-for-dispersed-air-basing-system) -- Official Saab description of Gripen/BAS 90 integration
14. [How Sweden's Austere Basing System Influenced the Gripen - FlightGlobal](https://www.flightglobal.com/fixed-wing/how-swedens-austere-basing-system-influenced-the-gripen/139316.article) -- Analysis of BAS 90 influence on Gripen design
15. [Sweden's Air Force Would Have Survived a Soviet Attack - National Interest](https://nationalinterest.org/blog/reboot/not-nato-swedens-air-force-would-have-survived-soviet-attack-no-problem-183339) -- Swedish Cold War air defense analysis
16. [How the Swedish Air Force Would Fight WWIII - National Interest](https://nationalinterest.org/blog/reboot/revealed-how-swedish-air-force-would-fight-world-war-iii-199123) -- Swedish warfighting doctrine analysis
17. [United24 - What Gripen Jets Would Mean for Ukraine](https://united24media.com/interview/airborne-within-five-minutes-what-gripen-jets-would-mean-for-ukraine-a-former-swedish-air-force-pilot-16919) -- Former Swedish Air Force pilot on Gripen operational capabilities
18. [RAND - Air Combat Model Engagement and Attrition Processes](https://www.rand.org/pubs/notes/N3566.html) -- RAND air combat attrition modeling methodology
19. [Air Supremacy - Wikipedia](https://en.wikipedia.org/wiki/Air_supremacy) -- Definitions of air superiority, supremacy, denial, parity
20. [NATO Air Policing: Guarding the Skies](https://ac.nato.int/archive/2025-2/nato-air-policing-guarding-the-skies-when-it-matters-most-) -- 2025 overview of NATO air policing operations and scramble statistics
21. [NATO Intercepts of Russian Aircraft Stable in 2024](https://www.defensenews.com/global/europe/2025/01/13/nato-intercepts-of-russian-aircraft-stable-in-2024-over-prior-year/) -- Scramble statistics showing ~300-570 annual intercepts, none resulting in combat
22. [PACOM Air Intercepts TACAID](https://www.pacom.mil/Portals/55/Documents/Legal/J06%20TACAID%20-%20AIR%20INTERCEPTS%20(FINAL)%20VER%202.pdf) -- U.S. Pacific Command tactical aid on air intercept procedures
23. [Counterair Companion - A Short Guide to Air Superiority](https://media.defense.gov/2017/Dec/29/2001861996/-1/-1/0/T_HOLMES_COUNTERAIR_COMPANION.PDF) -- Historical overview of counterair operations
24. [Swedish Air Force - Wikipedia](https://en.wikipedia.org/wiki/Swedish_Air_Force) -- History and force structure of Flygvapnet
25. [Rethinking Air Superiority - Australian Air Power Centre](https://airpower.airforce.gov.au/blog/rethinking-air-superiority-towards-integrated-framework-modern-airpower) -- Modern framework for understanding air control
26. [WashU - Analytical Modeling of BVR Air Combat](https://www.cse.wustl.edu/~jain/cse567-08/ftp/combat/index.html) -- Academic analysis of BVR combat modeling

## Methodology
Research conducted via web search using queries targeting: NATO air defense procedures, QRA operations, Swedish air defense doctrine, BAS 90, BVR combat mechanics, missile kill probabilities, rules of engagement, defensive counter air doctrine, asymmetric air defense, and air warfare attrition modeling. Sources prioritized: NATO official publications, USAF doctrine documents, defense analysis outlets (National Interest, CEPA, FlightGlobal), manufacturer documentation (Saab), RAND Corporation studies, and academic/military analysis. Cross-referenced multiple sources for key data points (missile Pk, turnaround times, scramble statistics).

## Confidence Assessment
- **Overall confidence**: MEDIUM
- **High confidence**: QRA procedures, weapons control orders, BAS 90 system description, Gripen turnaround times (well-documented in official sources)
- **Medium confidence**: BVR engagement sequence, missile Pk ranges, escalation ladder (based on open-source analysis, some classified details unavailable)
- **Lower confidence**: Specific deterrence quantification, exact force exchange ratios (limited publicly available data, much is classified or scenario-dependent)
- **Recommendations**: Sensitivity analysis on missile Pk values (run simulations with Pk ranging from 0.3 to 0.8). Validate engagement outcome model against known historical air campaigns. Consider consulting with military advisors for ROE modeling accuracy.

## Applied In
- `backend/src/domain/entities/aircraft.py` -- Should inform engagement outcome model refactoring
- `backend/src/domain/services/` -- Should inform combat resolution service redesign
- `Development/DOMAIN.md` -- CombatResult model should be expanded per recommendations
- `scenario/strategies/` -- Strategy design should incorporate ROE, reserve management, CAP zones
- `research/combat_probabilities.md` -- Cross-reference: missile Pk data refines probability estimates

## Last Updated
2026-04-17
