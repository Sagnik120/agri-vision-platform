"use client";

import { Seedling } from "@/components/brand/illustrations";
import { cn } from "@/lib/utils";

export function EmptyState({ title, body, action, className }: { title: string; body?: string; action?: React.ReactNode; className?: string }) {
  return (
    <div className={cn("flex flex-col items-center rounded-2xl border border-dashed border-line-2 bg-surface/50 px-6 py-12 text-center", className)}>
      <Seedling />
      <h3 className="mt-3 text-2xl font-medium">{title}</h3>
      {body && <p className="mt-1.5 max-w-sm text-ink-2">{body}</p>}
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}

export function ErrorState({ message, onRetry, retryLabel }: { message: string; onRetry?: () => void; retryLabel?: string }) {
  return (
    <div role="alert" className="rounded-2xl border border-[#eccabf] bg-brick-50 px-5 py-4 text-sm text-brick">
      <p className="font-semibold">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="mt-2 font-bold underline underline-offset-4">
          {retryLabel}
        </button>
      )}
    </div>
  );
}
