const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// ====== Types ======
export interface SimulationMetrics {
  total_civilian_casualties: number;
  time_to_first_casualty: number | null;
  aircraft_lost: number;
  aircraft_remaining: number;
  bases_lost: number;
  bases_remaining: number;
  cities_defended: number;
  capital_survived: boolean;
  total_ticks: number;
  fuel_efficiency: number;
  engagement_win_rate: number;
  response_time_avg: number;
  total_engagements: number;
  sorties_flown: number;
}

export interface SimulationResponse {
  simulation_id: string;
  status: string;
  outcome: string | null;
  total_ticks: number | null;
  metrics: SimulationMetrics | null;
}

export interface Strategy { id: string; name: string; description: string; }
export interface Scenario { id: string; name: string; theater_width_km: number; theater_height_km: number; }

export interface AttackTarget {
  type: string;
  id?: string | null;
  x_km?: number | null;
  y_km?: number | null;
}

export interface AttackAction {
  tick: number;
  type: string;
  aircraft_type: string;
  count: number;
  from_base?: string | null;
  target?: AttackTarget | null;
}

export interface AttackPlan {
  id: string;
  name: string;
  source: string;
  description: string;
  created_at: string;
  tags: string[];
  actions: AttackAction[];
}

export interface AttackPlanSummary {
  total: number;
  by_source: Record<string, number>;
}

export interface TickData {
  tick: number;
  aircraft: Array<{
    id: string; type: string; side: string;
    position: [number, number]; state: string; fuel: number; ammo: number;
  }>;
  bases: Array<{
    id: string; name: string; side: string; position: [number, number];
    operational: boolean; fuel_storage: number; aircraft_count: number; capacity: number;
  }>;
  cities: Array<{
    id: string; name: string; side: string; position: [number, number];
    damage: number; casualties: number; is_capital?: boolean; population?: number;
  }>;
  battles: Array<Record<string, unknown>>;
  decisions: Array<Record<string, unknown>>;
  events: string[];
}

export interface ReplayData {
  simulation_id: string; scenario: string; strategy: string; enemy_strategy: string;
  seed: number; side: string; outcome: string;
  total_ticks: number; tick_minutes: number;
  ticks: TickData[];
  metrics: SimulationMetrics | null;
}

export interface EvaluateResponse {
  simulation_id: string;
  outcome: string;
  total_ticks: number;
  attack_plan: AttackPlan;
  metrics: SimulationMetrics | null;
}

export interface TrainingPlanResult {
  attack_plan_id: string;
  simulations: number;
  wins: number;
  losses: number;
  timeouts: number;
  defense_success_rate: number;
  avg_casualties: number;
  avg_aircraft_lost: number;
}

export interface TrainingResponse {
  batch_id: string;
  total_simulations: number;
  total_wins: number;
  overall_defense_rate: number;
  by_attack_plan: TrainingPlanResult[];
}

// ====== Fetch wrapper ======
async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${body || res.statusText}`);
  }
  return res.json();
}

// ====== Scenarios & Strategies ======
export const getStrategies = () => fetchAPI<{ strategies: Strategy[] }>("/strategies");
export const getScenarios = () => fetchAPI<{ scenarios: Scenario[] }>("/scenarios");

// ====== Attack Plans ======
export const listAttackPlans = (source?: string) =>
  fetchAPI<{ plans: AttackPlan[]; total: number }>(
    source ? `/attack-plans?source=${source}` : "/attack-plans");

export const getAttackPlanSummary = () => fetchAPI<AttackPlanSummary>("/attack-plans/summary");

export const getAttackPlan = (id: string) => fetchAPI<AttackPlan>(`/attack-plans/${id}`);

export const createCustomPlan = (params: {
  name: string;
  description?: string;
  tags?: string[];
  actions: AttackAction[];
}) => fetchAPI<AttackPlan>("/attack-plans", {
  method: "POST",
  body: JSON.stringify(params),
});

export const generateRandomPlans = (count: number, base_seed: number = 1) =>
  fetchAPI<{ generated: number; plans: AttackPlan[] }>("/attack-plans/generate-random", {
    method: "POST",
    body: JSON.stringify({ count, base_seed }),
  });

export const generateAIPlan = (prompt: string) =>
  fetchAPI<AttackPlan>("/attack-plans/generate-ai", {
    method: "POST",
    body: JSON.stringify({ prompt }),
  });

export const deleteAttackPlan = (id: string) =>
  fetchAPI<{ deleted: boolean }>(`/attack-plans/${id}`, { method: "DELETE" });

// ====== Evaluate / Training ======
export const evaluateAttackPlan = (params: {
  attack_plan_id: string;
  strategy_id?: string;
  scenario_id?: string;
  side?: string;
  seed?: number;
}) => fetchAPI<EvaluateResponse>("/training/evaluate", {
  method: "POST",
  body: JSON.stringify({
    strategy_id: "defensive_v1",
    scenario_id: "boreal_passage_v1",
    side: "north",
    seed: 42,
    ...params,
  }),
});

export const runTraining = (params: {
  attack_plan_ids: string[];
  strategy_id?: string;
  scenario_id?: string;
  side?: string;
  seeds_per_plan?: number;
  seed_start?: number;
}) => fetchAPI<TrainingResponse>("/training/run", {
  method: "POST",
  body: JSON.stringify({
    strategy_id: "defensive_v1",
    scenario_id: "boreal_passage_v1",
    side: "north",
    seeds_per_plan: 5,
    seed_start: 1,
    ...params,
  }),
});

// ====== Simulation replay ======
export const getReplay = (id: string) => fetchAPI<ReplayData>(`/simulations/${id}/replay`);
