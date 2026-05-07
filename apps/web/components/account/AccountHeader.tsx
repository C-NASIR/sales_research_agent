import { formatStatus } from "@/lib/format";
import type { Account, ScoreReport } from "@/lib/types";

import { ScorePill } from "../results/ScorePill";
import { Card } from "../ui/Card";

type AccountHeaderProps = {
  account: Account;
  scoreReport: ScoreReport | null;
};

export function AccountHeader({ account, scoreReport }: AccountHeaderProps) {
  return (
    <Card className="stack-md">
      <div className="card-row">
        <div className="stack-sm">
          <p className="eyebrow">Account detail</p>
          <div>
            <h1>{account.company_name}</h1>
            <p className="lead">{account.domain}</p>
          </div>
        </div>
        <div className="account-header-pills">
          <span className="detail-tag">
            Research: {formatStatus(account.research_status)}
          </span>
          <span className="detail-tag">
            Review: {formatStatus(account.review_status)}
          </span>
        </div>
      </div>

      <div className="account-header-grid">
        <div>
          <p className="summary-label">Overall score</p>
          <ScorePill score={scoreReport?.overall_score} />
        </div>
        <div>
          <p className="summary-label">Recommended persona</p>
          <strong>{scoreReport?.recommended_persona ?? "Missing"}</strong>
        </div>
        <div>
          <p className="summary-label">Sales angle</p>
          <strong>{scoreReport?.sales_angle ?? "Missing"}</strong>
        </div>
      </div>
    </Card>
  );
}
