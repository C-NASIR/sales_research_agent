"use client";

import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";

import { ApiError, startCampaignRun } from "@/lib/api";
import type { CampaignStatus } from "@/lib/types";

import { Button } from "../ui/Button";
import { ErrorMessage } from "../ui/ErrorMessage";

type StartRunButtonProps = {
  campaignId: string;
  campaignStatus: CampaignStatus;
  accountCount: number;
};

export function StartRunButton({
  campaignId,
  campaignStatus,
  accountCount,
}: StartRunButtonProps) {
  const router = useRouter();
  const isDisabled = accountCount === 0 || campaignStatus === "draft";

  const mutation = useMutation({
    mutationFn: () => startCampaignRun(campaignId),
    onSuccess: (run) => {
      const path = run.id
        ? `/campaigns/${campaignId}/run?runId=${encodeURIComponent(run.id)}`
        : `/campaigns/${campaignId}/run`;
      router.push(path);
    },
  });

  let buttonText = "Start research run";
  if (accountCount === 0) {
    buttonText = "Upload companies first";
  } else if (campaignStatus === "draft") {
    buttonText = "Campaign is not ready";
  }

  return (
    <div className="stack-sm">
      <Button disabled={isDisabled || mutation.isPending} onClick={() => mutation.mutate()}>
        {mutation.isPending ? "Starting research run..." : buttonText}
      </Button>

      {mutation.isError ? (
        <ErrorMessage
          message={
            mutation.error instanceof ApiError
              ? mutation.error.message
              : "Unable to start research run."
          }
        />
      ) : null}

    </div>
  );
}
