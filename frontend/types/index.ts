// ── Enums ──────────────────────────────────────────────────────────────────

export enum ContentType {
  COLD_EMAIL = "cold_email",
  LINKEDIN_POST = "linkedin_post",
  BLOG_OUTLINE = "blog_outline",
  AD_COPY = "ad_copy",
}

export enum GTMMotion {
  PLG = "product_led_growth",
  SLG = "sales_led_growth",
  CLG = "community_led_growth",
  MLG = "marketing_led_growth",
}

export enum ValidationStatus {
  PENDING = "pending",
  APPROVED = "approved",
  REJECTED = "rejected",
  REVISED = "revised",
}

export enum UserRole {
  OWNER = "owner",
  ADMIN = "admin",
  MEMBER = "member",
}

export enum AgentEventType {
  AGENT_START = "agent_start",
  AGENT_PROGRESS = "agent_progress",
  AGENT_OUTPUT = "agent_output",
  AGENT_COMPLETE = "agent_complete",
  ERROR = "error",
  DONE = "done",
}

// ── Domain Models ─────────────────────────────────────────────────────────

export interface CompanyProfile {
  name: string;
  website?: string | null;
  industry: string;
  stage: string;
  description: string;
  founded_year?: number | null;
}

export interface MarketSize {
  tam: string;
  sam: string;
  som: string;
  source: string;
  year: number;
}

export interface Competitor {
  name: string;
  website?: string | null;
  positioning: string;
  strengths: string[];
  weaknesses: string[];
  pricing_model?: string | null;
}

export interface Segment {
  name: string;
  description: string;
  size_estimate: string;
  pain_points: string[];
  buying_triggers: string[];
}

export interface Signal {
  type: string;
  description: string;
  relevance: string;
}

export interface ICPProfile {
  title: string;
  industry: string;
  company_size: string;
  budget_range: string;
  pain_points: string[];
  goals: string[];
  buying_committee: string[];
  disqualifiers: string[];
}

export interface ResearchReport {
  company_profile: CompanyProfile;
  market_size: MarketSize;
  competitors: Competitor[];
  segments: Segment[];
  icp: ICPProfile;
  signals: Signal[];
  sources: string[];
  generated_at: string;
}

export interface ValueProp {
  headline: string;
  subheadline: string;
  proof_points: string[];
  differentiators: string[];
}

export interface Channel {
  name: string;
  priority: number;
  rationale: string;
  kpis: string[];
  estimated_cac?: string | null;
}

export interface CompetitiveBattlecard {
  competitor: string;
  our_strengths_vs_them: string[];
  their_strengths_vs_us: string[];
  winning_moves: string[];
  losing_scenarios: string[];
  talk_track: string;
}

export interface GrowthLoop {
  name: string;
  type: string;
  description: string;
  input_metric: string;
  output_metric: string;
}

export interface Milestone {
  week: number;
  goal: string;
  kpis: string[];
  owner: string;
}

export interface GTMStrategy {
  motion: GTMMotion;
  icp: ICPProfile;
  value_proposition: ValueProp;
  channels: Channel[];
  battlecards: CompetitiveBattlecard[];
  growth_loops: GrowthLoop[];
  ninety_day_plan: Milestone[];
  positioning_statement: string;
  generated_at: string;
}

export interface ContentAsset {
  id: string;
  type: ContentType;
  title: string;
  body: string;
  target_icp: string;
  validation_status: ValidationStatus;
  brand_alignment_score?: number | null;
  revision_notes?: string | null;
  created_at: string;
}

// ── SSE Events ────────────────────────────────────────────────────────────

export interface AgentEvent {
  event: AgentEventType;
  agent?: string | null;
  message?: string | null;
  data?: unknown;
  timestamp: string;
}

// ── API Request / Response Models ─────────────────────────────────────────

export interface RegisterRequest {
  email: string;
  password: string;
  company_name: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface ChatRequest {
  session_id?: string | null;
  message: string;
  company_id: string;
}

export interface StrategyGenerateRequest {
  company_profile: CompanyProfile;
  additional_context?: string | null;
}

export interface ContentGenerateRequest {
  strategy_id: string;
  content_types: ContentType[];
  count_per_type: number;
}

// ── DB Response Models ────────────────────────────────────────────────────

export interface StrategyRecord {
  id: string;
  company_id: string;
  user_id: string;
  session_id: string;
  status: "generating" | "complete" | "failed";
  payload: GTMStrategy | null;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeDocument {
  id: string;
  filename: string;
  doc_type: string;
  status: string;
  chunk_count: number | null;
  created_at: string;
}

export interface ContentAssetRecord {
  id: string;
  company_id: string;
  strategy_id: string | null;
  content_type: string;
  title: string;
  body: string;
  validation_status: string;
  brand_alignment_score: number | null;
  created_at: string;
}
