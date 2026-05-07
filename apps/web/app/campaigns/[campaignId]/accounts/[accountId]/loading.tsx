import { LoadingState } from "@/components/ui/LoadingState";

export default function AccountDetailLoadingPage() {
  return (
    <main className="page-shell">
      <LoadingState
        title="Loading account detail"
        message="Fetching research evidence, score details, and outreach artifacts."
      />
    </main>
  );
}
