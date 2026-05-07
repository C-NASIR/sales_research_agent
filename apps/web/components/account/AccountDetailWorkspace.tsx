"use client";

import { useQuery } from "@tanstack/react-query";

import { getAccountDetail } from "@/lib/api";
import type { AccountDetailResponse, OutreachDraft, ReviewStatusResponse } from "@/lib/types";

import { EvidenceList } from "./EvidenceList";
import { OutreachPreview } from "./OutreachPreview";
import { QualityReviewPanel } from "./QualityReviewPanel";
import { ResearchSummary } from "./ResearchSummary";
import { RiskList } from "./RiskList";
import { ScoreBreakdown } from "./ScoreBreakdown";
import { SignalList } from "./SignalList";
import { DraftEditor } from "../review/DraftEditor";
import { ReviewStatusControls } from "../review/ReviewStatusControls";
import { ErrorMessage } from "../ui/ErrorMessage";
import { LoadingState } from "../ui/LoadingState";

type AccountDetailWorkspaceProps = {
  campaignId: string;
  accountId: string;
  initialDetail: AccountDetailResponse;
};

export function AccountDetailWorkspace({
  campaignId,
  accountId,
  initialDetail,
}: AccountDetailWorkspaceProps) {
  const detailQuery = useQuery({
    queryKey: ["account-detail", campaignId, accountId],
    queryFn: () => getAccountDetail(campaignId, accountId),
    initialData: initialDetail,
  });

  if (detailQuery.isPending) {
    return (
      <LoadingState
        title="Loading account detail"
        message="Fetching the latest account research and review data."
      />
    );
  }

  if (detailQuery.isError || !detailQuery.data) {
    return (
      <ErrorMessage
        message={
          detailQuery.error instanceof Error
            ? detailQuery.error.message
            : "Unable to load account detail."
        }
      />
    );
  }

  const detail = detailQuery.data;

  async function handleReviewUpdated(_: ReviewStatusResponse) {
    await detailQuery.refetch();
  }

  async function handleDraftUpdated(_: OutreachDraft) {
    await detailQuery.refetch();
  }

  return (
    <div className="stack-xl">
      <ReviewStatusControls
        accountId={accountId}
        campaignId={campaignId}
        currentStatus={detail.account.review_status}
        onUpdated={handleReviewUpdated}
      />

      <div className="account-detail-grid">
        <ResearchSummary report={detail.research_report} />
        <SignalList report={detail.signal_report} />
      </div>

      <EvidenceList report={detail.research_report} />
      <ScoreBreakdown report={detail.score_report} />
      <OutreachPreview draft={detail.outreach_draft} />
      <DraftEditor
        accountId={accountId}
        campaignId={campaignId}
        draft={detail.outreach_draft}
        onUpdated={handleDraftUpdated}
      />
      <QualityReviewPanel review={detail.quality_review} />
      <RiskList
        researchReport={detail.research_report}
        outreachDraft={detail.outreach_draft}
      />
    </div>
  );
}
