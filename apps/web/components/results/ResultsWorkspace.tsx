"use client";

import { useQuery } from "@tanstack/react-query";
import { useDeferredValue, useState } from "react";

import { getCampaignResults, listCampaignExports } from "@/lib/api";
import type {
  CampaignResultsResponse,
  ExportFile,
} from "@/lib/types";

import { AccountResultsTable } from "./AccountResultsTable";
import { ResultsFilters, type ResultsFilterState } from "./ResultsFilters";
import { ResultsSummaryCards } from "./ResultsSummaryCards";
import { ExportList } from "../review/ExportList";
import { ExportPanel } from "../review/ExportPanel";
import { ErrorMessage } from "../ui/ErrorMessage";
import { LoadingState } from "../ui/LoadingState";

type ResultsWorkspaceProps = {
  campaignId: string;
  initialResults: CampaignResultsResponse;
  initialExports: ExportFile[];
};

const DEFAULT_FILTERS: ResultsFilterState = {
  searchTerm: "",
  researchStatus: "all",
  reviewStatus: "all",
  draftQualityStatus: "all",
  minOverallScore: "all",
};

export function ResultsWorkspace({
  campaignId,
  initialResults,
  initialExports,
}: ResultsWorkspaceProps) {
  const [filters, setFilters] = useState<ResultsFilterState>(DEFAULT_FILTERS);
  const deferredSearchTerm = useDeferredValue(filters.searchTerm);

  const resultsQuery = useQuery({
    queryKey: ["campaign-results", campaignId],
    queryFn: () => getCampaignResults(campaignId),
    initialData: initialResults,
  });
  const exportsQuery = useQuery({
    queryKey: ["campaign-exports", campaignId],
    queryFn: async () => (await listCampaignExports(campaignId)).exports,
    initialData: initialExports,
  });

  if (resultsQuery.isPending && !resultsQuery.data) {
    return (
      <LoadingState
        title="Loading results"
        message="Fetching campaign results and export files."
      />
    );
  }

  if (!resultsQuery.data) {
    return <ErrorMessage message="Unable to load results for this campaign." />;
  }

  const accounts = resultsQuery.data.accounts;

  const researchStatuses = [...new Set(accounts.map((account) => account.research_status))];
  const reviewStatuses = [...new Set(accounts.map((account) => account.review_status))];
  const qualityStatuses = [
    ...new Set(
      accounts
        .map((account) => account.draft_quality_status)
        .filter((status): status is string => Boolean(status)),
    ),
  ];

  const filteredAccounts = accounts.filter((account) => {
    const searchTerm = deferredSearchTerm.trim().toLowerCase();
    const matchesSearch =
      !searchTerm ||
      account.company_name.toLowerCase().includes(searchTerm) ||
      account.domain.toLowerCase().includes(searchTerm);
    const matchesResearchStatus =
      filters.researchStatus === "all" ||
      account.research_status === filters.researchStatus;
    const matchesReviewStatus =
      filters.reviewStatus === "all" ||
      account.review_status === filters.reviewStatus;
    const matchesDraftQuality =
      filters.draftQualityStatus === "all" ||
      (account.draft_quality_status ?? "missing") === filters.draftQualityStatus;
    const minScore =
      filters.minOverallScore === "all"
        ? null
        : Number.parseInt(filters.minOverallScore, 10);
    const matchesMinScore =
      minScore === null || (account.overall_score ?? -1) >= minScore;

    return (
      matchesSearch &&
      matchesResearchStatus &&
      matchesReviewStatus &&
      matchesDraftQuality &&
      matchesMinScore
    );
  });

  const approvedAccountCount = accounts.filter(
    (account) => account.review_status === "approved",
  ).length;

  return (
    <div className="stack-xl">
      {resultsQuery.isError ? (
        <ErrorMessage
          message={
            resultsQuery.error instanceof Error
              ? resultsQuery.error.message
              : "Unable to refresh results."
          }
        />
      ) : null}
      {exportsQuery.isError ? (
        <ErrorMessage
          message={
            exportsQuery.error instanceof Error
              ? exportsQuery.error.message
              : "Unable to refresh exports."
          }
        />
      ) : null}
      <ResultsSummaryCards accounts={accounts} />
      <ResultsFilters
        filters={filters}
        researchStatuses={researchStatuses}
        reviewStatuses={reviewStatuses}
        qualityStatuses={qualityStatuses}
        onChange={setFilters}
      />
      <ExportPanel
        campaignId={campaignId}
        approvedAccountCount={approvedAccountCount}
      />
      <ExportList exports={exportsQuery.data ?? []} />
      <section className="card stack-md">
        <div className="card-row">
          <div>
            <h2>Ranked account results</h2>
            <p className="supporting-text">
              Sorted by overall score by default, with missing scores pushed to the
              bottom. Only approved accounts are exported by default.
            </p>
          </div>
          <span className="count-pill">{filteredAccounts.length} visible</span>
        </div>
        <AccountResultsTable campaignId={campaignId} accounts={filteredAccounts} />
      </section>
    </div>
  );
}
