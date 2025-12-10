import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "API Control Center",
  description: "Control panel for Node.js, FastAPI, and C# demo APIs",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
