"use client";

import { motion } from "motion/react";

/** Re-mounts on every navigation inside the app: soft fade + lift between pages. */
export default function AppTemplate({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10, filter: "blur(4px)" }}
      animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className="mx-auto w-full max-w-6xl"
    >
      {children}
    </motion.div>
  );
}
