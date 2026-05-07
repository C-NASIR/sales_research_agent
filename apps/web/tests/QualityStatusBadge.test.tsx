import React from "react";
import { render, screen } from "@testing-library/react";

import { QualityStatusBadge } from "@/components/results/QualityStatusBadge";

describe("QualityStatusBadge", () => {
  it("renders flagged quality state", () => {
    render(<QualityStatusBadge status="flagged" />);

    expect(screen.getByText("Flagged")).toBeInTheDocument();
  });

  it("falls back to missing when status is absent", () => {
    render(<QualityStatusBadge status={null} />);

    expect(screen.getByText("Missing")).toBeInTheDocument();
  });
});
