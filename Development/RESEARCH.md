# Research Workflow

## Purpose

This project requires accurate data for aircraft stats, combat probabilities, and tactical doctrine. All AI-assisted research is documented in the `research/` folder so findings are reusable, traceable, and reviewable.

## When to Do Research

Do research BEFORE coding when you need:
- Aircraft performance stats (speed, fuel, range, payload)
- Combat probability estimates between aircraft types
- Tactical doctrine or historical engagement patterns
- Base capacity and logistics data
- City defense or damage modeling parameters
- Any numerical value that affects simulation accuracy

## Research Folder Structure

```
research/
├── combat_probabilities.md        # Matchup win rates between aircraft types
├── aircraft_performance.md        # Speed, fuel, range, payload data
├── base_logistics.md              # Refueling times, capacity, supply chains
├── tactical_doctrine.md           # Air defense strategies, engagement patterns
├── city_damage_modeling.md        # How air attacks affect urban areas
└── [topic].md                     # Additional research as needed
```

## Research File Template

Every research file MUST follow this format:

```markdown
# [Research Topic]

## Question
What specific question are we trying to answer?

## Summary
2-3 sentence summary of findings. Include confidence level: HIGH / MEDIUM / LOW.

## Findings

### [Finding 1]
- Data point or conclusion
- Supporting evidence

### [Finding 2]
- Data point or conclusion
- Supporting evidence

## Sources
1. [Source Name](URL) — Brief description of what this source provided
2. [Source Name](URL) — Brief description
3. ...

## Methodology
How was this research conducted? What search queries were used?
What AI tools were used and what were their limitations?

## Confidence Assessment
- **Overall confidence**: HIGH / MEDIUM / LOW
- **Limitations**: What aspects are uncertain or assumed?
- **Recommendations**: What should be validated further?

## Applied In
- `backend/src/domain/entities/aircraft.py` — Used for [specific stat]
- `Development/DOMAIN.md` — Referenced in [specific table]
- `scenario/boreal_passage.json` — Used for [specific config value]

## Last Updated
YYYY-MM-DD
```

## Research Rules

### For AI Coding Agents

When you need a numerical value for the simulation and it's not already documented:

1. **Check `research/` first.** The answer may already exist.
2. **If not found, create a research file.** Follow the template above.
3. **Search for real-world data.** Use web search to find authoritative sources.
4. **Cite your sources.** Every data point needs a source URL or reference.
5. **State your confidence level.** Be honest about uncertainty.
6. **Document your methodology.** What did you search for? What did you find?
7. **Cross-reference findings.** Multiple sources increase confidence.
8. **Note the "Applied In" section.** Link back to where the data is used in code.

### Confidence Levels

| Level | Meaning | When to Use |
|---|---|---|
| **HIGH** | Multiple authoritative sources agree | Published military specs, well-documented systems |
| **MEDIUM** | Some sources, reasonable extrapolation | Mix of sources, some estimation needed |
| **LOW** | Limited data, significant estimation | Novel combinations, classified data gaps, rough estimates |

### What Counts as a Good Source

**Preferred:**
- Military specification documents
- Defense industry publications (Jane's, Aviation Week)
- Academic papers on air combat modeling
- Government reports (DoD, NATO)
- Manufacturer specifications

**Acceptable:**
- Wikipedia (with cross-referencing)
- Military enthusiast sites (with caveats)
- Historical engagement data
- Simulation modeling literature

**Not Sufficient Alone:**
- AI-generated estimates without sourcing
- Single unverified blog posts
- Fictional or game-based data

### Handling Classified or Unavailable Data

Much real military data is classified. When exact data isn't available:

1. **Use publicly available approximations.** Document they are approximations.
2. **Use relative comparisons.** "Combat plane is ~3x faster than drone swarm" may be more useful than exact speeds.
3. **Create parameterized ranges.** Instead of one value, define min/median/max and note the simulation default.
4. **Mark confidence as LOW** and explain what's missing.
5. **Make it easy to update.** When better data becomes available, the research file and code should be straightforward to update.

## Updating Research

When you find better data:

1. Update the research file with new findings.
2. Add the new source to the Sources section.
3. Update the confidence assessment.
4. Update the "Last Updated" date.
5. Update any code or config that references the old data.
6. Update `Development/DOMAIN.md` tables if affected.

## Requesting Research

If you're a team member and need research done:

1. Create a research file with just the **Question** section filled in.
2. The next agent or team member picks it up, does the research, and fills in the rest.
3. This prevents duplicate research and ensures questions are captured even when you're focused on coding.
