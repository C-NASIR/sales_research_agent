"use client";

import { useDeferredValue, useState } from "react";

import type { AccountResult } from "@/lib/types";

import { AccountResultsTable } from "./AccountResultsTable";
import { ResultsFilters, type ResultsFilterState } from "./ResultsFilters";
import { ResultsSummaryCards } from "./ResultsSummaryCards";

type ResultsWorkspaceProps = {
  campaignId: string;
  accounts: AccountResult[];
};

const DEFAULT_FILTERS: ResultsFilterState = {
  searchTerm: "",
  researchStatus: "all",
  draftQualityStatus: "all",
  minOverallScore: "all",
};

export function ResultsWorkspace({
  campaignId,
  accounts,
}: ResultsWorkspaceProps) {
  const [filters, setFilters] = useState<ResultsFilterState>(DEFAULT_FILTERS);
  const deferredSearchTerm = useDeferredValue(filters.searchTerm);

  const researchStatuses = [...new Set(accounts.map((account) => account.research_status))];
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
      matchesDraftQuality &&
      matchesMinScore
    );
  });

  return (
    <div className="stack-xl">
      <ResultsSummaryCards accounts={accounts} />
      <ResultsFilters
        filters={filters}
        researchStatuses={researchStatuses}
        qualityStatuses={qualityStatuses}
        onChange={setFilters}
      />
      <section className="card stack-md">
        <div className="card-row">
          <div>
            <h2>Ranked account results</h2>
            <p className="supporting-text">
              Sorted by overall score by default, with missing scores pushed to the
              bottom.
            </p>
          </div>
          <span className="count-pill">{filteredAccounts.length} visible</span>
        </div>
        <AccountResultsTable campaignId={campaignId} accounts={filteredAccounts} />
      </section>
    </div>
  );
}
