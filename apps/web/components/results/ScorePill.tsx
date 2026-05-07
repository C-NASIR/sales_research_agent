import { formatScore } from "@/lib/format";

type ScorePillProps = {
  score: number | null | undefined;
};

function getScoreCategory(score: number | null | undefined): {
  label: string;
  className: string;
} {
  if (score === null || score === undefined) {
    return { label: "Missing", className: "score-missing" };
  }

  if (score >= 80) {
    return { label: "Strong", className: "score-strong" };
  }

  if (score >= 60) {
    return { label: "Good", className: "score-good" };
  }

  if (score >= 40) {
    return { label: "Weak", className: "score-weak" };
  }

  return { label: "Poor", className: "score-poor" };
}

export function ScorePill({ score }: ScorePillProps) {
  const category = getScoreCategory(score);
  const scoreLabel = score === null || score === undefined ? "--" : formatScore(score);

  return (
    <span className={`score-pill ${category.className}`}>
      <strong>{scoreLabel}</strong>
      <span>{category.label}</span>
    </span>
  );
}
