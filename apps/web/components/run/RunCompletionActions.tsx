import Link from "next/link";

import { Card } from "../ui/Card";

type RunCompletionActionsProps = {
  campaignId: string;
};

export function RunCompletionActions({ campaignId }: RunCompletionActionsProps) {
  return (
    <Card className="stack-md completion-actions">
      <div>
        <p className="eyebrow">Run complete</p>
        <h2>Next steps</h2>
      </div>
      <p className="supporting-text">Results dashboard will be added in Phase 8.</p>
      <div className="form-actions">
        <Link className="button button-secondary" href={`/campaigns/${campaignId}`}>
          Back to campaign setup
        </Link>
        <button className="button button-ghost" disabled type="button">
          Results dashboard coming later
        </button>
      </div>
    </Card>
  );
}
