import React from "react";
import { render, screen } from "@testing-library/react";

import { ScorePill } from "@/components/results/ScorePill";

describe("ScorePill", () => {
  it("renders a strong score state", () => {
    render(<ScorePill score={88} />);

    expect(screen.getByText("88")).toBeInTheDocument();
    expect(screen.getByText("Strong")).toBeInTheDocument();
  });

  it("renders the missing state", () => {
    render(<ScorePill score={null} />);

    expect(screen.getByText("--")).toBeInTheDocument();
    expect(screen.getByText("Missing")).toBeInTheDocument();
  });
});
