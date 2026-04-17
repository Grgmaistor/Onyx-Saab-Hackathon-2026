const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

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

export interface BatchResponse {
  batch_id: string;
  total_simulations: number;
  status: string;
}

export interface StrategyAgg {
  strategy_id: string;
  simulations: number;
  wins: number;
  losses: number;
  timeouts: number;
  win_rate: number;
  avg_civilian_casualties: number;
  avg_aircraft_lost: number;
  avg_engagement_win_rate: number;
  capital_survival_rate: number;
}

export interface BatchResults {
  batch_id: string;
  status: string;
  total: number;
  by_strategy: StrategyAgg[];
  best_strategy: string | null;
}

export interface Strategy {
  id: string;
  name: string;
  description: string;
}

export interface Scenario {
  id: string;
  name: string;
  theater_width_km: number;
  theater_height_km: number;
}

export interface TickData {
  tick: number;
  aircraft: Array<{
    id: string;
    type: string;
    side: string;
    position: [number, number];
    state: string;
    fuel: number;
    ammo: number;
  }>;
  bases: Array<{
    id: string;
    name: string;
    side: string;
    position: [number, number];
    operational: boolean;
    fuel_storage: number;
    aircraft_count: number;
    capacity: number;
  }>;
  cities: Array<{
    id: string;
    name: string;
    side: string;
    position: [number, number];
    damage: number;
    casualties: number;
    is_capital?: boolean;
    population?: number;
  }>;
  battles: Array<Record<string, unknown>>;
  decisions: Array<Record<string, unknown>>;
  events: string[];
}

export interface ReplayData {
  simulation_id: string;
  scenario: string;
  strategy: string;
  enemy_strategy: string;
  seed: number;
  side: string;
  outcome: string;
  total_ticks: number;
  tick_minutes: number;
  ticks: TickData[];
  metrics: SimulationMetrics | null;
}

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function getStrategies(): Promise<{ strategies: Strategy[] }> {
  return fetchAPI("/strategies");
}

export async function getScenarios(): Promise<{ scenarios: Scenario[] }> {
  return fetchAPI("/scenarios");
}

export async function runSimulation(params: {
  scenario_id: string;
  strategy_id: string;
  enemy_strategy_id: string;
  side: string;
  seed: number;
}): Promise<SimulationResponse> {
  return fetchAPI("/simulations", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export async function runBatch(params: {
  scenario_id: string;
  side: string;
  runs: Array<{
    strategy_id: string;
    enemy_strategy_id: string;
    seed_start: number;
    seed_count: number;
  }>;
}): Promise<BatchResponse> {
  return fetchAPI("/simulations/batch", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export async function getSimulation(id: string): Promise<SimulationResponse> {
  return fetchAPI(`/simulations/${id}`);
}

export async function getReplay(id: string): Promise<ReplayData> {
  return fetchAPI(`/simulations/${id}/replay`);
}

export async function getBatchResults(batchId: string): Promise<BatchResults> {
  return fetchAPI(`/batches/${batchId}/results`);
}
