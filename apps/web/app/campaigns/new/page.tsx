import Link from "next/link";

import { CampaignForm } from "@/components/campaign/CampaignForm";
import { Card } from "@/components/ui/Card";

export default function NewCampaignPage() {
  return (
    <main className="page-shell stack-xl">
      <section className="stack-md">
        <p className="eyebrow">Create campaign</p>
        <h1>Set up a new research campaign</h1>
        <p className="lead">
          Start with the campaign brief. You can upload companies and launch the first
          run on the next page.
        </p>
        <Link className="button button-ghost inline-button" href="/campaigns">
          Back to campaign list
        </Link>
      </section>

      <Card>
        <CampaignForm />
      </Card>
    </main>
  );
}
