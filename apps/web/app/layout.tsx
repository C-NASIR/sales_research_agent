import type { Metadata } from "next";
import type { ReactNode } from "react";

import Providers from "./providers";

import "./globals.css";

export const metadata: Metadata = {
  title: "Prospecting Agent",
  description: "AI sales research workspace powered by Deep Agents",
};

type RootLayoutProps = Readonly<{
  children: ReactNode;
}>;

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
