import type { OutreachDraft, ResearchReport } from "@/lib/types";

import { Card } from "../ui/Card";

type RiskListProps = {
  researchReport: ResearchReport | null;
  outreachDraft: OutreachDraft | null;
};

export function RiskList({ researchReport, outreachDraft }: RiskListProps) {
  const researchRisks = researchReport?.risks ?? [];
  const outreachRisks = outreachDraft?.risk_notes ?? [];

  return (
    <Card className="stack-md">
      <h2>Risks and uncertainty</h2>
      {researchRisks.length || outreachRisks.length ? (
        <div className="risk-grid">
          <div className="detail-section-block">
            <h3>Research risks</h3>
            {researchRisks.length ? (
              <ul className="detail-list">
                {researchRisks.map((risk, index) => (
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
          <div className="detail-section-block">
            <h3>Outreach risks</h3>
            {outreachRisks.length ? (
              <ul className="detail-list">
                {outreachRisks.map((risk, index) => (
                  <li key={`${risk}-${index}`}>{risk}</li>
                ))}
              </ul>
            ) : (
              <p className="supporting-text">No outreach risks were saved.</p>
            )}
          </div>
        </div>
      ) : (
        <p>No major risks or uncertainty notes were saved.</p>
      )}
    </Card>
  );
}
