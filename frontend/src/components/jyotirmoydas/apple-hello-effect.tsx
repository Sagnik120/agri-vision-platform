"use client";

import type { TargetAndTransition } from "motion/react";
import { motion } from "motion/react";

import { cn } from "@/lib/utils";

const initialProps: TargetAndTransition = {
  pathLength: 0,
  opacity: 0,
};

const animateProps: TargetAndTransition = {
  pathLength: 1,
  opacity: 1,
};

type Props = React.ComponentProps<typeof motion.svg> & {
  speed?: number;
  onAnimationComplete?: () => void;
};

function AppleHelloHindiEffect({
  className,
  speed = 1,
  onAnimationComplete,
  ...props
}: Props) {
  const calc = (x: number) => x * speed;

  return (
    <motion.svg
      className={cn("h-20", className)}
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 605 273"
      fill="none"
      stroke="currentColor"
      strokeWidth="14.8883"
      initial={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      {...props}
    >
      <title>नमस्ते</title>

      {/* न - first loop */}
      <motion.path
        d="M42.3842 150.002C53.2928 153.473 60.4984 162.29 60.4984 175.561C60.4984 189.953 50.3247 201.119 36.677 201.119C24.022 201.119 14.8408 192.186 14.8408 179.035C14.8408 160.269 31.2182 148.265 56.5282 149.01C82.0863 149.754 103.723 163.663 120.367 185.069"
        style={{ strokeLinecap: "round" }}
        initial={initialProps}
        animate={animateProps}
        transition={{
          duration: calc(0.6),
          ease: "easeInOut",
          opacity: { duration: 0.3 },
        }}
      />

      {/* न - vertical stem */}
      <motion.path
        d="M133.502 93.5842C124.459 153.875 117.303 209.683 111.71 264.988"
        style={{ strokeLinecap: "round" }}
        initial={initialProps}
        animate={animateProps}
        transition={{
          duration: calc(0.5),
          ease: "easeInOut",
          delay: calc(0.5),
          opacity: { duration: 0.25, delay: calc(0.5) },
        }}
      />

      {/* म - loop and curve */}
      <motion.path
        d="M216.556 90.9181C217.117 117.977 216.81 137.689 214.869 160.067C212.007 193.058 200.119 213.115 180.936 213.115C169.295 213.115 160.844 205.334 160.844 193.399C160.844 177.222 175.901 164.28 203.653 165.376C229.863 166.411 256.651 174.863 275.138 192.025"
        style={{ strokeLinecap: "round" }}
        initial={initialProps}
        animate={animateProps}
        transition={{
          duration: calc(0.7),
          ease: "easeInOut",
          delay: calc(0.9),
          opacity: { duration: 0.35, delay: calc(0.9) },
        }}
      />

      {/* म - vertical stem */}
      <motion.path
        d="M289.489 90.0085C280.255 150.162 272.672 207.783 267.379 263.003"
        style={{ strokeLinecap: "round" }}
        initial={initialProps}
        animate={animateProps}
        transition={{
          duration: calc(0.5),
          ease: "easeInOut",
          delay: calc(1.5),
          opacity: { duration: 0.25, delay: calc(1.5) },
        }}
      />

      {/* स्त - complex loop */}
      <motion.path
        d="M373.949 90.0198C394.816 102.051 408.098 128.602 408.098 154.079C408.098 185.141 387.465 205.586 358.47 205.586C330.249 205.586 311.145 186.038 317.527 170.35C322.864 157.231 341.378 156.812 356.237 168.861C374.674 183.811 382.044 216.764 385.021 261.169"
        style={{ strokeLinecap: "round" }}
        initial={initialProps}
        animate={animateProps}
        transition={{
          duration: calc(0.8),
          ease: "easeInOut",
          delay: calc(1.9),
          opacity: { duration: 0.4, delay: calc(1.9) },
        }}
      />

      {/* Halant mark (virama) */}
      <motion.path
        d="M403.474 177.549C418.085 183.32 439.163 184.314 458.424 179.805"
        style={{ strokeLinecap: "round" }}
        initial={initialProps}
        animate={animateProps}
        transition={{
          duration: calc(0.3),
          ease: "easeOut",
          delay: calc(2.6),
          opacity: { duration: 0.15, delay: calc(2.6) },
        }}
      />

      {/* त - vertical stem */}
      <motion.path
        d="M556.981 88.1333C546.807 149.619 538.371 207.01 531.919 262.906"
        style={{ strokeLinecap: "round" }}
        initial={initialProps}
        animate={animateProps}
        transition={{
          duration: calc(0.5),
          ease: "easeInOut",
          delay: calc(2.8),
          opacity: { duration: 0.25, delay: calc(2.8) },
        }}
      />

      {/* त - matra loop */}
      <motion.path
        d="M536.891 222.462C541.984 183.336 528.689 152.484 496.435 152.484C472.365 152.484 453.755 175.064 453.755 203.104C453.755 223.451 461.199 245.784 475.095 261.417"
        style={{ strokeLinecap: "round" }}
        initial={initialProps}
        animate={animateProps}
        transition={{
          duration: calc(0.6),
          ease: "easeInOut",
          delay: calc(3.2),
          opacity: { duration: 0.3, delay: calc(3.2) },
        }}
      />

      {/* त े - Chandrabindu / accent mark */}
      <motion.path
        className="stroke-yellow-400"
        d="M521.259 45.4307C485.619 43.0134 474.856 32.3917 474.856 21.5298C474.856 12.832 482.71 7.04349 493.506 7.46568C518.289 8.37031 542.96 35.3336 555.578 70.4412"
        style={{ strokeLinecap: "round" }}
        initial={initialProps}
        animate={animateProps}
        transition={{
          duration: calc(0.5),
          ease: "easeInOut",
          delay: calc(3.7),
          opacity: { duration: 0.25, delay: calc(3.7) },
        }}
      />

      {/* Shirorekha (headline) - the connecting line */}
      <motion.path
        d="M7.44434 88.6792C30.9102 88.8706 59.0093 89.2085 95.3706 89.2085C132.178 89.2085 208.165 89.2571 253.623 89.2047C295.091 89.1568 396.683 89.0223 452.784 89.0234C506.182 89.0244 552.847 88.4444 596.931 87.2836"
        style={{ strokeLinecap: "round" }}
        initial={initialProps}
        animate={animateProps}
        transition={{
          duration: calc(0.8),
          ease: "easeOut",
          delay: calc(4.1),
          opacity: { duration: 0.4, delay: calc(4.1) },
        }}
        onAnimationComplete={onAnimationComplete}
      />
    </motion.svg>
  );
}

function AppleHelloEnglishEffect({
  className,
  speed = 1,
  onAnimationComplete,
  ...props
}: Props) {
  const calc = (x: number) => x * speed;

  return (
    <motion.svg
      className={cn("h-20", className)}
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 638 200"
      fill="none"
      stroke="currentColor"
      strokeWidth="14.8883"
      initial={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      {...props}
    >
      <title>hello</title>

      {/* h1 */}
      <motion.path
        d="M8.69214 166.553C36.2393 151.239 61.3409 131.548 89.8191 98.0295C109.203 75.1488 119.625 49.0228 120.122 31.0026C120.37 17.6036 113.836 7.43883 101.759 7.43883C88.3598 7.43883 79.9231 17.6036 74.7122 40.9363C69.005 66.5793 64.7866 96.0036 54.1166 190.356"
        style={{ strokeLinecap: "round" }}
        initial={initialProps}
        animate={animateProps}
        transition={{
          duration: calc(0.8),
          ease: "easeInOut",
          opacity: { duration: 0.4 },
        }}
      />

      {/* h2, ello */}
      <motion.path
        d="M55.1624 181.135C60.6251 133.114 81.4118 98.0479 107.963 98.0479C123.844 98.0479 133.937 110.703 131.071 128.817C129.457 139.487 127.587 150.405 125.408 163.06C122.869 178.941 130.128 191.348 152.122 191.348C184.197 191.348 219.189 173.523 237.097 145.915C243.198 136.509 245.68 128.073 245.928 119.884C246.176 104.996 237.739 93.8296 222.851 93.8296C203.992 93.8296 189.6 115.17 189.6 142.465C189.6 171.745 205.481 192.341 239.208 192.341C285.066 192.341 335.86 137.292 359.199 75.8585C365.788 58.513 368.26 42.4065 368.26 31.1512C368.26 17.8057 364.042 7.55823 352.131 7.55823C340.469 7.55823 332.777 16.6141 325.829 30.9129C317.688 47.4967 311.667 71.4162 309.203 98.4549C303 166.301 316.896 191.348 349.936 191.348C390 191.348 434.542 135.534 457.286 75.6686C463.803 58.513 466.275 42.4065 466.275 31.1512C466.275 17.8057 462.057 7.55823 450.146 7.55823C438.484 7.55823 430.792 16.6141 423.844 30.9129C415.703 47.4967 409.682 71.4162 407.218 98.4549C401.015 166.301 414.911 191.348 444.416 191.348C473.874 191.348 489.877 165.67 499.471 138.402C508.955 111.447 520.618 94.8221 544.935 94.8221C565.035 94.8221 580.916 109.71 580.916 137.75C580.916 168.768 560.792 192.093 535.362 192.341C512.984 192.589 498.285 174.475 499.774 147.179C501.511 116.907 519.873 94.8221 543.943 94.8221C557.839 94.8221 569.51 100.999 578.682 107.725C603.549 125.866 622.709 114.656 630.047 96.7186"
        style={{ strokeLinecap: "round" }}
        initial={initialProps}
        animate={animateProps}
        transition={{
          duration: calc(2.8),
          ease: "easeInOut",
          delay: calc(0.7),
          opacity: { duration: 0.7, delay: calc(0.7) },
        }}
        onAnimationComplete={onAnimationComplete}
      />
    </motion.svg>
  );
}
export { AppleHelloEnglishEffect, AppleHelloHindiEffect };
