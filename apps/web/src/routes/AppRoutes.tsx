import { Route, Routes } from "react-router-dom";

import { AccountDetailPage } from "./AccountDetailPage";
import { CampaignDetailPage } from "./CampaignDetailPage";
import { CampaignResultsPage } from "./CampaignResultsPage";
import { CampaignRunPage } from "./CampaignRunPage";
import { CampaignsPage } from "./CampaignsPage";
import { HomePage } from "./HomePage";
import { NewCampaignPage } from "./NewCampaignPage";
import { NotFoundPage } from "./NotFoundPage";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/campaigns" element={<CampaignsPage />} />
      <Route path="/campaigns/new" element={<NewCampaignPage />} />
      <Route path="/campaigns/:campaignId" element={<CampaignDetailPage />} />
      <Route path="/campaigns/:campaignId/run" element={<CampaignRunPage />} />
      <Route
        path="/campaigns/:campaignId/results"
        element={<CampaignResultsPage />}
      />
      <Route
        path="/campaigns/:campaignId/accounts/:accountId"
        element={<AccountDetailPage />}
      />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
