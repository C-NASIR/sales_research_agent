"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

import {
  ApiError,
  getCampaignRun,
  getCampaignTodos,
  getLatestCampaignRun,
  listCampaignAccounts,
  listCampaignEvents,
} from "@/lib/api";
import type { CampaignRun } from "@/lib/types";

import { AccountProgress } from "./AccountProgress";
import { ActivityLog } from "./ActivityLog";
import { RunCompletionActions } from "./RunCompletionActions";
import { RunErrorPanel } from "./RunErrorPanel";
import { RunStatusCard } from "./RunStatusCard";
import { TodoList } from "./TodoList";
import { Card } from "../ui/Card";
import { EmptyState } from "../ui/EmptyState";
import { ErrorMessage } from "../ui/ErrorMessage";
import { LoadingState } from "../ui/LoadingState";

const POLL_INTERVAL_MS = 2000;

function isTerminalRunStatus(status: string | null | undefined): boolean {
  return status === "completed" || status === "failed" || status === "partial";
}

type RunProgressViewProps = {
  campaignId: string;
  initialRunId?: string;
};

export function RunProgressView({
  campaignId,
  initialRunId,
}: RunProgressViewProps) {
  const runQuery = useQuery({
    queryKey: ["campaign-run", campaignId, initialRunId ?? "latest"],
    queryFn: () =>
      initialRunId
        ? getCampaignRun(campaignId, initialRunId)
        : getLatestCampaignRun(campaignId),
    retry: false,
    refetchInterval: (query) => {
      const error = query.state.error;
      if (error instanceof ApiError && error.status === 404) {
        return false;
      }
      const run = query.state.data as CampaignRun | undefined;
      return isTerminalRunStatus(run?.status) ? false : POLL_INTERVAL_MS;
    },
  });

  const run = runQuery.data;
  const isTerminal = isTerminalRunStatus(run?.status);

  const eventsQuery = useQuery({
    queryKey: ["campaign-events", campaignId],
    queryFn: () => listCampaignEvents(campaignId),
    enabled: Boolean(run),
    refetchInterval: isTerminal ? false : POLL_INTERVAL_MS,
  });

  const accountsQuery = useQuery({
    queryKey: ["campaign-accounts", campaignId],
    queryFn: () => listCampaignAccounts(campaignId),
    enabled: Boolean(run),
    refetchInterval: isTerminal ? false : POLL_INTERVAL_MS,
  });

  const todosQuery = useQuery({
    queryKey: ["campaign-todos", campaignId],
    queryFn: () => getCampaignTodos(campaignId),
    enabled: Boolean(run),
    refetchInterval: isTerminal ? false : POLL_INTERVAL_MS,
  });

  if (runQuery.isPending) {
    return (
      <LoadingState
        title="Loading run"
        message="Fetching the latest run record and progress data."
      />
    );
  }

  if (runQuery.isError) {
    if (runQuery.error instanceof ApiError && runQuery.error.status === 404) {
      return (
        <Card className="stack-md">
          <EmptyState
            title="No run yet"
            message="No run has been started for this campaign yet."
          />
          <Link className="button button-secondary" href={`/campaigns/${campaignId}`}>
            Back to campaign setup
          </Link>
        </Card>
      );
    }

    const message =
      runQuery.error instanceof Error
        ? runQuery.error.message
        : "Unable to load run progress.";

    return (
      <Card className="stack-md">
        <div>
          <p className="eyebrow">Run progress</p>
          <h2>Unable to load run data</h2>
        </div>
        <ErrorMessage message={message} />
        <Link className="button button-secondary" href={`/campaigns/${campaignId}`}>
          Back to campaign setup
        </Link>
      </Card>
    );
  }

  if (!run) {
    return (
      <Card className="stack-md">
        <ErrorMessage message="Run data is unavailable." />
        <Link className="button button-secondary" href={`/campaigns/${campaignId}`}>
          Back to campaign setup
        </Link>
      </Card>
    );
  }

  const filteredEvents =
    eventsQuery.data?.events.filter((event) => event.run_id === run.id) ?? [];
  const accounts = accountsQuery.data?.accounts ?? [];
  const todos = todosQuery.data?.todos ?? [];

  return (
    <div className="stack-xl">
      <RunStatusCard run={run} />

      <div className="run-grid">
        <AccountProgress accounts={accounts} />
        <TodoList todos={todos} />
      </div>

      {(eventsQuery.isPending || accountsQuery.isPending || todosQuery.isPending) && !isTerminal ? (
        <LoadingState
          title="Polling run progress"
          message="Fetching the latest run status, events, accounts, and todos."
        />
      ) : null}

      <ActivityLog events={filteredEvents} />

      {run.status === "failed" ? (
        <RunErrorPanel campaignId={campaignId} errorMessage={run.error_message} />
      ) : null}

      {run.status === "completed" || run.status === "partial" ? (
        <RunCompletionActions campaignId={campaignId} />
      ) : null}
    </div>
  );
}
