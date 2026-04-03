export type SummaryLabel =
  | "official_update"
  | "race_result"
  | "analysis"
  | "prediction";

export type EditorialStatus = "draft" | "review_required" | "approved";

export interface Source {
  id: string;
  name: string;
  kind: "official" | "team" | "media";
  reliability_tier: string;
  base_url: string;
}

export interface Entity {
  id: string;
  name: string;
  kind: string;
  slug: string;
}

export interface DocumentItem {
  id: string;
  source_id: string;
  title: string;
  url: string;
  kind: string;
  publish_time: string;
  race_stage: string;
  stance: string;
}

export interface SummaryOutput {
  id: string;
  label: SummaryLabel;
  title: string;
  body: string;
  editorial_status: EditorialStatus;
  updated_at: string;
}

export interface TimelinePhase {
  phase: string;
  state: "complete" | "active" | "upcoming";
  headline: string;
  focus: string;
}

export interface StandingEntry {
  position: number;
  name: string;
  points: number;
  code?: string;
  team?: string;
  nationality?: string;
}

export interface ScheduleRace {
  round: number;
  grand_prix: string;
  date_range: string;
  venue: string;
  status: "completed" | "next" | "upcoming";
  winner?: string;
  winner_team?: string;
}

export interface TeamCarWatch {
  team: string;
  points: number;
  championship_position: number;
  drivers: Array<{
    name: string;
    code?: string;
    points: number;
    position: number;
  }>;
  update_status: string;
}

export interface ArticleFeedItem {
  id: string;
  title: string;
  url: string;
  publish_time: string;
  kind: string;
  stance: string;
  source_name: string;
  source_kind: string;
}

export interface ChartSeries {
  label: string;
  values: number[];
}

export interface SessionResultEntry {
  position: number;
  driver: string;
  team: string;
  metric: string;
  points?: number;
}

export interface SessionResult {
  name: string;
  category: "practice" | "qualifying" | "race";
  status: "completed" | "active" | "upcoming";
  source_url: string;
  entries: SessionResultEntry[];
}

export interface CompletedWeekendResult {
  id: string;
  name: string;
  date_range: string | null;
  sessions: SessionResult[];
}

export interface Cluster {
  id: string;
  slug: string;
  title: string;
  label: SummaryLabel;
  status: string;
  race_stage: string;
  freshness: string;
  confidence: number;
  trend: string;
  summary: SummaryOutput;
  documents: DocumentItem[];
  entities: Entity[];
  sources: Source[];
  source_count: number;
  document_count: number;
  weekend: {
    id: string;
    name: string;
    stage: string;
  };
}

export interface DashboardResponse {
  weekend: {
    id: string;
    name: string;
    stage: string;
    changes_since_last_race: string[];
    previous_weekend_name: string | null;
    date_range?: string;
  };
  hero: {
    eyebrow: string;
    title: string;
    subtitle: string;
    stage: string;
    updated_at: string;
    signal_score: string;
  };
  what_changed: string[];
  sections: {
    official_updates: Cluster[];
    race_results: Cluster[];
    analysis: Cluster[];
    predictions: Cluster[];
  };
  top_clusters: Cluster[];
  timeline: TimelinePhase[];
  season: {
    year: number;
    current_phase: string;
    status_note: string;
    leader_driver: string;
    leader_team: string;
    rounds_completed: number;
    total_rounds: number;
    next_race_name: string;
    next_race_date_range: string;
    next_race_sessions: Array<{
      name: string;
      time_local: string;
    }>;
  };
  latest_weekend_results: {
    name: string | null;
    date_range: string | null;
    sessions: SessionResult[];
  };
  completed_weekend_results: CompletedWeekendResult[];
  driver_standings: StandingEntry[];
  constructor_standings: StandingEntry[];
  team_cars: TeamCarWatch[];
  article_feed: ArticleFeedItem[];
  calendar: ScheduleRace[];
  performance_charts: {
    race_labels: string[];
    contenders: string[];
    points_series: ChartSeries[];
    speed_series: ChartSeries[];
    fastest_lap_series: ChartSeries[];
  };
  next_race_prediction: {
    race_name: string;
    date_range: string;
    weekend_format: string;
    reason: string;
    top_three: Array<{
      position: number;
      driver: string;
      team: string;
    }>;
  };
  sync: {
    source: string;
    last_attempt_at: string | null;
    last_success_at: string | null;
    status: string;
    message: string;
  };
  source_rollup: {
    official_count: number;
    media_count: number;
    team_count: number;
    total_sources: number;
    total_documents: number;
  };
}

export interface PredictionFeatureScore {
  key: string;
  label: string;
  value: number;
  display_value: string;
  impact: string;
}

export interface PredictionContender {
  rank: number;
  driver: string;
  team: string;
  win_probability: number;
  podium_probability: number;
  model_score: number;
  confidence: string;
  outlook: string;
  evidence: string[];
  features: PredictionFeatureScore[];
}

export interface PredictionImportance {
  label: string;
  value: number;
  description: string;
}

export interface ConstructorOutlook {
  team: string;
  car_formula: string;
  power_score: number;
  qualifying_score: number;
  tyre_score: number;
  reliability: number;
}

export interface ScenarioMatrixItem {
  title: string;
  description: string;
  effect: string;
}

export interface PredictionSourceItem {
  label: string;
  kind: string;
  role: string;
  url: string;
}

export interface PredictionAnalyticsResponse {
  race: {
    name: string;
    date_range: string;
    weekend_format: string;
    venue: string;
    phase: string;
  };
  track: {
    track_type: string;
    street_circuit_bias: number;
    overtaking_score: number;
    tyre_stress_score: number;
    traction_importance: number;
    track_evolution: number;
    weather_variability: number;
    expected_strategy: string;
    tyre_outlook: string;
    notes: string;
  };
  model: {
    name: string;
    version: string;
    overview: string;
    target: string;
    training: {
      completed_races: number;
      observations: number;
      positive_examples: number;
      blend: string;
    };
    confidence: string;
    notes: string[];
  };
  contenders: PredictionContender[];
  feature_importance: PredictionImportance[];
  constructor_outlook: ConstructorOutlook[];
  scenario_matrix: ScenarioMatrixItem[];
  source_stack: PredictionSourceItem[];
}
