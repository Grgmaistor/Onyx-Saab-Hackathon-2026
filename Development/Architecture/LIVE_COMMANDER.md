# Live Commander — Real-Time LLM Decision System

The LLM commander runs during **Evaluation mode** and makes decisions each tick. This document specifies how we keep the LLM "aware" of evaluation context without burning tokens.

## The core constraint

Anthropic's Messages API is **stateless**. Every call must include the full conversation we want the LLM to "remember." There is no server-side session state.

Goal: make it *feel* like a persistent streaming conversation where the LLM remembers everything, while keeping cost and latency acceptable.

## The technique: cached conversation history + delta messages + periodic compaction

Three mechanisms combined:

### 1. Prompt caching

Anthropic supports marking prompt segments as cacheable. Cached tokens cost **10% of normal input price** after first request, with a 5-minute TTL (refreshed on each access).

For an evaluation session, these are cached:
- System prompt (~2k tokens) — the role, output format, decision vocabulary
- Settings context (~3k tokens) — map, resources, aircraft specs, doctrine excerpts
- Initial playbook (~1k tokens) — what the defense plan is
- Session memory (~1k tokens, rebuilt every 20 ticks) — compacted history

Only the **current tick delta** is fresh, per call:
- Per-tick delta (~100-300 tokens) — what changed since last tick

### 2. Delta messages (not full-state dumps)

At tick 0, the commander receives the full state once. Each subsequent tick, it receives only changes:

```json
{
  "tick": 45,
  "delta": {
    "friendly_aircraft_state_changes": [
      {"id": "n-cp-02", "change": "launched", "from_base": "northern_vanguard"},
      {"id": "n-cp-07", "change": "fuel_low", "fuel_fraction": 0.22}
    ],
    "enemy_aircraft_new_detections": [
      {"id": "s-bo-04", "type": "bomber", "position": [920, 450], "bearing_toward": "arktholm"}
    ],
    "engagements_this_tick": [
      {"attacker": "n-cp-03", "defender": "s-uav-01", "outcome": "defender_destroyed"}
    ],
    "asset_health_changes": {},
    "playbook_triggers_fired": ["intercept_bomber_approach"]
  },
  "unchanged_summary": "40 friendly airborne, 12 enemy airborne, 0 cities damaged"
}
```

Total: ~200 tokens per tick. The LLM reconstructs "what's happening" from the delta + its own prior responses in the conversation history.

### 3. Periodic compaction

The conversation grows each tick. After K=25 ticks, we compact:

- Ask the LLM: *"Summarize the evaluation so far in ~200 tokens: key decisions you made, enemy intent as you understand it, current tactical state."*
- Store the response as the new **session memory**.
- Replace messages 1..K with this single memory message.
- Mark the new memory as cacheable.
- Continue tick-by-tick from there.

Without compaction, a 300-tick eval accumulates ~60k tokens of history — expensive. With compaction every 25 ticks, context stays bounded at ~8-10k tokens.

## Token cost model

Per tick breakdown (after caches are warm):

| Segment | Tokens | Cached? | Cost per tick |
|---|---|---|---|
| System prompt | 2,000 | yes | 2k × $0.30/M = $0.0006 |
| Settings context | 3,000 | yes | 3k × $0.30/M = $0.0009 |
| Initial playbook | 1,000 | yes | $0.0003 |
| Session memory (cached after creation) | 1,000 | yes | $0.0003 |
| Recent tick history (rolling window) | 3,000 | mostly cached | $0.001 |
| Current tick delta | 200 | no | 200 × $3.00/M = $0.0006 |
| Output (usually "continue") | 20 | n/a | 20 × $15/M = $0.0003 |
| **Total per tick** | | | **~$0.004** |

For a 300-tick evaluation: **~$1.20 per evaluation**.
For a 100-tick short evaluation: **~$0.40**.

First tick of a fresh session is more expensive (~$0.05) because caches must be built. After that, every subsequent tick is cheap.

## Conversation structure

```
Message 0 (cached, sticky):
  role: system
  content: [
    {type: text, text: "<role prompt>", cache_control: {type: ephemeral}},
    {type: text, text: "<settings and map>", cache_control: {type: ephemeral}},
    {type: text, text: "<doctrine excerpts>", cache_control: {type: ephemeral}},
    {type: text, text: "<initial playbook>", cache_control: {type: ephemeral}}
  ]

Message 1 (cached after creation, rebuilt every 25 ticks):
  role: user  
  content: "<session memory so far>" with cache_control

Messages 2..N (rolling window, last 24 ticks):
  role: user / assistant alternating
  - user: tick delta
  - assistant: decision ("continue" or action)

Message N+1 (current tick, fresh):
  role: user
  content: "<tick delta>"
```

## Streaming responses

