import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import { AccountDetailWorkspace } from "@/components/account/AccountDetailWorkspace";
import { AccountHeader } from "@/components/account/AccountHeader";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { LoadingState } from "@/components/ui/LoadingState";
import { Link } from "@/components/ui/Link";
import { useDocumentTitle } from "@/hooks/useDocumentTitle";
import { ApiError, getAccountDetail, getCampaign } from "@/lib/api";

type AccountDetailData = {
  campaign: Awaited<ReturnType<typeof getCampaign>>;
  detail: Awaited<ReturnType<typeof getAccountDetail>>;
};

export function AccountDetailPage() {
  const { campaignId = "", accountId = "" } = useParams<{
    campaignId: string;
    accountId: string;
  }>();

  const accountPageQuery = useQuery<AccountDetailData>({
    queryKey: ["account-detail-page", campaignId, accountId],
    enabled: Boolean(campaignId && accountId),
    retry: false,
    queryFn: async () => {
      const [campaign, detail] = await Promise.all([
        getCampaign(campaignId),
        getAccountDetail(campaignId, accountId),
      ]);

      return { campaign, detail };
    },
  });

  useDocumentTitle(
    accountPageQuery.data?.campaign.name
      ? `${accountPageQuery.data.campaign.name} Account Detail | Prospecting Agent`
      : "Account Detail | Prospecting Agent",
  );

  if (accountPageQuery.isPending) {
    return (
      <main className="page-shell">
        <LoadingState
          title="Loading account detail"
          message="Fetching research evidence, score details, and outreach artifacts."
        />
      </main>
    );
  }

  if (accountPageQuery.isError) {
    if (
      accountPageQuery.error instanceof ApiError &&
      accountPageQuery.error.status === 404
    ) {
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
      accountPageQuery.error instanceof Error
        ? accountPageQuery.error.message
        : "Unable to load account details.";

    return (
      <main className="page-shell">
        <Card className="stack-md">
          <div>
            <p className="eyebrow">Account detail</p>
            <h1>Unable to load account</h1>
          </div>
          <ErrorMessage message={message} />
          <div className="form-actions">
            <Link
              className="button button-secondary"
              href={`/campaigns/${campaignId}/results`}
            >
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

  if (!accountPageQuery.data) {
    return (
      <main className="page-shell">
        <ErrorMessage message="Account detail is unavailable." />
      </main>
    );
  }

  const { campaign, detail } = accountPageQuery.data;

  return (
    <main className="page-shell stack-xl">
      <section className="section-heading">
        <div className="stack-sm">
          <div>
            <p className="eyebrow">Account results</p>
            <h1>{campaign.name}</h1>
          </div>
          <p className="lead">
            Inspect the research evidence, timing signals, score breakdown, draft, and
            quality review for a single account.
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
}
