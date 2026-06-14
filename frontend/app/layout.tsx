import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/shared/Navbar";
import { Providers } from "@/lib/swr-config";

export const metadata: Metadata = {
  title: "Zeham Security Monitor",
  description: "On-chain AI security monitoring dashboard for Mantle contracts."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <Providers>
          <Navbar />
          <main>{children}</main>
        </Providers>
      </body>
    </html>
  );
}
