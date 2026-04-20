# Knowledge Base — Three-Tier Data Model

The core asset of the system. Specifies exactly how simulation results become retrievable, reusable intelligence for the LLM commander.

## Three tiers

### Tier 1 — `match_results` (raw)
One row per unique (attack_plan × defense_playbook × settings) triple. Append-only.

### Tier 2 — `attack_patterns` (aggregated index)
Fuzzy groupings of attack plans by tactical characteristics. Points at the current best defense.

### Tier 3 — `doctrine_entries` (abstract principles)
LLM-synthesized lessons with trigger conditions and supporting evidence.

## Complete schema

### Settings (the root — everything scopes to it)

```sql
CREATE TABLE settings (
  settings_id TEXT PRIMARY KEY,           -- sha256 of canonical serialization
  name TEXT NOT NULL,                     -- user label
  scenario_json TEXT NOT NULL,            -- map, bases, cities
  defender_resources_json TEXT NOT NULL,  -- {combat_plane: 30, bomber: 3, ...}
  attacker_resources_json TEXT NOT NULL,
  engagement_params_json TEXT NOT NULL,   -- Pk, ranges, tick size
  tick_minutes REAL NOT NULL,
  max_ticks INTEGER NOT NULL,
  is_active BOOLEAN DEFAULT 0,
  created_at TIMESTAMP NOT NULL,
  last_used_at TIMESTAMP NOT NULL,
  notes TEXT
);
```

`settings_id = sha256(canonical_json(serialized_content))`. Changing any field produces a new row; re-entering identical settings reuses the existing row.

Only one row has `is_active = 1` at any time.

### Attack Plans (the scripted adversary actions)

```sql
CREATE TABLE attack_plans (
  plan_id TEXT PRIMARY KEY,               -- uuid
  settings_id TEXT NOT NULL REFERENCES settings(settings_id),
  pattern_id TEXT REFERENCES attack_patterns(pattern_id),  -- fuzzy group
  name TEXT NOT NULL,
  description TEXT,
  source TEXT NOT NULL,                   -- 'ai_generated' | 'random' | 'custom'
  actions_json TEXT NOT NULL,             -- timeline of actions
  tags_json TEXT,                         -- ['multi_wave', 'capital_focus']
  created_at TIMESTAMP NOT NULL
);
CREATE INDEX idx_plan_settings ON attack_plans(settings_id);
CREATE INDEX idx_plan_pattern ON attack_plans(pattern_id);
```

### Attack Patterns (fuzzy tactical groupings)

```sql
CREATE TABLE attack_patterns (
  pattern_id TEXT PRIMARY KEY,            -- sha256 of canonical features
  settings_id TEXT NOT NULL REFERENCES settings(settings_id),
  canonical_description TEXT NOT NULL,    -- LLM-written summary
  feature_tags_json TEXT NOT NULL,        -- ['multi_wave', 'bomber_heavy', 'east_axis']
  force_composition_json TEXT NOT NULL,   -- {bombers: 4, drones: 8, ...}
  target_profile TEXT NOT NULL,           -- 'capital_primary' | 'city_distributed' | ...
  wave_count INTEGER,
  first_seen_at TIMESTAMP NOT NULL,
  total_plans_count INTEGER DEFAULT 0,
  total_matches_count INTEGER DEFAULT 0,
  best_defense_playbook_id TEXT,          -- current champion (nullable)
  best_fitness_score REAL,
  best_match_id TEXT                      -- pointer to winning match row
);
```

Multiple attack plans can share one pattern. Pattern features are extracted by the `PatternExtractor` service (rule-based initial version, LLM-augmented later).

### Defense Playbooks

```sql
CREATE TABLE defense_playbooks (
  playbook_id TEXT PRIMARY KEY,           -- uuid
  settings_id TEXT NOT NULL REFERENCES settings(settings_id),
  name TEXT NOT NULL,
  description TEXT,
  source TEXT NOT NULL,                   -- 'ai_generated' | 'custom' | 'coached'
  standing_orders_json TEXT NOT NULL,
  triggers_json TEXT NOT NULL,
  constraints_json TEXT NOT NULL,
  doctrine_notes TEXT,
  parent_playbook_id TEXT REFERENCES defense_playbooks(playbook_id),  -- lineage
  created_at TIMESTAMP NOT NULL
);
CREATE INDEX idx_playbook_settings ON defense_playbooks(settings_id);
```

### Match Results (the raw data — NEVER DELETED)

