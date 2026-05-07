import type { Account } from "@/lib/types";

import { Card } from "../ui/Card";

type AccountProgressProps = {
  accounts: Account[];
};

function countByStatus(accounts: Account[], status: string): number {
  return accounts.filter((account) => account.research_status === status).length;
}

export function AccountProgress({ accounts }: AccountProgressProps) {
  const total = accounts.length;
  const pending = countByStatus(accounts, "pending");
  const researching = countByStatus(accounts, "researching");
  const completed = countByStatus(accounts, "completed");
  const failed = countByStatus(accounts, "failed");
  const skipped = countByStatus(accounts, "skipped");
  const finished = completed + failed + skipped;
  const percent = total === 0 ? 0 : Math.round((finished / total) * 100);

  return (
    <Card className="stack-md">
      <div className="card-row">
        <div>
          <p className="eyebrow">Account progress</p>
          <h2>{percent}% complete</h2>
        </div>
        <span className="count-pill">{total} total</span>
      </div>

      <div className="progress-track" aria-hidden="true">
        <div className="progress-fill" style={{ width: `${percent}%` }} />
      </div>

      <div className="summary-grid">
        <div>
          <span className="summary-label">Pending</span>
          <strong>{pending}</strong>
        </div>
        <div>
          <span className="summary-label">Researching</span>
          <strong>{researching}</strong>
        </div>
        <div>
          <span className="summary-label">Completed</span>
          <strong>{completed}</strong>
        </div>
        <div>
          <span className="summary-label">Failed</span>
          <strong>{failed}</strong>
        </div>
        <div>
          <span className="summary-label">Skipped</span>
          <strong>{skipped}</strong>
        </div>
      </div>
    </Card>
  );
}
