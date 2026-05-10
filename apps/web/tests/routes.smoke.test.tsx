import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "@/App";
import * as api from "@/lib/api";
import { AppRoutes } from "@/routes/AppRoutes";

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");

  return {
    ...actual,
    listCampaigns: vi.fn(),
    getCampaign: vi.fn(),
    createCampaign: vi.fn(),
    listCampaignAccounts: vi.fn(),
    uploadCampaignCsv: vi.fn(),
    startCampaignRun: vi.fn(),
    getCampaignRun: vi.fn(),
    listCampaignRuns: vi.fn(),
    getLatestCampaignRun: vi.fn(),
    listCampaignEvents: vi.fn(),
    getCampaignTodos: vi.fn(),
    getCampaignResults: vi.fn(),
    getAccountDetail: vi.fn(),
    updateAccountReviewStatus: vi.fn(),
    updateOutreachDraft: vi.fn(),
    createCampaignExports: vi.fn(),
    listCampaignExports: vi.fn(),
  };
});

const mockedListCampaigns = vi.mocked(api.listCampaigns);
const mockedGetCampaign = vi.mocked(api.getCampaign);
const mockedListCampaignAccounts = vi.mocked(api.listCampaignAccounts);
const mockedGetLatestCampaignRun = vi.mocked(api.getLatestCampaignRun);
const mockedGetCampaignRun = vi.mocked(api.getCampaignRun);
const mockedListCampaignEvents = vi.mocked(api.listCampaignEvents);
const mockedGetCampaignTodos = vi.mocked(api.getCampaignTodos);
const mockedGetCampaignResults = vi.mocked(api.getCampaignResults);
const mockedListCampaignExports = vi.mocked(api.listCampaignExports);
const mockedGetAccountDetail = vi.mocked(api.getAccountDetail);

const campaign = {
  id: "campaign-1",
  name: "Acme Expansion",
  status: "completed",
  product_description: "AI workspace for outbound prospecting",
  ideal_customer_profile: "B2B software teams",
  pain_statement: "Pipeline quality is inconsistent.",
  target_persona: "VP of Sales",
  tone: "Direct and confident",
  max_accounts: 10,
  created_at: "2026-05-09T12:00:00Z",
} as const;

const account = {
  id: "account-1",
  company_name: "Acme Corp",
  domain: "acme.com",
  research_status: "completed",
  review_status: "approved",
} as const;

const run = {
  id: "run-1",
  status: "completed",
  started_at: "2026-05-09T12:00:00Z",
  completed_at: "2026-05-09T12:05:00Z",
  agent_thread_id: "thread-123",
  error_message: null,
} as const;

const resultAccount = {
  account_id: "account-1",
  company_name: "Acme Corp",
  domain: "acme.com",
  research_status: "completed",
  review_status: "approved",
  draft_quality_status: "ready",
  overall_score: 88,
  fit_score: 84,
  timing_score: 80,
  confidence_score: 90,
  recommended_persona: "VP of Sales",
  sales_angle: "Improve prospecting throughput with better research context.",
} as const;

const accountDetail = {
  account: {
    ...account,
    status: "active",
  },
  research_report: null,
  signal_report: null,
  score_report: {
    overall_score: 88,
    recommended_persona: "VP of Sales",
    sales_angle: "Improve prospecting throughput with better research context.",
  },
  outreach_draft: null,
  quality_review: null,
} as const;

function renderRoute(path: string) {
  render(
    <App
      router={
        <MemoryRouter initialEntries={[path]}>
          <AppRoutes />
        </MemoryRouter>
      }
    />,
  );
}

describe("App route smoke coverage", () => {
  beforeEach(() => {
    mockedListCampaigns.mockResolvedValue({ campaigns: [campaign] } as never);
    mockedGetCampaign.mockResolvedValue(campaign as never);
    mockedListCampaignAccounts.mockResolvedValue({ accounts: [account] } as never);
    mockedGetLatestCampaignRun.mockResolvedValue(run as never);
    mockedGetCampaignRun.mockResolvedValue(run as never);
    mockedListCampaignEvents.mockResolvedValue({
      events: [
        {
          id: "event-1",
          run_id: "run-1",
          type: "run_started",
          message: "Research run started.",
          payload: null,
          created_at: "2026-05-09T12:00:01Z",
        },
      ],
    } as never);
    mockedGetCampaignTodos.mockResolvedValue({
      todos: [
        {
          id: "todo-1",
          title: "Research Acme Corp",
          status: "completed",
        },
      ],
    } as never);
    mockedGetCampaignResults.mockResolvedValue({
      status: "completed",
      accounts: [resultAccount],
    } as never);
    mockedListCampaignExports.mockResolvedValue({
      exports: [
        {
          id: "export-1",
          export_type: "csv",
          created_at: "2026-05-09T12:06:00Z",
          download_url: "/exports/export-1.csv",
        },
      ],
    } as never);
    mockedGetAccountDetail.mockResolvedValue(accountDetail as never);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it.each([
    ["/", "Prospecting Agent"],
    ["/campaigns", "Campaign setup workspace"],
    ["/campaigns/new", "Set up a new research campaign"],
    ["/campaigns/campaign-1", "Acme Expansion"],
    ["/campaigns/campaign-1/run?runId=run-1", "Run activity log"],
    ["/campaigns/campaign-1/results", "Ranked account results"],
    ["/campaigns/campaign-1/accounts/account-1", "Acme Corp"],
  ])("renders %s", async (path, text) => {
    renderRoute(path);

    expect(await screen.findByText(text)).toBeInTheDocument();
  });
});
