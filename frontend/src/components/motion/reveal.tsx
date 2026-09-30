"use client";

import { animate, motion, useInView, useMotionValue, useTransform, type HTMLMotionProps, type Variants } from "motion/react";
import { useEffect, useRef } from "react";

const EASE = [0.22, 1, 0.36, 1] as const;

/** Fades + lifts content in as it scrolls into view (once). */
export function Reveal({
  delay = 0,
  y = 18,
  blur = true,
  ...props
}: HTMLMotionProps<"div"> & { delay?: number; y?: number; blur?: boolean }) {
  return (
    <motion.div
      initial={{ opacity: 0, y, filter: blur ? "blur(6px)" : "blur(0px)" }}
      whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.7, ease: EASE, delay }}
      {...props}
    />
  );
}

const container: Variants = {
  hidden: {},
  show: (stagger: number = 0.08) => ({ transition: { staggerChildren: stagger, delayChildren: 0.05 } }),
};

export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 14, filter: "blur(4px)" },
  show: { opacity: 1, y: 0, filter: "blur(0px)", transition: { duration: 0.55, ease: EASE } },
};

/** Children using `variants={staggerItem}` animate in one after another. */
export function Stagger({
  stagger = 0.08,
  inView = true,
  ...props
}: HTMLMotionProps<"div"> & { stagger?: number; inView?: boolean }) {
  return (
    <motion.div
      variants={container}
      custom={stagger}
      initial="hidden"
      {...(inView ? { whileInView: "show", viewport: { once: true, margin: "-40px" } } : { animate: "show" })}
      {...props}
    />
  );
}

export function StaggerItem(props: HTMLMotionProps<"div">) {
  return <motion.div variants={staggerItem} {...props} />;
}

/** Counts up from 0 to `value` when visible. */
export function CountUp({
  value, suffix = "", duration = 1.2, className, format,
}: { value: number; suffix?: string; duration?: number; className?: string; format?: (s: string) => string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true });
  const mv = useMotionValue(0);
  const text = useTransform(mv, (v) => {
    const s = `${Math.round(v)}${suffix}`;
    return format ? format(s) : s;
  });

  useEffect(() => {
    if (!inView) return;
    const c = animate(mv, value, { duration, ease: EASE });
    return () => c.stop();
  }, [inView, value, duration, mv]);

  return (
    <motion.span ref={ref} className={className}>
      {text}
    </motion.span>
  );
}
