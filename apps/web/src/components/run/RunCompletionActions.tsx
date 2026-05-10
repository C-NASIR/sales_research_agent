import { Card } from "../ui/Card";
import { Link } from "../ui/Link";

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
      <p className="supporting-text">
        Open the results dashboard to inspect ranked accounts, evidence, scores, and
        draft quality notes.
      </p>
      <div className="form-actions">
        <Link className="button button-secondary" href={`/campaigns/${campaignId}`}>
          Back to campaign setup
        </Link>
        <Link className="button button-ghost" href={`/campaigns/${campaignId}/results`}>
          View results
        </Link>
      </div>
    </Card>
  );
}
