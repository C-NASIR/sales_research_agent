import Link from "next/link";

import { CampaignList } from "@/components/campaign/CampaignList";
import { Card } from "@/components/ui/Card";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { listCampaigns } from "@/lib/api";

export default async function CampaignsPage() {
  try {
    const { campaigns } = await listCampaigns();

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

        <CampaignList campaigns={campaigns} />
      </main>
    );
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Unable to load campaigns right now.";

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
}
