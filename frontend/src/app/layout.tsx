import type { Metadata, Viewport } from "next";
import { Fraunces, Manrope, Noto_Sans_Devanagari, Tiro_Devanagari_Hindi } from "next/font/google";

import { SplashScreen } from "@/components/brand/splash-screen";
import { AppProviders } from "@/providers/app-providers";

import "./globals.css";

const fraunces = Fraunces({ subsets: ["latin"], axes: ["SOFT", "opsz"], variable: "--font-fraunces", display: "swap" });
const manrope = Manrope({ subsets: ["latin"], variable: "--font-manrope", display: "swap" });
const devaSans = Noto_Sans_Devanagari({ subsets: ["devanagari"], weight: ["400", "500", "600", "700"], variable: "--font-deva-sans", display: "swap" });
const devaSerif = Tiro_Devanagari_Hindi({ subsets: ["devanagari"], weight: "400", variable: "--font-deva-serif", display: "swap" });

export const metadata: Metadata = {
  title: { default: "Agri-Vision — Crop & livestock health", template: "%s · Agri-Vision" },
  description:
    "Offline-first, bilingual AI assistant for crop disease identification and livestock health monitoring for rural farmers.",
  icons: { icon: "/icon.svg" },
};

export const viewport: Viewport = {
  themeColor: "#faf8f3",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${fraunces.variable} ${manrope.variable} ${devaSans.variable} ${devaSerif.variable}`}
      data-scroll-behavior="smooth"
      suppressHydrationWarning
    >
      <body className="relative min-h-dvh">
        <AppProviders>
          <SplashScreen />
          <div className="relative z-10 flex min-h-dvh flex-col">{children}</div>
        </AppProviders>
      </body>
    </html>
  );
}
