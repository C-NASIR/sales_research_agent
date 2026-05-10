import type { CampaignStatus } from "@/lib/types";

const LABELS: Record<CampaignStatus, string> = {
  draft: "Draft",
  ready: "Ready",
  running: "Running",
  completed: "Completed",
  failed: "Failed",
  partial: "Partial",
};

type CampaignStatusBadgeProps = {
  status: CampaignStatus;
};

export function CampaignStatusBadge({ status }: CampaignStatusBadgeProps) {
  return (
    <span className={`status-badge status-${status}`}>
      {LABELS[status] ?? status}
    </span>
  );
}
