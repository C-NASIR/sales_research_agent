"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { ApiError, updateAccountReviewStatus } from "@/lib/api";
import { formatStatus } from "@/lib/format";
import type { ReviewStatus, ReviewStatusResponse } from "@/lib/types";

import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { ErrorMessage } from "../ui/ErrorMessage";

type ReviewStatusControlsProps = {
  campaignId: string;
  accountId: string;
  currentStatus: ReviewStatus;
  onUpdated: (response: ReviewStatusResponse) => void;
};

const OPTIONS: Array<{ label: string; value: ReviewStatus }> = [
  { label: "Approve", value: "approved" },
  { label: "Reject", value: "rejected" },
  { label: "Needs edit", value: "needs_edit" },
  { label: "Not enough evidence", value: "not_enough_evidence" },
  { label: "Reset to unreviewed", value: "unreviewed" },
];

export function ReviewStatusControls({
  campaignId,
  accountId,
  currentStatus,
  onUpdated,
}: ReviewStatusControlsProps) {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: (reviewStatus: ReviewStatus) =>
      updateAccountReviewStatus(campaignId, accountId, reviewStatus),
    onSuccess: async (response) => {
      onUpdated(response);
      await queryClient.invalidateQueries({
        queryKey: ["campaign-results", campaignId],
      });
      await queryClient.invalidateQueries({
        queryKey: ["account-detail", campaignId, accountId],
      });
    },
  });

  return (
    <Card className="stack-md">
      <div className="stack-sm">
        <div className="card-row">
          <div>
            <h2>Review status</h2>
            <p className="supporting-text">
              Decide whether this account should be exported, edited, or excluded.
            </p>
          </div>
          <span className="detail-tag">Current: {formatStatus(currentStatus)}</span>
        </div>
        <div className="review-button-grid">
          {OPTIONS.map((option) => (
            <Button
              className="review-button"
              disabled={mutation.isPending}
              key={option.value}
              onClick={() => mutation.mutate(option.value)}
              variant={currentStatus === option.value ? "primary" : "ghost"}
            >
              {mutation.isPending && mutation.variables === option.value
                ? "Saving..."
                : option.label}
            </Button>
          ))}
        </div>
      </div>

      {mutation.isError ? (
        <ErrorMessage
          message={
            mutation.error instanceof ApiError
              ? mutation.error.message
              : "Unable to update review status."
          }
        />
      ) : null}
    </Card>
  );
}
