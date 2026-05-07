import { LoadingState } from "@/components/ui/LoadingState";

export default function CampaignsLoadingPage() {
  return (
    <main className="page-shell">
      <LoadingState
        title="Loading campaigns"
        message="Fetching campaign setup data from the local API."
      />
    </main>
  );
}
