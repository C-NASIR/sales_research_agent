import { useQuery } from "@tanstack/react-query";

import { CampaignList } from "@/components/campaign/CampaignList";
import { Card } from "@/components/ui/Card";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { LoadingState } from "@/components/ui/LoadingState";
import { Link } from "@/components/ui/Link";
import { useDocumentTitle } from "@/hooks/useDocumentTitle";
import { listCampaigns } from "@/lib/api";

export function CampaignsPage() {
  useDocumentTitle("Campaigns | Prospecting Agent");

  const campaignsQuery = useQuery({
    queryKey: ["campaigns"],
    queryFn: listCampaigns,
    retry: false,
  });

  if (campaignsQuery.isPending) {
    return (
      <main className="page-shell">
        <LoadingState
          title="Loading campaigns"
          message="Fetching campaign setup data from the local API."
        />
      </main>
    );
  }

  if (campaignsQuery.isError) {
    const message =
      campaignsQuery.error instanceof Error
        ? campaignsQuery.error.message
        : "Unable to load campaigns right now.";

    return (
      <main className="page-shell">
        <Card className="stack-md">
          <div>
            <p className="eyebrow">Campaigns</p>
            <h1>Campaign setup workspace</h1>
          </div>
          <ErrorMessage message={message} />
          <Link className="button button-secondary" href="/campaigns/new">
            Create campaign anyway
          </Link>
        </Card>
      </main>
    );
  }

  return (
    <main className="page-shell stack-xl">
      <section className="section-heading">
        <div>
          <p className="eyebrow">Campaigns</p>
          <h1>Campaign setup workspace</h1>
          <p className="lead">
            Create a campaign, upload target companies, and start the first research
            run from the browser.
          </p>
        </div>
        <Link className="button button-primary" href="/campaigns/new">
          Create campaign
        </Link>
      </section>

      <CampaignList campaigns={campaignsQuery.data.campaigns} />
    </main>
  );
}
