import type { ReactNode } from "react";
import { BrowserRouter } from "react-router-dom";

import { AppProviders } from "./providers/AppProviders";
import { AppRoutes } from "./routes/AppRoutes";

type AppProps = {
  router?: ReactNode;
};

export default function App({ router }: AppProps) {
  return (
    <AppProviders>
      {router ?? (
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      )}
    </AppProviders>
  );
}
