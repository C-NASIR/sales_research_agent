import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import { ResultsWorkspace } from "@/components/results/ResultsWorkspace";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { LoadingState } from "@/components/ui/LoadingState";
import { Link } from "@/components/ui/Link";
import { useDocumentTitle } from "@/hooks/useDocumentTitle";
import {
  ApiError,
  getCampaign,
  getCampaignResults,
  listCampaignExports,
} from "@/lib/api";
import { formatStatus } from "@/lib/format";

type CampaignResultsData = {
  campaign: Awaited<ReturnType<typeof getCampaign>>;
  results: Awaited<ReturnType<typeof getCampaignResults>>;
  exports: Awaited<ReturnType<typeof listCampaignExports>>;
};

export function CampaignResultsPage() {
  const { campaignId = "" } = useParams<{ campaignId: string }>();

  const resultsPageQuery = useQuery<CampaignResultsData>({
    queryKey: ["campaign-results-page", campaignId],
    enabled: Boolean(campaignId),
    retry: false,
    queryFn: async () => {
      const [campaign, results, exportsResponse] = await Promise.all([
        getCampaign(campaignId),
        getCampaignResults(campaignId),
        listCampaignExports(campaignId),
      ]);

      return {
        campaign,
        results,
        exports: exportsResponse,
      };
    },
  });

  useDocumentTitle(
    resultsPageQuery.data?.campaign.name
      ? `${resultsPageQuery.data.campaign.name} Results | Prospecting Agent`
      : "Results Dashboard | Prospecting Agent",
  );

  if (resultsPageQuery.isPending) {
    return (
      <main className="page-shell">
        <LoadingState
          title="Loading results"
          message="Fetching ranked account results and campaign summary data."
        />
      </main>
    );
  }

  if (resultsPageQuery.isError) {
    if (
      resultsPageQuery.error instanceof ApiError &&
      resultsPageQuery.error.status === 404
    ) {
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
      resultsPageQuery.error instanceof Error
        ? resultsPageQuery.error.message
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

  if (!resultsPageQuery.data) {
    return (
      <main className="page-shell">
        <ErrorMessage message="Campaign results are unavailable." />
      </main>
    );
  }

  const { campaign, results, exports: exportsResponse } = resultsPageQuery.data;

  return (
    <main className="page-shell stack-xl">
      <section className="section-heading">
        <div className="stack-sm">
          <div>
            <p className="eyebrow">Results dashboard</p>
            <h1>{campaign.name}</h1>
          </div>
          <p className="lead">
            Review ranked account results, evidence-backed scoring, and draft quality
            signals for this completed run.
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
}
