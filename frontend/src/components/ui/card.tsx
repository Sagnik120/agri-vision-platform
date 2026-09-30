import { cn } from "@/lib/utils";

export function Card({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      className={cn("rounded-2xl border border-line bg-surface shadow-[var(--shadow-soft)]", className)}
      {...props}
    />
  );
}

export function Badge({
  tone = "neutral",
  className,
  ...props
}: React.ComponentProps<"span"> & { tone?: "neutral" | "leaf" | "ochre" | "amber" | "brick" | "ink" }) {
  const tones = {
    neutral: "bg-paper-2 text-ink-2 border-line",
    leaf: "bg-leaf-50 text-leaf border-leaf-100",
    ochre: "bg-ochre-50 text-ochre-700 border-ochre-100",
    amber: "bg-amber-50 text-amber border-[#f1dfb4]",
    brick: "bg-brick-50 text-brick border-[#eccabf]",
    ink: "bg-ink text-paper border-ink",
  };
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold whitespace-nowrap [&_svg]:size-3.5",
        tones[tone],
        className,
      )}
      {...props}
    />
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("skeleton", className)} aria-hidden />;
}
