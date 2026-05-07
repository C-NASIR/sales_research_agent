import type { UploadReportResponse } from "@/lib/types";

import { Card } from "../ui/Card";

type CsvUploadSummaryProps = {
  report: UploadReportResponse;
};

export function CsvUploadSummary({ report }: CsvUploadSummaryProps) {
  return (
    <Card className="stack-md">
      <div className="summary-grid">
        <div>
          <span className="summary-label">Valid rows</span>
          <strong>{report.valid_rows}</strong>
        </div>
        <div>
          <span className="summary-label">Invalid rows</span>
          <strong>{report.invalid_rows}</strong>
        </div>
        <div>
          <span className="summary-label">Duplicate rows</span>
          <strong>{report.duplicate_rows}</strong>
        </div>
        <div>
          <span className="summary-label">Created accounts</span>
          <strong>{report.created_accounts}</strong>
        </div>
      </div>

      {report.invalid.length > 0 ? (
        <div className="stack-sm">
          <h3>Invalid rows</h3>
          <ul className="detail-list">
            {report.invalid.map((row) => (
              <li key={`${row.row_number}-${row.reason}`}>
                Row {row.row_number}: {row.reason}
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {report.duplicates.length > 0 ? (
        <div className="stack-sm">
          <h3>Duplicate rows</h3>
          <ul className="detail-list">
            {report.duplicates.map((row) => (
              <li key={`${row.row_number}-${row.domain}`}>
                Row {row.row_number}: {row.domain}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </Card>
  );
}
