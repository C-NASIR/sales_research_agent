import Link from "next/link";

import { Card } from "../ui/Card";

type RunErrorPanelProps = {
  campaignId: string;
  errorMessage: string | null;
};

export function RunErrorPanel({ campaignId, errorMessage }: RunErrorPanelProps) {
  return (
    <Card className="stack-md error-panel">
      <div>
        <p className="eyebrow">Run failed</p>
        <h2>Run error</h2>
      </div>
      <p className="error-message">{errorMessage ?? "The run failed without an error message."}</p>
      <Link className="button button-secondary" href={`/campaigns/${campaignId}`}>
        Back to campaign setup
      </Link>
    </Card>
  );
}
