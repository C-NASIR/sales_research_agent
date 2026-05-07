import type { AccountResult } from "@/lib/types";

type ResultsSummaryCardsProps = {
  accounts: AccountResult[];
};

export function ResultsSummaryCards({
  accounts,
}: ResultsSummaryCardsProps) {
  const completedAccounts = accounts.filter(
    (account) => account.research_status === "completed",
  ).length;
  const failedAccounts = accounts.filter(
    (account) => account.research_status === "failed",
  ).length;
  const highScoreAccounts = accounts.filter(
    (account) => (account.overall_score ?? -1) >= 75,
  ).length;
  const flaggedDrafts = accounts.filter((account) =>
    ["flagged", "blocked"].includes(account.draft_quality_status ?? ""),
  ).length;

  const items = [
    { label: "Total accounts", value: accounts.length },
    { label: "Completed accounts", value: completedAccounts },
    { label: "Failed accounts", value: failedAccounts },
    { label: "High score accounts", value: highScoreAccounts },
    { label: "Flagged drafts", value: flaggedDrafts },
  ];

  return (
    <section className="results-summary-grid" aria-label="Results summary">
      {items.map((item) => (
        <article className="summary-card" key={item.label}>
          <p className="summary-card-label">{item.label}</p>
          <strong className="summary-card-value">{item.value}</strong>
        </article>
      ))}
    </section>
  );
}
