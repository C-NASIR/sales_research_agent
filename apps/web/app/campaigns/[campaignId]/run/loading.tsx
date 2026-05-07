import { LoadingState } from "@/components/ui/LoadingState";

export default function CampaignRunLoadingPage() {
  return (
    <main className="page-shell">
      <LoadingState
        title="Loading run progress"
        message="Fetching the latest run record and progress timeline."
      />
    </main>
  );
}
