type QualityStatusBadgeProps = {
  status: string | null | undefined;
};

function getQualityMeta(status: string | null | undefined): {
  label: string;
  className: string;
} {
  switch (status) {
    case "approved_by_reviewer":
      return { label: "Approved", className: "quality-approved" };
    case "flagged":
      return { label: "Flagged", className: "quality-flagged" };
    case "blocked":
      return { label: "Blocked", className: "quality-blocked" };
    case "pending":
      return { label: "Pending", className: "quality-pending" };
    default:
      return { label: "Missing", className: "quality-missing" };
  }
}

export function QualityStatusBadge({ status }: QualityStatusBadgeProps) {
  const meta = getQualityMeta(status);

  return <span className={`quality-badge ${meta.className}`}>{meta.label}</span>;
}
