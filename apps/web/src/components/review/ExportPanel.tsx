"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { ApiError, createCampaignExports } from "@/lib/api";
import { formatStatus } from "@/lib/format";
import type { ReviewStatus } from "@/lib/types";

import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { ErrorMessage } from "../ui/ErrorMessage";

type ExportPanelProps = {
  campaignId: string;
  approvedAccountCount: number;
};

const OPTIONS: ReviewStatus[] = [
  "approved",
  "unreviewed",
  "needs_edit",
  "not_enough_evidence",
  "rejected",
];

export function ExportPanel({
  campaignId,
  approvedAccountCount,
}: ExportPanelProps) {
  const queryClient = useQueryClient();
  const [selectedStatuses, setSelectedStatuses] = useState<ReviewStatus[]>([
    "approved",
  ]);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (statuses: ReviewStatus[]) =>
      createCampaignExports(campaignId, { include_review_statuses: statuses }),
    onSuccess: async () => {
      setSuccessMessage("Export files created.");
      await queryClient.invalidateQueries({
        queryKey: ["campaign-exports", campaignId],
      });
    },
  });

  const hint =
    approvedAccountCount === 0 && selectedStatuses.length === 1 && selectedStatuses[0] === "approved"
      ? "Approve at least one account before creating the default export."
      : "Only approved accounts are exported by default.";

  const sortedSelections = useMemo(
    () => OPTIONS.filter((status) => selectedStatuses.includes(status)),
    [selectedStatuses],
  );

  return (
    <div className="stack-xl">
      <Card className="stack-md">
        <div className="card-row">
          <div>
            <h2>Create export</h2>
            <p className="supporting-text">{hint}</p>
          </div>
          <span className="detail-tag">
            Selected: {sortedSelections.map((status) => formatStatus(status)).join(", ")}
          </span>
        </div>

        <div className="checkbox-grid">
          {OPTIONS.map((status) => {
            const checked = selectedStatuses.includes(status);
            return (
              <label className="checkbox-row" key={status}>
                <input
                  checked={checked}
                  onChange={(event) => {
                    setSuccessMessage(null);
                    setSelectedStatuses((current) => {
                      if (event.target.checked) {
                        return [...current, status];
                      }
                      return current.filter((item) => item !== status);
                    });
                  }}
                  type="checkbox"
                />
                <span>{formatStatus(status)}</span>
              </label>
            );
          })}
        </div>

        {successMessage ? <p className="success-message">{successMessage}</p> : null}

        {mutation.isError ? (
          <ErrorMessage
            message={
              mutation.error instanceof ApiError
                ? mutation.error.message
                : "Unable to create exports."
            }
          />
        ) : null}

        <Button
          disabled={!selectedStatuses.length || mutation.isPending}
          onClick={() => {
            setSuccessMessage(null);
            mutation.mutate(selectedStatuses);
          }}
        >
          {mutation.isPending ? "Creating exports..." : "Create export"}
        </Button>
      </Card>
    </div>
  );
}
