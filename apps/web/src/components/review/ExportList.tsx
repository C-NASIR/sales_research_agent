import { API_BASE_URL } from "@/lib/api";
import { formatDateTime, formatExportType } from "@/lib/format";
import type { ExportFile } from "@/lib/types";

import { Card } from "../ui/Card";

type ExportListProps = {
  exports: ExportFile[];
};

function getDownloadUrl(downloadUrl: string): string {
  if (downloadUrl.startsWith("http://") || downloadUrl.startsWith("https://")) {
    return downloadUrl;
  }

  return `${API_BASE_URL}${downloadUrl.startsWith("/") ? downloadUrl : `/${downloadUrl}`}`;
}

export function ExportList({ exports }: ExportListProps) {
  return (
    <Card className="stack-md">
      <div className="card-row">
        <div>
          <h2>Exports</h2>
          <p className="supporting-text">
            Download the latest generated files for this campaign.
          </p>
        </div>
        <span className="count-pill">{exports.length} files</span>
      </div>

      {exports.length ? (
        <div className="export-list">
          {exports.map((exportFile) => (
            <div className="export-row" key={exportFile.id}>
              <div className="stack-sm">
                <strong>{formatExportType(exportFile.export_type)}</strong>
                <span className="supporting-text">
                  Created {formatDateTime(exportFile.created_at)}
                </span>
              </div>
              <a
                className="button button-secondary inline-button"
                href={getDownloadUrl(exportFile.download_url)}
              >
                Download
              </a>
            </div>
          ))}
        </div>
      ) : (
        <p className="supporting-text">No export files have been created yet.</p>
      )}
    </Card>
  );
}
