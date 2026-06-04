"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Zap, Shield, MessageCircle, TrendingUp } from "lucide-react";

const fade = {
  hidden: { opacity: 0, y: 18 },
  show: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: 0.1 + i * 0.1, duration: 0.6, ease: [0.22, 1, 0.36, 1] as const },
  }),
};

export function HeroCopy() {
  return (
    <div className="flex flex-col gap-6 lg:gap-8">
      <motion.div
        custom={0}
        variants={fade}
        initial="hidden"
        animate="show"
        className="inline-flex w-fit items-center gap-2.5 rounded-full px-4 py-2"
        style={{ background: "var(--color-bg)", boxShadow: "var(--shadow-neu-sm)" }}
      >
        <span className="text-xs font-bold uppercase tracking-widest" style={{ color: "#7c3aed" }}>
          2,400+ Experts Earning Passively
        </span>
      </motion.div>

      <motion.h1
        custom={1}
        variants={fade}
        initial="hidden"
        animate="show"
        className="text-fg"
        style={{ fontSize: "clamp(2.8rem, 5vw, 5rem)", fontWeight: 900, letterSpacing: "-0.04em", lineHeight: 0.96 }}
      >
        Turn Human Knowledge
        <br />
        Into{" "}
        <span
          style={{
            background: "linear-gradient(120deg,#a855f7 0%,#7c3aed 45%,#6366f1 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
          }}
        >
          Living Intelligence
        </span>
      </motion.h1>

      <motion.p
        custom={2}
        variants={fade}
        initial="hidden"
        animate="show"
        className="max-w-[44ch] text-base font-medium leading-relaxed text-fg-muted md:text-lg"
      >
        Upload once. We transform your expertise into an AI that absorbs your knowledge, becomes your
        digital twin, and earns for you 24/7.
      </motion.p>

      <motion.div
        custom={3}
        variants={fade}
        initial="hidden"
        animate="show"
        className="flex flex-col gap-4 sm:flex-row sm:flex-wrap"
      >
        <Link
          href="/creator/dashboard"
          className="inline-flex items-center justify-center gap-3 px-8 py-4 text-base font-bold text-white transition-transform duration-300 hover:-translate-y-0.5"
          style={{ borderRadius: "1rem", background: "linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%)", boxShadow: "var(--shadow-brand)" }}
        >
          Create Your Expert AI <ArrowRight className="h-5 w-5" />
        </Link>
        <Link
          href="/explore"
          className="inline-flex items-center justify-center gap-2 px-8 py-4 text-base font-semibold text-fg transition-transform duration-300 hover:-translate-y-0.5"
          style={{ borderRadius: "1rem", background: "var(--color-bg-raised)", border: "1px solid var(--color-border)", boxShadow: "var(--shadow-neu-sm)" }}
        >
          Explore Experts
        </Link>
      </motion.div>

      <motion.div
        custom={4}
        variants={fade}
        initial="hidden"
        animate="show"
        className="mt-2 grid max-w-sm grid-cols-2 gap-3"
      >
        {[
          { Icon: Zap, label: "Live in 10 minutes", desc: "Quick setup" },
          { Icon: Shield, label: "Verified citations", desc: "Sources you trust" },
          { Icon: MessageCircle, label: "Unlimited questions", desc: "From subscribers" },
          { Icon: TrendingUp, label: "Passive income", desc: "Earn every month" },
        ].map(({ Icon, label, desc }) => (
          <div
            key={label}
            className="flex items-start gap-2.5 px-3 py-2.5"
            style={{ background: "var(--color-bg)", boxShadow: "var(--shadow-neu-xs)", borderRadius: "0.875rem" }}
          >
            <div
              className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center"
              style={{ background: "var(--color-bg)", boxShadow: "var(--shadow-neu-sm)", borderRadius: "0.65rem" }}
            >
              <Icon className="h-4 w-4" style={{ color: "#7c3aed" }} />
            </div>
            <div>
              <p className="text-xs font-black text-fg" style={{ letterSpacing: "-0.01em" }}>{label}</p>
              <p style={{ fontSize: "0.6rem", color: "var(--color-fg-subtle)" }}>{desc}</p>
            </div>
          </div>
        ))}
      </motion.div>
    </div>
  );
}
