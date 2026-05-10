import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import { AccountPreviewTable } from "@/components/campaign/AccountPreviewTable";
import { CampaignStatusBadge } from "@/components/campaign/CampaignStatusBadge";
import { CsvUploader } from "@/components/campaign/CsvUploader";
import { StartRunButton } from "@/components/campaign/StartRunButton";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { LoadingState } from "@/components/ui/LoadingState";
import { Link } from "@/components/ui/Link";
import { useDocumentTitle } from "@/hooks/useDocumentTitle";
import {
  ApiError,
  getCampaign,
  getLatestCampaignRun,
  listCampaignAccounts,
} from "@/lib/api";

type CampaignDetailData = {
  campaign: Awaited<ReturnType<typeof getCampaign>>;
  accounts: Awaited<ReturnType<typeof listCampaignAccounts>>;
  latestRun: Awaited<ReturnType<typeof getLatestCampaignRun>> | null;
};

export function CampaignDetailPage() {
  const { campaignId = "" } = useParams<{ campaignId: string }>();

  const detailQuery = useQuery<CampaignDetailData>({
    queryKey: ["campaign-detail", campaignId],
    enabled: Boolean(campaignId),
    retry: false,
    queryFn: async () => {
      const [campaign, accounts, latestRun] = await Promise.all([
        getCampaign(campaignId),
        listCampaignAccounts(campaignId),
        getLatestCampaignRun(campaignId).catch((error) => {
          if (error instanceof ApiError && error.status === 404) {
            return null;
          }

          throw error;
        }),
      ]);

      return { campaign, accounts, latestRun };
    },
  });

  useDocumentTitle(
    detailQuery.data?.campaign.name
      ? `${detailQuery.data.campaign.name} | Prospecting Agent`
      : "Campaign Detail | Prospecting Agent",
  );

  if (detailQuery.isPending) {
    return (
      <main className="page-shell">
        <LoadingState
          title="Loading campaign"
          message="Fetching campaign details, uploaded accounts, and setup controls."
        />
      </main>
    );
  }

  if (detailQuery.isError) {
    if (detailQuery.error instanceof ApiError && detailQuery.error.status === 404) {
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
      detailQuery.error instanceof Error
        ? detailQuery.error.message
        : "Unable to load this campaign.";

    return (
      <main className="page-shell">
        <Card className="stack-md">
          <div>
            <p className="eyebrow">Campaign detail</p>
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

  if (!detailQuery.data) {
    return (
      <main className="page-shell">
        <ErrorMessage message="Campaign data is unavailable." />
      </main>
    );
  }

  const { campaign, accounts: accountResponse, latestRun } = detailQuery.data;
  const accountCount = accountResponse.accounts.length;
  const showRunProgressLink =
    latestRun !== null ||
    ["running", "completed", "failed", "partial"].includes(campaign.status);
  const showResultsLink = ["completed", "partial"].includes(campaign.status);

  return (
    <main className="page-shell stack-xl">
      <section className="section-heading">
        <div className="stack-sm">
          <div className="card-row">
            <div>
              <p className="eyebrow">Campaign detail</p>
              <h1>{campaign.name}</h1>
            </div>
            <CampaignStatusBadge status={campaign.status} />
          </div>
          <p className="lead">
            Finish setup by uploading a CSV of companies and starting the research
            run.
          </p>
        </div>
        <Link className="button button-ghost" href="/campaigns">
          Back to campaigns
        </Link>
      </section>

      {showRunProgressLink ? (
        <Card className="stack-sm">
          <div className="card-row">
            <div>
              <h2>Latest run</h2>
              <p className="supporting-text">
                View the polling-based progress page for the most recent campaign run.
              </p>
            </div>
            <Link
              className="button button-secondary"
              href={`/campaigns/${campaign.id}/run`}
            >
              View run progress
            </Link>
          </div>
        </Card>
      ) : null}

      {showResultsLink ? (
        <Card className="stack-sm">
          <div className="card-row">
            <div>
              <h2>Completed results</h2>
              <p className="supporting-text">
                Review ranked account results, evidence-backed scoring, and draft
                quality for this campaign.
              </p>
            </div>
            <Link
              className="button button-secondary"
              href={`/campaigns/${campaign.id}/results`}
            >
              View results
            </Link>
          </div>
        </Card>
      ) : null}

      <Card className="stack-md">
        <h2>Campaign brief</h2>
        <dl className="detail-grid">
          <div>
            <dt>Product description</dt>
            <dd>{campaign.product_description}</dd>
          </div>
          <div>
            <dt>Ideal customer profile</dt>
            <dd>{campaign.ideal_customer_profile}</dd>
          </div>
          <div>
            <dt>Pain statement</dt>
            <dd>{campaign.pain_statement}</dd>
          </div>
          <div>
            <dt>Target persona</dt>
            <dd>{campaign.target_persona}</dd>
          </div>
          <div>
            <dt>Tone</dt>
            <dd>{campaign.tone}</dd>
          </div>
          <div>
            <dt>Max accounts</dt>
            <dd>{campaign.max_accounts}</dd>
          </div>
        </dl>
      </Card>

      <Card className="stack-md">
        <div className="card-row">
          <div>
            <h2>Upload companies</h2>
            <p className="supporting-text">
              Upload a CSV to create accounts for this campaign and move it out of
              draft state.
            </p>
          </div>
        </div>
        <CsvUploader campaignId={campaign.id} />
      </Card>

      <Card className="stack-md">
        <div className="card-row">
          <div>
            <h2>Uploaded accounts</h2>
            <p className="supporting-text">
              Accounts created from the campaign CSV appear here.
            </p>
          </div>
          <span className="count-pill">{accountCount} accounts</span>
        </div>
        <AccountPreviewTable accounts={accountResponse.accounts} />
      </Card>

      <Card className="stack-md">
        <h2>Start research run</h2>
        <p className="supporting-text">
          Starting the run now opens the progress page. Completed or partial runs can
          be reviewed from the results dashboard.
        </p>
        <StartRunButton
          campaignId={campaign.id}
          campaignStatus={campaign.status}
          accountCount={accountCount}
        />
      </Card>
    </main>
  );
}
