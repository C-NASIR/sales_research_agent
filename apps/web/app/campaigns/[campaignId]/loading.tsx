import { LoadingState } from "@/components/ui/LoadingState";

export default function CampaignDetailLoadingPage() {
  return (
    <main className="page-shell">
      <LoadingState
        title="Loading campaign"
        message="Fetching campaign details, uploaded accounts, and setup controls."
      />
    </main>
  );
}
