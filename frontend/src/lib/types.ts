// Mirrors the backend response schemas (app/schemas).

export interface ActivityView {
  id: string;
  timestamp: string;
  category: string;
  project: string | null;
  duration: number;
  intent: string | null;
  confidence: number;
  evaluation_score: number | null;
  validated: boolean;
}

export interface ActivityResponse {
  activity: ActivityView | null;
  timeline_updated: boolean;
  errors: string[];
}

export interface TimelineResponse {
  date: string;
  activities: ActivityView[];
  total_duration: number;
  context_switches: number;
  session_count: number;
}

export interface MemoryView {
  id: string;
  type: string;
  statement: string;
  confidence: number;
  evidence_count: number;
  status: string;
}

export interface MemoryResponse {
  memories: MemoryView[];
  count: number;
}

export interface InsightView {
  id: string;
  title: string;
  description: string;
  confidence: number;
  importance: number;
}

export interface InsightsResponse {
  insights: InsightView[];
  count: number;
}

export interface RecommendationView {
  id: string;
  title: string;
  reason: string;
  expected_impact: string;
  priority: string;
  confidence: number;
}

export interface RecommendationsResponse {
  recommendations: RecommendationView[];
  count: number;
}

export interface SummaryResponse {
  id: string;
  date: string;
  overview: string;
  timeline: string;
  metrics: Record<string, unknown>;
  insights: InsightView[];
  recommendations: RecommendationView[];
  tomorrow_focus: string;
}

export interface ProfileResponse {
  id: string;
  name: string;
  occupation: string;
  timezone: string;
  goals: string[];
  interests: string[];
  active_projects: string[];
  preferences: Record<string, unknown>;
}
