import { LoadingState } from "@/components/ui/LoadingState";

export default function CampaignResultsLoadingPage() {
  return (
    <main className="page-shell">
      <LoadingState
        title="Loading results"
        message="Fetching ranked account results and campaign summary data."
      />
    </main>
  );
}
