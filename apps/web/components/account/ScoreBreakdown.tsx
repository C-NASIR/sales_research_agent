import { formatScore } from "@/lib/format";
import type { ScoreReport } from "@/lib/types";

import { Card } from "../ui/Card";

type ScoreBreakdownProps = {
  report: ScoreReport | null;
};

export function ScoreBreakdown({ report }: ScoreBreakdownProps) {
  if (!report) {
    return (
      <Card className="stack-md">
        <h2>Score breakdown</h2>
        <p>No score report is available for this account.</p>
      </Card>
    );
  }

  return (
    <Card className="stack-md">
      <h2>Score breakdown</h2>
      <div className="summary-grid">
        <div>
          <span className="summary-label">Overall score</span>
          <strong>{formatScore(report.overall_score)}</strong>
        </div>
        <div>
          <span className="summary-label">Fit score</span>
          <strong>{formatScore(report.fit_score)}</strong>
        </div>
        <div>
          <span className="summary-label">Timing score</span>
          <strong>{formatScore(report.timing_score)}</strong>
        </div>
        <div>
          <span className="summary-label">Confidence score</span>
          <strong>{formatScore(report.confidence_score)}</strong>
        </div>
        <div>
          <span className="summary-label">Persona score</span>
          <strong>{formatScore(report.persona_score)}</strong>
        </div>
      </div>

      <div className="detail-section-block">
        <h3>Score explanation</h3>
        <p>{report.score_explanation ?? "Missing"}</p>
      </div>

      <div className="detail-section-block">
        <h3>Raw breakdown</h3>
        <pre className="json-block">
          {JSON.stringify(report.score_breakdown ?? {}, null, 2)}
        </pre>
      </div>
    </Card>
  );
}
