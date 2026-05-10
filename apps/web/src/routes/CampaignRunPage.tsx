import { useQuery } from "@tanstack/react-query";
import { useParams, useSearchParams } from "react-router-dom";

import { RunProgressView } from "@/components/run/RunProgressView";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { LoadingState } from "@/components/ui/LoadingState";
import { Link } from "@/components/ui/Link";
import { useDocumentTitle } from "@/hooks/useDocumentTitle";
import { ApiError, getCampaign } from "@/lib/api";

export function CampaignRunPage() {
  const { campaignId = "" } = useParams<{ campaignId: string }>();
  const [searchParams] = useSearchParams();
  const selectedRunId = searchParams.get("runId") ?? undefined;

  const campaignQuery = useQuery({
    queryKey: ["campaign", campaignId],
    enabled: Boolean(campaignId),
    retry: false,
    queryFn: () => getCampaign(campaignId),
  });

  useDocumentTitle(
    campaignQuery.data?.name
      ? `${campaignQuery.data.name} Run Progress | Prospecting Agent`
      : "Run Progress | Prospecting Agent",
  );

  if (campaignQuery.isPending) {
    return (
      <main className="page-shell">
        <LoadingState
          title="Loading run progress"
          message="Fetching the latest run record and progress timeline."
        />
      </main>
    );
  }

  if (campaignQuery.isError) {
    if (campaignQuery.error instanceof ApiError && campaignQuery.error.status === 404) {
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
      campaignQuery.error instanceof Error
        ? campaignQuery.error.message
        : "Unable to load this campaign.";

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

  if (!campaignQuery.data) {
    return (
      <main className="page-shell">
        <ErrorMessage message="Campaign data is unavailable." />
      </main>
    );
  }

  const campaign = campaignQuery.data;

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
}
