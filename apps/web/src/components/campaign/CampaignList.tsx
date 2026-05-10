import { formatDateTime } from "@/lib/format";
import { Link } from "@/components/ui/Link";
import type { Campaign } from "@/lib/types";

import { CampaignStatusBadge } from "./CampaignStatusBadge";
import { Card } from "../ui/Card";
import { EmptyState } from "../ui/EmptyState";

type CampaignListProps = {
  campaigns: Campaign[];
};

export function CampaignList({ campaigns }: CampaignListProps) {
  if (campaigns.length === 0) {
    return (
      <EmptyState
        title="No campaigns yet"
        message="No campaigns yet. Create your first campaign."
      />
    );
  }

  return (
    <div className="campaign-grid">
      {campaigns.map((campaign) => (
        <Card key={campaign.id} className="campaign-card">
          <div className="card-row">
            <h2>{campaign.name}</h2>
            <CampaignStatusBadge status={campaign.status} />
          </div>
          <p className="campaign-meta">
            <strong>Target persona:</strong> {campaign.target_persona}
          </p>
          <p className="campaign-meta">
            <strong>Created:</strong> {formatDateTime(campaign.created_at)}
          </p>
          <Link className="button button-secondary" href={`/campaigns/${campaign.id}`}>
            Open campaign
          </Link>
        </Card>
      ))}
    </div>
  );
}
