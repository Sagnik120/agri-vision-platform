"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MotionConfig } from "motion/react";
import { useState } from "react";
import { Toaster } from "sonner";

import { LanguageProvider } from "./language-provider";
import { SessionProvider } from "./session-provider";

export function AppProviders({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: { staleTime: 30_000, retry: 1, refetchOnWindowFocus: false },
        },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>
      <LanguageProvider>
        <SessionProvider>
          {/* "user" = honour the OS reduced-motion setting for every motion component */}
          <MotionConfig reducedMotion="user">{children}</MotionConfig>
          <Toaster
            position="top-center"
            toastOptions={{
              classNames: {
                toast: "!bg-surface !border-line !text-ink !rounded-xl !shadow-[var(--shadow-lift)] !font-sans",
                description: "!text-ink-3",
              },
            }}
          />
        </SessionProvider>
      </LanguageProvider>
    </QueryClientProvider>
  );
}