Claude supports **streaming** — response tokens arrive as generated. We use this so "continue" answers are processed in ~200ms instead of waiting for full response.

Client-side: as soon as we parse a valid `{"action": "continue"}` JSON, we apply it and move to next tick without waiting for additional (absent) tokens. If the response contains an action payload, we wait for full JSON before applying.

## Decision response schema

The LLM must respond with JSON matching one of these shapes:

```jsonc
// Most common (free-ish, ~20 output tokens)
{"action": "continue"}

// Issue a direct command  
{
  "action": "command",
  "rationale": "enemy bomber inbound to arktholm, 2-ship CAP not sufficient",
  "commands": [
    {"type": "scramble", "count": 3, "aircraft_type": "combat_plane",
     "from_base": "highridge_command", "intercept_target": "s-bo-04"}
  ]
}

// Update the playbook (rules change for remainder of evaluation)
{
  "action": "update_playbook",
  "rationale": "attack pattern revealed as multi-wave, need to preserve reserves",
  "patch": {
    "constraints": {"reserve_fraction": 0.45},
    "add_triggers": [...],
    "remove_triggers": ["intercept_drone_west"]
  }
}

// Request human attention (rare)
{
  "action": "escalate",
  "severity": "high",
  "rationale": "capital damage threshold exceeded, current playbook cannot respond"
}
```

The playbook executor (pure code) handles standing orders and most triggers. The LLM layers on top, only intervening with `command` or `update_playbook` when state warrants.

## Latency budget

Target: ~500ms per tick. Breakdown:

| Phase | Target | How |
|---|---|---|
| Compute tick delta locally | 10ms | Compare current state to prior |
| LLM call round-trip (cached heavy, output short) | 300-400ms | Streaming short response |
| Parse + apply decision | 10ms | JSON validation |
| Advance simulation one tick | 80ms | Existing simulation code |
| **Per-tick total** | **~500ms** | |

For a 300-tick evaluation: ~2.5 min wall-clock. Watchable at 2x playback.

For faster playback, the UI can buffer several ticks ahead while user watches.

## Error handling

The LLM may:
- Return invalid JSON → we retry once with a repair prompt, else default to `{"action": "continue"}` and log warning
- Return a command for a non-existent aircraft → playbook executor ignores silently, logs
- Time out (>3s) → default to `{"action": "continue"}`, tick proceeds
- Claude API returns error (5xx, rate limit) → retry with exponential backoff; if all retries fail, fall back to deterministic playbook execution for remainder of evaluation

The simulation should **never fail** because of an LLM issue. Graceful degradation to playbook-only execution is always available.

## Integration with playbook executor

Order of operations per tick:

```
1. Compute state delta since last tick
2. Run Layer 2 pilot reflexes → some aircraft take self-directed actions
3. Compute playbook executor output (standing orders + triggers) for remaining aircraft
4. Call LLM with delta → may issue additional commands or update playbook
5. Apply any LLM-issued commands (override/supplement playbook output)
6. Advance simulation physics (move, engage, damage, service)
7. Record tick in event log (includes the LLM's response)
```

The LLM is an **additive layer** on top of the deterministic playbook — it doesn't replace it. Playbook handles the boring 90%; LLM intervenes when things are interesting.

## What the LLM is NOT doing

To keep scope clear:

- **Not** controlling individual aircraft tactics (turn, fire, evade) — that's the engagement engine + pilot reflexes
- **Not** computing paths or trajectories — that's movement code
- **Not** deciding base-level logistics (fuel, rearm) — that's fuel manager
- **Not** validating its own output — the playbook executor is the source of truth for executable commands

The LLM is the **strategic overseer**, not the tactical controller.

## Training mode vs Live Evaluation

To be unambiguous: **there is no LLM in the simulation loop during training**. Training produces playbooks and analyzes results; the training simulations execute those playbooks deterministically with no LLM per-tick.

Live Commander with per-tick LLM calls is **only used in Evaluation mode** — a single interactive run where the user watches and the LLM reacts in real time.

| Mode | LLM calls during sim | Cost per run |
|---|---|---|
| Training simulation | 0 | $0 (pre-generated playbook) |
| Live Evaluation | 1 per tick (~300) | ~$1.20 |

The $1.20 cost is absorbable for demos and real-world decision support. The zero-cost training is what makes the knowledge base economical to grow.

## Conversation persistence for audit

After an evaluation, the full conversation is stored:

```
evaluation_conversations table:
  eval_id PK
  match_id FK → match_results
  messages_json    -- full conversation history
  total_input_tokens
  total_output_tokens
  cost_usd
  started_at, ended_at
```

This gives us:
- **Reviewability** — officer can read exactly what the LLM decided and why
- **Debugging** — we can replay an eval with a different model or prompt
- **Training data** — if we ever do fine-tuning, these are the golden examples
