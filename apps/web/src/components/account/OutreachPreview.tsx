import type { OutreachDraft } from "@/lib/types";

import { Card } from "../ui/Card";

type OutreachPreviewProps = {
  draft: OutreachDraft | null;
};

export function OutreachPreview({ draft }: OutreachPreviewProps) {
  if (!draft) {
    return (
      <Card className="stack-md">
        <h2>Outreach draft</h2>
        <p>No outreach draft is available for this account.</p>
      </Card>
    );
  }

  return (
    <Card className="stack-md">
      <h2>Outreach draft</h2>
      <dl className="detail-grid">
        <div>
          <dt>Subject</dt>
          <dd>{draft.subject ?? "Missing"}</dd>
        </div>
        <div>
          <dt>Sales angle</dt>
          <dd>{draft.sales_angle ?? "Missing"}</dd>
        </div>
        <div>
          <dt>Personalization source</dt>
          <dd>{draft.personalization_source ?? "Missing"}</dd>
        </div>
        <div>
          <dt>Personalization source URL</dt>
          <dd>
            {draft.personalization_source_url ? (
              <a
                className="source-link"
                href={draft.personalization_source_url}
                rel="noreferrer"
                target="_blank"
              >
                View source
              </a>
            ) : (
              "Missing"
            )}
          </dd>
        </div>
      </dl>

      <div className="detail-section-block">
        <h3>Draft body</h3>
        <div className="outreach-preview-body">{draft.body ?? "Missing"}</div>
      </div>

      <div className="detail-section-block">
        <h3>Risk notes</h3>
        {draft.risk_notes.length ? (
          <ul className="detail-list">
            {draft.risk_notes.map((note, index) => (
              <li key={`${note}-${index}`}>{note}</li>
            ))}
          </ul>
        ) : (
          <p className="supporting-text">No outreach risk notes were saved.</p>
        )}
      </div>
    </Card>
  );
}
