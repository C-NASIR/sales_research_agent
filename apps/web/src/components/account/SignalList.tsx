import { formatConfidence, formatStatus } from "@/lib/format";
import type { SignalReport } from "@/lib/types";

import { Card } from "../ui/Card";

type SignalListProps = {
  report: SignalReport | null;
};

export function SignalList({ report }: SignalListProps) {
  if (!report) {
    return (
      <Card className="stack-md">
        <h2>Timing signals</h2>
        <p>No signal report is available for this account.</p>
      </Card>
    );
  }

  return (
    <Card className="stack-md">
      <h2>Timing signals</h2>
      {report.why_now ? (
        <div className="detail-section-block">
          <p className="summary-label">Why now</p>
          <p>{report.why_now}</p>
        </div>
      ) : null}

      {report.signals.length ? (
        <div className="detail-card-grid">
          {report.signals.map((signal, index) => (
            <article className="detail-card" key={`${signal.type}-${index}`}>
              <div className="stack-sm">
                <div>
                  <p className="summary-label">Signal type</p>
                  <strong>{formatStatus(signal.type)}</strong>
                </div>
                <div>
                  <p className="summary-label">Description</p>
                  <p>{signal.description}</p>
                </div>
                {signal.why_it_matters ? (
                  <div>
                    <p className="summary-label">Why it matters</p>
                    <p>{signal.why_it_matters}</p>
                  </div>
                ) : null}
                <div className="detail-metadata">
                  <span>Confidence: {formatConfidence(signal.confidence)}</span>
                </div>
                {signal.source_url ? (
                  <a
                    className="source-link"
                    href={signal.source_url}
                    rel="noreferrer"
                    target="_blank"
                  >
                    View source
                  </a>
                ) : (
                  <p className="supporting-text">No source URL saved.</p>
                )}
              </div>
            </article>
          ))}
        </div>
      ) : (
        <p>No clear timing signals were found.</p>
      )}
    </Card>
  );
}