```sql
CREATE TABLE match_results (
  match_id TEXT PRIMARY KEY,              -- sha256(attack_plan_id + playbook_id + settings_id)
  settings_id TEXT NOT NULL REFERENCES settings(settings_id),
  attack_plan_id TEXT NOT NULL REFERENCES attack_plans(plan_id),
  pattern_id TEXT NOT NULL REFERENCES attack_patterns(pattern_id),
  defense_playbook_id TEXT NOT NULL REFERENCES defense_playbooks(playbook_id),
  outcome TEXT NOT NULL,                  -- 'WIN' | 'LOSS' | 'TIMEOUT'
  fitness_score REAL NOT NULL,
  metrics_json TEXT NOT NULL,             -- full 14 KPIs
  event_log_json TEXT NOT NULL,           -- full simulation replay
  ai_analysis_text TEXT,                  -- LLM's narrative of what happened
  ai_takeaways_json TEXT,                 -- [{principle, confidence, tags, refs_ticks}]
  created_at TIMESTAMP NOT NULL,
  analysis_completed_at TIMESTAMP
);
CREATE INDEX idx_match_by_plan ON match_results(attack_plan_id, fitness_score DESC);
CREATE INDEX idx_match_by_pattern ON match_results(pattern_id, fitness_score DESC);
CREATE INDEX idx_match_by_playbook ON match_results(defense_playbook_id);
CREATE INDEX idx_match_by_settings_fitness ON match_results(settings_id, fitness_score DESC);
```

`match_id` is deterministic. Re-running the same triple updates the same row via `INSERT OR REPLACE` — no duplicates possible.

### Doctrine Entries (the learned wisdom)

```sql
CREATE TABLE doctrine_entries (
  entry_id TEXT PRIMARY KEY,              -- uuid
  settings_id TEXT NOT NULL REFERENCES settings(settings_id),
  category TEXT NOT NULL,                 -- 'multi_wave_defense' | 'bomber_counter' | ...
  principle_text TEXT NOT NULL,           -- the lesson in plain English
  trigger_conditions_json TEXT,           -- when this applies: tags, force ratios, etc.
  supporting_match_ids_json TEXT,         -- [match_id, match_id, ...]
  confidence_score REAL,                  -- 0.0 to 1.0 based on evidence
  version INTEGER NOT NULL DEFAULT 1,
  parent_entry_id TEXT REFERENCES doctrine_entries(entry_id),  -- versioning
  is_active BOOLEAN NOT NULL DEFAULT 1,
  human_edited BOOLEAN NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);
CREATE INDEX idx_doctrine_settings_active ON doctrine_entries(settings_id, is_active);
CREATE INDEX idx_doctrine_category ON doctrine_entries(settings_id, category, is_active);
```

### Evaluation Conversations (audit trail for Live Commander sessions)

```sql
CREATE TABLE evaluation_conversations (
  eval_id TEXT PRIMARY KEY,               -- uuid
  match_id TEXT NOT NULL REFERENCES match_results(match_id),
  messages_json TEXT NOT NULL,            -- full message history with tick refs
  commands_issued_json TEXT,              -- extracted LLM commands per tick
  total_input_tokens INTEGER,
  total_output_tokens INTEGER,
  cached_tokens INTEGER,
  cost_usd REAL,
  started_at TIMESTAMP NOT NULL,
  ended_at TIMESTAMP
);
```

## The three identification schemes

| ID | Formation | Purpose |
|---|---|---|
| `settings_id` | `sha256(canonical_json)` | Deduplication + scoping |
| `match_id` | `sha256(attack_plan_id + playbook_id + settings_id)` | Uniqueness per matchup, enables `INSERT OR REPLACE` |
| `pattern_id` | `sha256(canonical_features)` | Fuzzy grouping of tactically similar attacks |
| `attack_plan_id` / `playbook_id` / `entry_id` / `eval_id` | uuid4 | Stable random identifier |

## Flow diagrams

### Writing a match result (how data gets stored)

```
1. Training orchestrator picks (attack_plan, playbook) pair
2. Simulation runs deterministically, produces outcome + metrics + event_log
3. Compute match_id = sha256(attack_plan_id + playbook_id + settings_id)
4. INSERT OR REPLACE INTO match_results (...)  -- idempotent
5. LLM analyzes the match:
   - Input: attack_plan, playbook, event_log highlights, metrics
   - Output: ai_analysis_text + ai_takeaways_json (structured lessons)
6. UPDATE match_results SET ai_analysis_* WHERE match_id = ?
7. Update attack_patterns:
   - total_matches_count += 1
   - if fitness_score > best_fitness_score:
       UPDATE SET best_defense_playbook_id, best_fitness_score, best_match_id
8. Evaluate doctrine impact:
   - LLM reads takeaways + current doctrine entries in this category
   - Decides: reinforce existing (increment confidence), create new entry, 
     or version existing entry (insert row with parent_entry_id)
```

