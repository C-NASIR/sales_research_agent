export type CampaignStatus =
  | "draft"
  | "ready"
  | "running"
  | "completed"
  | "failed"
  | "partial";

export type Campaign = {
  id: string;
  name: string;
  product_description: string;
  ideal_customer_profile: string;
  pain_statement: string;
  target_persona: string;
  tone: string;
  max_accounts: number;
  status: CampaignStatus;
  workspace_path: string;
  created_at: string;
  updated_at: string;
};

export type CampaignListResponse = {
  campaigns: Campaign[];
};

export type CreateCampaignInput = {
  name: string;
  product_description: string;
  ideal_customer_profile: string;
  pain_statement: string;
  target_persona: string;
  tone: string;
  max_accounts: number;
};

export type Account = {
  id: string;
  campaign_id: string;
  company_name: string;
  domain: string;
  research_status: string;
  review_status: string;
  created_at: string;
  updated_at: string;
};

export type AccountListResponse = {
  accounts: Account[];
};

export type UploadInvalidRow = {
  row_number: number;
  reason: string;
  raw: Record<string, unknown>;
};

export type UploadDuplicateRow = {
  row_number: number;
  company_name: string;
  domain: string;
  duplicate_of_domain: string;
};

export type UploadAccountPreview = {
  id: string | null;
  company_name: string;
  domain: string;
};

export type UploadReportResponse = {
  campaign_id: string;
  valid_rows: number;
  invalid_rows: number;
  duplicate_rows: number;
  created_accounts: number;
  accounts: UploadAccountPreview[];
  invalid: UploadInvalidRow[];
  duplicates: UploadDuplicateRow[];
};

export type CampaignRun = {
  id: string;
  campaign_id: string;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  agent_thread_id: string | null;
  created_at: string;
  updated_at: string;
};

export type CampaignRunListResponse = {
  runs: CampaignRun[];
};

export type ActivityEvent = {
  id: string;
  campaign_id: string;
  run_id: string | null;
  type: string;
  message: string;
  payload: Record<string, unknown> | null;
  created_at: string;
};

export type ActivityEventListResponse = {
  events: ActivityEvent[];
};

export type TodoStatus = "pending" | "in_progress" | "completed" | "failed";

export type TodoItem = {
  id: string;
  title: string;
  status: TodoStatus | string;
};

export type TodoListResponse = {
  todos: TodoItem[];
};

export type AccountResult = {
  account_id: string;
  company_name: string;
  domain: string;
  overall_score: number | null;
  fit_score: number | null;
  timing_score: number | null;
  confidence_score: number | null;
  persona_score: number | null;
  recommended_persona: string | null;
  sales_angle: string | null;
  review_status: string;
  research_status: string;
  draft_quality_status: string | null;
};

export type CampaignResultsResponse = {
  campaign_id: string;
  status: string;
  accounts: AccountResult[];
};

export type EvidenceItem = {
  claim: string;
  evidence: string;
  source_url?: string | null;
  source_title?: string | null;
  confidence?: string | null;
  evidence_type?: string | null;
};

export type RiskItem = {
  risk: string;
  reason: string;
  confidence?: string | null;
};

export type ResearchReport = {
  id?: string;
  account_id?: string;
  company_summary: string | null;
  business_model?: string | null;
  fit_claims: EvidenceItem[];
  evidence: EvidenceItem[];
  risks: RiskItem[];
  confidence: number | null;
  workspace_file?: string | null;
  sources?: unknown[];
};

export type SignalItem = {
  type: string;
  description: string;
  why_it_matters?: string | null;
  source_url?: string | null;
  confidence?: string | null;
};

export type SignalReport = {
  id?: string;
  account_id?: string;
  signals: SignalItem[];
  timing_score: number | null;
  why_now: string | null;
  confidence: number | null;
  workspace_file?: string | null;
  sources?: unknown[];
};

export type ScoreReport = {
  id?: string;
  account_id?: string;
  fit_score: number | null;
  timing_score: number | null;
  confidence_score: number | null;
  persona_score: number | null;
  overall_score: number | null;
  recommended_persona?: string | null;
  sales_angle?: string | null;
  score_explanation: string | null;
  score_breakdown: Record<string, unknown> | null;
  workspace_file?: string | null;
};

export type OutreachDraft = {
  id?: string;
  account_id?: string;
  subject: string | null;
  body: string | null;
  personalization_source: string | null;
  personalization_source_url?: string | null;
  sales_angle: string | null;
  risk_notes: string[];
  quality_status: string | null;
  workspace_file?: string | null;
};

export type QualityReview = {
  company_name?: string;
  domain?: string;
  quality_status: string | null;
  issues: string[];
  blocked_reasons: string[];
  recommended_edits: string[];
};

export type AccountDetailResponse = {
  account: Account;
  research_report: ResearchReport | null;
  signal_report: SignalReport | null;
  score_report: ScoreReport | null;
  outreach_draft: OutreachDraft | null;
  quality_review: QualityReview | null;
};
