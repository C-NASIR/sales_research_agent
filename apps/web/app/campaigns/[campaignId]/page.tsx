import Link from "next/link";

import { AccountPreviewTable } from "@/components/campaign/AccountPreviewTable";
import { CampaignStatusBadge } from "@/components/campaign/CampaignStatusBadge";
import { CsvUploader } from "@/components/campaign/CsvUploader";
import { StartRunButton } from "@/components/campaign/StartRunButton";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { getCampaign, listCampaignAccounts, ApiError } from "@/lib/api";

type CampaignDetailPageProps = {
  params: Promise<{
    campaignId: string;
  }>;
};

export default async function CampaignDetailPage({
  params,
}: CampaignDetailPageProps) {
  const { campaignId } = await params;

  try {
    const [campaign, accountResponse] = await Promise.all([
      getCampaign(campaignId),
      listCampaignAccounts(campaignId),
    ]);
    const accountCount = accountResponse.accounts.length;

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
            This phase starts the run only. Progress and results views are added later.
          </p>
          <StartRunButton
            campaignId={campaign.id}
            campaignStatus={campaign.status}
            accountCount={accountCount}
          />
        </Card>
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
}
