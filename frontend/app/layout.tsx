import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "ReachGTM — AI-Powered Go-To-Market Strategy",
  description:
    "Generate complete GTM strategies with AI agents. Research, strategy, content — in minutes, not weeks.",
  keywords: ["GTM", "go-to-market", "AI", "strategy", "content generation"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans antialiased`} suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
