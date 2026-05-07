import React from "react";
import { render, screen } from "@testing-library/react";

import { CampaignStatusBadge } from "@/components/campaign/CampaignStatusBadge";

describe("CampaignStatusBadge", () => {
  it("renders a formatted label", () => {
    render(<CampaignStatusBadge status="partial" />);

    expect(screen.getByText("Partial")).toBeInTheDocument();
  });
});
