import { Link } from "@/components/ui/Link";
import { useDocumentTitle } from "@/hooks/useDocumentTitle";

const mvpSteps = [
  "Create campaign",
  "Upload companies",
  "Start research",
  "Review results later",
  "Export prospects later",
];

export function HomePage() {
  useDocumentTitle("Prospecting Agent");

  return (
    <main className="page-shell">
      <section className="hero-card">
        <p className="eyebrow">Phase 10 demo workspace</p>
        <h1>Prospecting Agent</h1>
        <p className="lead">AI sales research workspace powered by Deep Agents</p>
        <div className="hero-actions">
          <Link className="button button-primary" href="/campaigns">
            Open campaigns
          </Link>
        </div>
      </section>

      <section className="flow-card">
        <h2>MVP flow</h2>
        <ol>
          {mvpSteps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </section>
    </main>
  );
}
