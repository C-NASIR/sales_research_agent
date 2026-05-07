"use client";

import { Field } from "@/components/ui/Field";
import { Input } from "@/components/ui/Input";
import { formatStatus } from "@/lib/format";

export type ResultsFilterState = {
  searchTerm: string;
  researchStatus: string;
  draftQualityStatus: string;
  minOverallScore: string;
};

type ResultsFiltersProps = {
  filters: ResultsFilterState;
  researchStatuses: string[];
  qualityStatuses: string[];
  onChange: (filters: ResultsFilterState) => void;
};

export function ResultsFilters({
  filters,
  researchStatuses,
  qualityStatuses,
  onChange,
}: ResultsFiltersProps) {
  return (
    <section className="card stack-md" aria-label="Results filters">
      <div>
        <p className="eyebrow">Filters</p>
        <h2>Find the strongest accounts fast</h2>
        <p className="supporting-text">
          Narrow by company, research completion, draft quality, or minimum score.
        </p>
      </div>

      <div className="filters-grid">
        <Field
          label="Search"
          htmlFor="results-search"
          description="Search by company name or domain."
        >
          <Input
            id="results-search"
            type="search"
            placeholder="Search accounts"
            value={filters.searchTerm}
            onChange={(event) =>
              onChange({ ...filters, searchTerm: event.target.value })
            }
          />
        </Field>

        <Field label="Research status" htmlFor="research-status-filter">
          <select
            id="research-status-filter"
            className="input"
            value={filters.researchStatus}
            onChange={(event) =>
              onChange({ ...filters, researchStatus: event.target.value })
            }
          >
            <option value="all">All statuses</option>
            {researchStatuses.map((status) => (
              <option key={status} value={status}>
                {formatStatus(status)}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Draft quality" htmlFor="quality-status-filter">
          <select
            id="quality-status-filter"
            className="input"
            value={filters.draftQualityStatus}
            onChange={(event) =>
              onChange({ ...filters, draftQualityStatus: event.target.value })
            }
          >
            <option value="all">All quality states</option>
            {qualityStatuses.map((status) => (
              <option key={status} value={status}>
                {formatStatus(status)}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Minimum overall score" htmlFor="min-score-filter">
          <select
            id="min-score-filter"
            className="input"
            value={filters.minOverallScore}
            onChange={(event) =>
              onChange({ ...filters, minOverallScore: event.target.value })
            }
          >
            <option value="all">Any score</option>
            <option value="75">75 and above</option>
            <option value="60">60 and above</option>
            <option value="40">40 and above</option>
          </select>
        </Field>
      </div>
    </section>
  );
}