### Reading for LLM context (how data informs decisions)

For **generating a new defense playbook** against a specific attack:

```
1. Get attack's pattern_id
2. Retrieve top-K match_results WHERE pattern_id = ? ORDER BY fitness_score DESC LIMIT K
   (these are the best defenses against similar attacks)
3. Retrieve active doctrine entries WHERE settings_id = ? AND is_active
4. Compose LLM input:
   - Current settings
   - Attack plan to defend against
   - Top-K match summaries (attack description, what worked, takeaways)
   - Full active doctrine
5. LLM produces new playbook
```

For **live commander per tick** (see [LIVE_COMMANDER.md](LIVE_COMMANDER.md)):

```
Initial (tick 0):
  Load active doctrine + top-5 pattern matches → cached context
  
Per tick:
  Send only delta + current tick state changes
  LLM reconstructs picture from cached context + prior conversation
```

## Handling the tricky cases

### Case A: Two defenses tried against same attack, one better

Both rows exist in `match_results`. `attack_patterns.best_defense_playbook_id` points to the winner. Nothing deleted.

```sql
-- See all defenses tried against this attack, ranked
SELECT m.*, p.name AS playbook_name
FROM match_results m
JOIN defense_playbooks p ON m.defense_playbook_id = p.playbook_id
WHERE m.attack_plan_id = ?
ORDER BY m.fitness_score DESC;

-- Current best
SELECT * FROM attack_patterns WHERE pattern_id = (
  SELECT pattern_id FROM attack_plans WHERE plan_id = ?
);
```

### Case B: New match result contradicts existing doctrine

LLM decision during doctrine update step:

1. If new takeaway has higher confidence than existing → version existing (new row with `parent_entry_id`, old set `is_active=0`)
2. If new takeaway agrees → increment `confidence_score` on existing, append to `supporting_match_ids_json`
3. If new takeaway is orthogonal → create new entry in same/different category

Human can override any automatic versioning via UI.

### Case C: Human disagrees with doctrine entry

Human edits entry via UI → sets `human_edited=1`. Coach loop respects this flag:
- Won't auto-version this entry without explicit confirmation
- Uses human version as ground truth in future LLM prompts

### Case D: Settings changed mid-training

Not possible — settings is immutable once created. To "change settings," user creates a new settings row. All subsequent training flows to that. Prior settings' data remains queryable.

### Case E: Delete a bad attack plan

`DELETE FROM attack_plans WHERE plan_id = ?` — match_results referencing it are retained (historical record) but pattern statistics are recomputed. UI shows deleted plan's matches as "orphaned" but still readable.

### Case F: Same attack plan runs against new playbook later

`match_id` is deterministic. If that triple was already run, `INSERT OR REPLACE` updates the row with latest result. Useful when re-running with improved engagement engine for example.

## LLM retrieval patterns

When the LLM needs context, we use BM25 over text fields + structured filters:

```python
# "Find cases most similar to this attack pattern"
candidates = (
    session.query(MatchResult)
    .filter(MatchResult.settings_id == current_settings_id)
    .filter(MatchResult.pattern_id == target_pattern_id)
    .order_by(MatchResult.fitness_score.desc())
    .limit(5)
    .all()
)

# "Find doctrine relevant to this situation"
relevant_doctrine = (
    session.query(DoctrineEntry)
    .filter(DoctrineEntry.settings_id == current_settings_id)
    .filter(DoctrineEntry.is_active == True)
    .filter(DoctrineEntry.category.in_(relevant_categories))
    .order_by(DoctrineEntry.confidence_score.desc())
    .all()
)
```

Upgrade path: replace BM25 with sentence embeddings later if retrieval quality matters (not needed for hackathon).

## Size estimates

For a 1000-match training run:

| Table | Rows | Avg size | Storage |
|---|---|---|---|
| settings | 5-10 | 5 KB | ~50 KB |
| attack_plans | 100-500 | 2 KB | ~1 MB |
| attack_patterns | 20-50 | 1 KB | ~50 KB |
| defense_playbooks | 50-200 | 3 KB | ~600 KB |
| match_results | 1000 | 50 KB (incl. event log) | **~50 MB** |
| doctrine_entries | 20-100 | 1 KB | ~100 KB |
| evaluation_conversations | 10-50 | 30 KB | ~1.5 MB |

SQLite handles this trivially. Event logs dominate storage — optionally gzip them in the column for 5-10x reduction.
