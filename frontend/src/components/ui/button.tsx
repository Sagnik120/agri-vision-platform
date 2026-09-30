"use client";

import { cva, type VariantProps } from "class-variance-authority";
import { Loader2 } from "lucide-react";
import Link from "next/link";
import { useRef, useState } from "react";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  [
    "relative isolate inline-flex shrink-0 items-center justify-center gap-2 overflow-hidden whitespace-nowrap select-none",
    "font-semibold transition-[background-color,color,box-shadow,transform] duration-200 ease-[var(--ease-out-soft)]",
    "active:scale-[0.97] disabled:pointer-events-none disabled:opacity-50",
    "[&_svg]:pointer-events-none [&_svg]:shrink-0",
  ],
  {
    variants: {
      variant: {
        primary:
          "bg-leaf text-primary-foreground shadow-[inset_0_1px_0_rgb(255_255_255/0.14),0_1px_2px_rgb(31_42_36/0.2)] hover:bg-leaf-700",
        accent: "bg-ochre text-ink shadow-[inset_0_1px_0_rgb(255_255_255/0.3)] hover:bg-[#d4a44f]",
        outline: "border border-line-2 bg-surface text-ink hover:border-ink-3/40 hover:bg-paper-2",
        ghost: "text-ink-2 hover:bg-paper-2 hover:text-ink",
        soft: "bg-leaf-50 text-leaf hover:bg-leaf-100",
        link: "text-leaf underline-offset-4 hover:underline",
      },
      size: {
        sm: "h-9 rounded-lg px-3.5 text-sm [&_svg]:size-4",
        md: "h-11 rounded-xl px-5 text-[0.95rem] [&_svg]:size-[1.1rem]",
        lg: "h-13 rounded-2xl px-7 text-base [&_svg]:size-5",
        icon: "size-10 rounded-xl [&_svg]:size-5",
      },
    },
    defaultVariants: { variant: "primary", size: "md" },
  },
);

type Ripple = { id: number; x: number; y: number; size: number };

function useRipple() {
  const [ripples, setRipples] = useState<Ripple[]>([]);
  const next = useRef(0);
  const add = (e: React.PointerEvent<HTMLElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height) * 2;
    const r = { id: next.current++, x: e.clientX - rect.left - size / 2, y: e.clientY - rect.top - size / 2, size };
    setRipples((rs) => [...rs, r]);
    setTimeout(() => setRipples((rs) => rs.filter((x) => x.id !== r.id)), 650);
  };
  const nodes = ripples.map((r) => (
    <span
      key={r.id}
      aria-hidden
      className="pointer-events-none absolute -z-10 animate-[ripple_650ms_ease-out_forwards] rounded-full bg-current opacity-20"
      style={{ left: r.x, top: r.y, width: r.size, height: r.size }}
    />
  ));
  return { add, nodes };
}

type ButtonProps = React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & { loading?: boolean; href?: string };

export function Button({ className, variant, size, loading, href, children, onPointerDown, disabled, ...props }: ButtonProps) {
  const ripple = useRipple();
  const classes = cn(buttonVariants({ variant, size }), className);
  const content = (
    <>
      {ripple.nodes}
      {loading && <Loader2 className="animate-spin" />}
      {children}
    </>
  );

  if (href) {
    return (
      <Link href={href} className={classes} onPointerDown={ripple.add}>
        {content}
      </Link>
    );
  }
  return (
    <button
      className={classes}
      disabled={disabled || loading}
      onPointerDown={(e) => {
        ripple.add(e);
        onPointerDown?.(e);
      }}
      {...props}
    >
      {content}
    </button>
  );
}

export { buttonVariants };
