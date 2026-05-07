import Link from "next/link";

import { ResultsWorkspace } from "@/components/results/ResultsWorkspace";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { ApiError, getCampaign, getCampaignResults, listCampaignExports } from "@/lib/api";
import { formatStatus } from "@/lib/format";

type CampaignResultsPageProps = {
  params: Promise<{
    campaignId: string;
  }>;
};

export default async function CampaignResultsPage({
  params,
}: CampaignResultsPageProps) {
  const { campaignId } = await params;

  try {
    const [campaign, results, exportsResponse] = await Promise.all([
      getCampaign(campaignId),
      getCampaignResults(campaignId),
      listCampaignExports(campaignId),
    ]);

    return (
      <main className="page-shell stack-xl">
        <section className="section-heading">
          <div className="stack-sm">
            <div>
              <p className="eyebrow">Results dashboard</p>
              <h1>{campaign.name}</h1>
            </div>
            <p className="lead">
              Review ranked account results, evidence-backed scoring, and draft
              quality signals for this completed run.
            </p>
          </div>
          <div className="results-page-actions">
            <span className="detail-tag">Campaign status: {formatStatus(results.status)}</span>
            <Link className="button button-ghost" href={`/campaigns/${campaignId}`}>
              Back to campaign setup
            </Link>
            <Link className="button button-secondary" href={`/campaigns/${campaignId}/run`}>
              View run progress
            </Link>
          </div>
        </section>

        {results.accounts.length ? (
          <ResultsWorkspace
            campaignId={campaignId}
            initialExports={exportsResponse.exports}
            initialResults={results}
          />
        ) : (
          <Card className="stack-md">
            <EmptyState
              title="No results yet"
              message="No results are available yet. Run the campaign first."
            />
          </Card>
        )}
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
      error instanceof Error
        ? error.message
        : "Unable to load campaign results.";

    return (
      <main className="page-shell">
        <Card className="stack-md">
          <div>
            <p className="eyebrow">Results dashboard</p>
            <h1>Unable to load results</h1>
          </div>
          <ErrorMessage message={message} />
          <div className="form-actions">
            <Link className="button button-secondary" href={`/campaigns/${campaignId}`}>
              Back to campaign setup
            </Link>
            <Link className="button button-ghost" href="/campaigns">
              Return to campaign list
            </Link>
          </div>
        </Card>
      </main>
    );
  }
}
