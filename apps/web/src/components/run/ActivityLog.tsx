import { formatDateTime, formatEventType } from "@/lib/format";
import type { ActivityEvent } from "@/lib/types";

import { Card } from "../ui/Card";

type ActivityLogProps = {
  events: ActivityEvent[];
};

function summarizePayload(payload: Record<string, unknown> | null): string | null {
  if (!payload) {
    return null;
  }

  const keys = [
    "company_name",
    "domain",
    "account_id",
    "succeeded",
    "failed",
    "quality_status",
    "error",
  ];
  const parts = keys
    .filter((key) => key in payload)
    .map((key) => `${key}: ${String(payload[key])}`);

  return parts.length > 0 ? parts.join(" | ") : null;
}

export function ActivityLog({ events }: ActivityLogProps) {
  const displayedEvents = events.slice(-100);

  return (
    <Card className="stack-md">
      <div>
        <p className="eyebrow">Activity</p>
        <h2>Run activity log</h2>
      </div>

      {displayedEvents.length === 0 ? (
        <p className="supporting-text">Waiting for run activity.</p>
      ) : (
        <ol className="activity-log">
          {displayedEvents.map((event) => {
            const payloadSummary = summarizePayload(event.payload);

            return (
              <li key={event.id} className="event-item">
                <div className="event-header">
                  <strong>{formatEventType(event.type)}</strong>
                  <span>{formatDateTime(event.created_at)}</span>
                </div>
                <p>{event.message}</p>
                {payloadSummary ? <p className="event-payload">{payloadSummary}</p> : null}
              </li>
            );
          })}
        </ol>
      )}
    </Card>
  );
}
