# Combat Engagement Probabilities

## Question
What are realistic combat engagement probabilities between drone swarms, UAVs, manned combat aircraft, and bomber aircraft?

## Summary
Initial probability estimates based on general aviation capabilities and combat role analysis. Confidence: LOW - these are working estimates for the simulation prototype, not validated military data.

## Findings

### Manned Combat Aircraft vs Others
- Combat planes (e.g., F-16, Gripen) are purpose-built for air superiority
- Strong advantage over all non-fighter types
- 50/50 against peer fighters (skill/position dependent)

### Drone Swarms
- Effective through numbers and saturation
- Can overwhelm individual UAVs and bombers
- Vulnerable to high-speed combat aircraft with advanced weapons

### UAVs
- Medium capability, good surveillance but limited air-to-air
- Outclassed by manned fighters in dogfights
- Moderate advantage over bombers due to agility

### Bombers
- Optimized for ground attack, not air combat
- Vulnerable to all fighter types
- Can defend against other bombers (mutual vulnerability)

## Sources
1. General aviation performance characteristics - publicly available specifications
2. Combat role analysis based on aircraft design purposes

## Methodology
Estimates derived from relative capabilities of aircraft classes. No classified data used.

## Confidence Assessment
- **Overall confidence**: LOW
- **Limitations**: No real engagement data. Probabilities are symmetric approximations.
- **Recommendations**: Consult with military advisors. Run sensitivity analysis on these values.

## Applied In
- `backend/src/domain/entities/aircraft.py` - AIRCRAFT_SPECS combat_matchups
- `Development/DOMAIN.md` - Combat Matchup Probabilities table
- `scenario/boreal_passage.json` - combat_matchups config

## Last Updated
2026-04-17
