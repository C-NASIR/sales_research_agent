const mvpSteps = [
  "Create campaign",
  "Upload companies",
  "Run research",
  "Review accounts",
  "Export prospects",
];

export default function HomePage() {
  return (
    <main className="page-shell">
      <section className="hero-card">
        <p className="eyebrow">Phase 0 foundation is running</p>
        <h1>Prospecting Agent</h1>
        <p className="lead">AI sales research workspace powered by Deep Agents</p>
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
