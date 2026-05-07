import type {
  ActivityEventListResponse,
  AccountListResponse,
  Campaign,
  CampaignListResponse,
  CampaignRun,
  CampaignRunListResponse,
  CreateCampaignInput,
  TodoListResponse,
  UploadReportResponse,
} from "./types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type ApiErrorPayload = {
  detail?: string;
  message?: string;
};

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;
  const headers = new Headers(options.headers);
  const isFormData = options.body instanceof FormData;

  if (!isFormData && options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(url, {
    ...options,
    headers,
    cache: options.cache ?? (options.method ? undefined : "no-store"),
  });

  const contentType = response.headers.get("content-type") ?? "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    const errorPayload =
      typeof payload === "string" ? null : (payload as ApiErrorPayload);
    const message =
      typeof payload === "string"
        ? payload || `Request failed with status ${response.status}`
        : errorPayload?.detail ||
          errorPayload?.message ||
          `Request failed with status ${response.status}`;
    throw new ApiError(message, response.status);
  }

  return payload as T;
}

export async function listCampaigns(): Promise<CampaignListResponse> {
  return apiRequest<CampaignListResponse>("/campaigns");
}

export async function getCampaign(campaignId: string): Promise<Campaign> {
  return apiRequest<Campaign>(`/campaigns/${campaignId}`);
}

export async function createCampaign(
  input: CreateCampaignInput,
): Promise<Campaign> {
  return apiRequest<Campaign>("/campaigns", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function listCampaignAccounts(
  campaignId: string,
): Promise<AccountListResponse> {
  return apiRequest<AccountListResponse>(`/campaigns/${campaignId}/accounts`);
}

export async function uploadCampaignCsv(
  campaignId: string,
  file: File,
): Promise<UploadReportResponse> {
  const formData = new FormData();
  formData.append("file", file);

  return apiRequest<UploadReportResponse>(`/campaigns/${campaignId}/upload`, {
    method: "POST",
    body: formData,
  });
}

export async function startCampaignRun(
  campaignId: string,
): Promise<CampaignRun> {
  return apiRequest<CampaignRun>(`/campaigns/${campaignId}/runs`, {
    method: "POST",
  });
}

export async function getCampaignRun(
  campaignId: string,
  runId: string,
): Promise<CampaignRun> {
  return apiRequest<CampaignRun>(`/campaigns/${campaignId}/runs/${runId}`);
}

export async function listCampaignRuns(
  campaignId: string,
): Promise<CampaignRunListResponse> {
  return apiRequest<CampaignRunListResponse>(`/campaigns/${campaignId}/runs`);
}

export async function getLatestCampaignRun(
  campaignId: string,
): Promise<CampaignRun> {
  return apiRequest<CampaignRun>(`/campaigns/${campaignId}/runs/latest`);
}

export async function listCampaignEvents(
  campaignId: string,
): Promise<ActivityEventListResponse> {
  return apiRequest<ActivityEventListResponse>(`/campaigns/${campaignId}/events`);
}

export async function getCampaignTodos(
  campaignId: string,
): Promise<TodoListResponse> {
  return apiRequest<TodoListResponse>(`/campaigns/${campaignId}/todos`);
}
