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
