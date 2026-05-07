import Link from "next/link";

import { RunProgressView } from "@/components/run/RunProgressView";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { ApiError, getCampaign } from "@/lib/api";

type CampaignRunPageProps = {
  params: Promise<{
    campaignId: string;
  }>;
  searchParams: Promise<{
    runId?: string | string[];
  }>;
};

export default async function CampaignRunPage({
  params,
  searchParams,
}: CampaignRunPageProps) {
  const { campaignId } = await params;
  const { runId } = await searchParams;
  const selectedRunId = typeof runId === "string" ? runId : undefined;

  try {
    const campaign = await getCampaign(campaignId);

    return (
      <main className="page-shell stack-xl">
        <section className="section-heading">
          <div className="stack-sm">
            <div>
              <p className="eyebrow">Run progress</p>
              <h1>{campaign.name}</h1>
            </div>
            <p className="lead">
              This page polls the latest run status, todos, activity events, and account
              completion counts every 2 seconds until the run finishes.
            </p>
          </div>
          <Link className="button button-ghost" href={`/campaigns/${campaignId}`}>
            Back to campaign setup
          </Link>
        </section>

        <RunProgressView campaignId={campaignId} initialRunId={selectedRunId} />
      </main>
    );
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return (
        <main className="page-shell">
          <EmptyState
            title="Campaign not found"
            message="This campaign does not exist or is no longer available."
          />
        </main>
      );
    }

    const message =
      error instanceof Error ? error.message : "Unable to load this campaign.";

    return (
      <main className="page-shell">
        <Card className="stack-md">
          <div>
            <p className="eyebrow">Run progress</p>
            <h1>Unable to load campaign</h1>
          </div>
          <ErrorMessage message={message} />
          <Link className="button button-secondary" href="/campaigns">
            Return to campaign list
          </Link>
        </Card>
      </main>
    );
  }
}
