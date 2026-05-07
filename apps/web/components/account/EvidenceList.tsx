import { formatConfidence, formatStatus } from "@/lib/format";
import type { ResearchReport } from "@/lib/types";

import { Card } from "../ui/Card";

type EvidenceListProps = {
  report: ResearchReport | null;
};

export function EvidenceList({ report }: EvidenceListProps) {
  if (!report) {
    return (
      <Card className="stack-md">
        <h2>Research evidence</h2>
        <p>No research report is available for this account.</p>
      </Card>
    );
  }

  return (
    <Card className="stack-md">
      <h2>Research evidence</h2>
      {report.evidence.length ? (
        <div className="detail-card-grid">
          {report.evidence.map((item, index) => (
            <article className="detail-card" key={`${item.claim}-${index}`}>
              <div className="stack-sm">
                <div>
                  <p className="summary-label">Claim</p>
                  <strong>{item.claim}</strong>
                </div>
                <div>
                  <p className="summary-label">Evidence</p>
                  <p>{item.evidence}</p>
                </div>
                <div className="detail-metadata">
                  <span>Confidence: {formatConfidence(item.confidence)}</span>
                  <span>Type: {formatStatus(item.evidence_type)}</span>
                </div>
                {item.source_url ? (
                  <a
                    className="source-link"
                    href={item.source_url}
                    rel="noreferrer"
                    target="_blank"
                  >
                    {item.source_title ?? item.source_url}
                  </a>
                ) : (
                  <p className="supporting-text">No source URL saved.</p>
                )}
              </div>
            </article>
          ))}
        </div>
      ) : (
        <p>No supporting evidence items were saved.</p>
      )}
    </Card>
  );
}
