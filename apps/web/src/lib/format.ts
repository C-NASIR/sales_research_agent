export function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return "Not available";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function formatEventType(type: string): string {
  return type
    .split("_")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function formatScore(score: number | null | undefined): string {
  if (score === null || score === undefined) {
    return "Missing";
  }

  return `${Math.round(score)}`;
}

export function formatStatus(status: string | null | undefined): string {
  if (!status) {
    return "Missing";
  }

  return status
    .split("_")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function formatConfidence(
  value: number | string | null | undefined,
): string {
  if (value === null || value === undefined || value === "") {
    return "Missing";
  }

  if (typeof value === "number") {
    const normalized = value > 0 && value <= 1 ? value * 100 : value;
    return `${Math.round(normalized)}%`;
  }

  return formatStatus(value);
}

export function truncateText(value: string, maxLength: number): string {
  if (value.length <= maxLength) {
    return value;
  }

  return `${value.slice(0, Math.max(0, maxLength - 3)).trimEnd()}...`;
}

export function formatExportType(value: string): string {
  switch (value) {
    case "prospects_csv":
      return "Prospects CSV";
    case "campaign_report_md":
      return "Campaign report";
    case "archive_json":
      return "Archive JSON";
    default:
      return formatStatus(value);
  }
}
