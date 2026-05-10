import { EmptyState } from "@/components/ui/EmptyState";
import { Link } from "@/components/ui/Link";
import { useDocumentTitle } from "@/hooks/useDocumentTitle";

export function NotFoundPage() {
  useDocumentTitle("Not Found | Prospecting Agent");

  return (
    <main className="page-shell">
      <div className="card stack-md">
        <EmptyState
          title="Page not found"
          message="The requested route does not exist in the Vite workspace."
        />
        <Link className="button button-secondary" href="/campaigns">
          Open campaigns
        </Link>
      </div>
    </main>
  );
}
