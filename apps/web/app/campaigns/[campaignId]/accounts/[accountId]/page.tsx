import Link from "next/link";

import { AccountDetailWorkspace } from "@/components/account/AccountDetailWorkspace";
import { AccountHeader } from "@/components/account/AccountHeader";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { ApiError, getAccountDetail, getCampaign } from "@/lib/api";

type AccountDetailPageProps = {
  params: Promise<{
    campaignId: string;
    accountId: string;
  }>;
};

export default async function AccountDetailPage({
  params,
}: AccountDetailPageProps) {
  const { campaignId, accountId } = await params;

  try {
    const [campaign, detail] = await Promise.all([
      getCampaign(campaignId),
      getAccountDetail(campaignId, accountId),
    ]);

    return (
      <main className="page-shell stack-xl">
        <section className="section-heading">
          <div className="stack-sm">
            <div>
              <p className="eyebrow">Account results</p>
              <h1>{campaign.name}</h1>
            </div>
            <p className="lead">
              Inspect the research evidence, timing signals, score breakdown, draft,
              and quality review for a single account.
            </p>
          </div>
          <div className="results-page-actions">
            <Link className="button button-ghost" href={`/campaigns/${campaignId}/results`}>
              Back to results dashboard
            </Link>
            <Link className="button button-secondary" href={`/campaigns/${campaignId}`}>
              Back to campaign setup
            </Link>
          </div>
        </section>

        <AccountHeader account={detail.account} scoreReport={detail.score_report} />
        <AccountDetailWorkspace
          accountId={accountId}
          campaignId={campaignId}
          initialDetail={detail}
        />
      </main>
    );
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return (
        <main className="page-shell">
          <EmptyState
            title="Account not found"
            message="This account does not exist or is no longer available for the selected campaign."
          />
        </main>
      );
    }

    const message =
      error instanceof Error ? error.message : "Unable to load account details.";

    return (
      <main className="page-shell">
        <Card className="stack-md">
          <div>
            <p className="eyebrow">Account detail</p>
            <h1>Unable to load account</h1>
          </div>
          <ErrorMessage message={message} />
          <div className="form-actions">
            <Link className="button button-secondary" href={`/campaigns/${campaignId}/results`}>
              Back to results dashboard
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
