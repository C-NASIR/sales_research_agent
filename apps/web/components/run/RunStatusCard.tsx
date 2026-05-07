import { formatDateTime } from "@/lib/format";
import type { CampaignRun } from "@/lib/types";

import { Card } from "../ui/Card";

const RUN_STATUS_LABELS: Record<string, string> = {
  pending: "Pending",
  running: "Running",
  completed: "Completed",
  failed: "Failed",
  partial: "Partial",
};

type RunStatusCardProps = {
  run: CampaignRun;
};

export function RunStatusCard({ run }: RunStatusCardProps) {
  return (
    <Card className="stack-md">
      <div className="card-row">
        <div>
          <p className="eyebrow">Run status</p>
          <h2>{RUN_STATUS_LABELS[run.status] ?? run.status}</h2>
        </div>
        <span className={`status-badge status-${run.status}`.trim()}>
          {RUN_STATUS_LABELS[run.status] ?? run.status}
        </span>
      </div>

      <dl className="detail-grid">
        <div>
          <dt>Run ID</dt>
          <dd>{run.id}</dd>
        </div>
        <div>
          <dt>Started at</dt>
          <dd>{formatDateTime(run.started_at)}</dd>
        </div>
        <div>
          <dt>Completed at</dt>
          <dd>{formatDateTime(run.completed_at)}</dd>
        </div>
        <div>
          <dt>Agent thread ID</dt>
          <dd>{run.agent_thread_id ?? "Not available"}</dd>
        </div>
      </dl>

      {run.error_message ? <p className="error-message">{run.error_message}</p> : null}
    </Card>
  );
}
