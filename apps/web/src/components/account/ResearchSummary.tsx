import { formatConfidence } from "@/lib/format";
import type { ResearchReport } from "@/lib/types";

import { Card } from "../ui/Card";

type ResearchSummaryProps = {
  report: ResearchReport | null;
};

export function ResearchSummary({ report }: ResearchSummaryProps) {
  if (!report) {
    return (
      <Card className="stack-md">
        <h2>Research summary</h2>
        <p>No research report is available for this account.</p>
      </Card>
    );
  }

  return (
    <Card className="stack-md">
      <h2>Research summary</h2>
      <dl className="detail-grid">
        <div>
          <dt>Company summary</dt>
          <dd>{report.company_summary ?? "Missing"}</dd>
        </div>
        <div>
          <dt>Business model</dt>
          <dd>{report.business_model ?? "Missing"}</dd>
        </div>
        <div>
          <dt>Confidence</dt>
          <dd>{formatConfidence(report.confidence)}</dd>
        </div>
      </dl>

      <div className="detail-section-block">
        <h3>Fit claims</h3>
        {report.fit_claims.length ? (
          <ul className="detail-list">
            {report.fit_claims.map((item, index) => (
              <li key={`${item.claim}-${index}`}>
                <strong>{item.claim}</strong>
                {item.evidence ? `: ${item.evidence}` : ""}
              </li>
            ))}
          </ul>
        ) : (
          <p className="supporting-text">No fit claims were saved.</p>
        )}
      </div>

      <div className="detail-section-block">
        <h3>Research risks</h3>
        {report.risks.length ? (
          <ul className="detail-list">
            {report.risks.map((risk, index) => (
              <li key={`${risk.risk}-${index}`}>
                <strong>{risk.risk}</strong>
                {risk.reason ? `: ${risk.reason}` : ""}
              </li>
            ))}
          </ul>
        ) : (
          <p className="supporting-text">No research risks were saved.</p>
        )}
      </div>
    </Card>
  );
}
