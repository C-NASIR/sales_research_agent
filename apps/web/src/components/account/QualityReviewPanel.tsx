import type { QualityReview } from "@/lib/types";

import { QualityStatusBadge } from "../results/QualityStatusBadge";
import { Card } from "../ui/Card";

type QualityReviewPanelProps = {
  review: QualityReview | null;
};

export function QualityReviewPanel({ review }: QualityReviewPanelProps) {
  if (!review) {
    return (
      <Card className="stack-md">
        <h2>Quality review</h2>
        <p>No quality review is available for this account.</p>
      </Card>
    );
  }

  return (
    <Card className="stack-md">
      <div className="card-row">
        <div>
          <h2>Quality review</h2>
          <p className="supporting-text">
            Read-only notes from the quality review step.
          </p>
        </div>
        <QualityStatusBadge status={review.quality_status} />
      </div>

      <div className="detail-section-block">
        <h3>Issues</h3>
        {review.issues.length ? (
          <ul className="detail-list">
            {review.issues.map((issue, index) => (
              <li key={`${issue}-${index}`}>{issue}</li>
            ))}
          </ul>
        ) : (
          <p>No quality issues were found.</p>
        )}
      </div>

      <div className="detail-section-block">
        <h3>Blocked reasons</h3>
        {review.blocked_reasons.length ? (
          <ul className="detail-list">
            {review.blocked_reasons.map((reason, index) => (
              <li key={`${reason}-${index}`}>{reason}</li>
            ))}
          </ul>
        ) : (
          <p className="supporting-text">No blocked reasons were recorded.</p>
        )}
      </div>

      <div className="detail-section-block">
        <h3>Recommended edits</h3>
        {review.recommended_edits.length ? (
          <ul className="detail-list">
            {review.recommended_edits.map((edit, index) => (
              <li key={`${edit}-${index}`}>{edit}</li>
            ))}
          </ul>
        ) : (
          <p className="supporting-text">No recommended edits were recorded.</p>
        )}
      </div>
    </Card>
  );
}
