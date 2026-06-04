"use client";

import { HeroCopy } from "./HeroCopy";

// Shown while the 3D scene lazy-loads, and as the permanent experience on
// mobile / no-WebGL / prefers-reduced-motion. Static, theme-aware brain image
// with a soft glow so the page never looks empty.
export function HeroFallback() {
  return (
    <section
      className="relative flex items-center overflow-hidden"
      style={{ background: "var(--color-bg)", minHeight: "100svh", color: "var(--color-fg)" }}
    >
      <div className="relative z-10 mx-auto grid w-full max-w-[1440px] grid-cols-1 items-center gap-12 px-6 pb-10 pt-[5.5rem] md:pb-24 lg:grid-cols-[45%_55%] lg:px-12 xl:px-16">
        <HeroCopy />
        <div className="relative hidden items-center justify-center lg:flex" style={{ height: "clamp(520px, 80vh, 760px)" }}>
          <div
            aria-hidden
            className="absolute inset-0"
            style={{ background: "radial-gradient(circle at 55% 45%, rgba(124,58,237,0.18), transparent 65%)" }}
          />
          {/* light/dark swap via CSS so it's correct before JS theme resolves */}
          <img
            src="/neumorphic_brain_light.png"
            alt="Digital expert brain"
            className="relative max-h-full w-auto object-contain dark:hidden"
            style={{ filter: "drop-shadow(0 0 40px rgba(124,58,237,0.25))" }}
          />
          <img
            src="/neumorphic_brain_dark.png"
            alt="Digital expert brain"
            className="relative hidden max-h-full w-auto object-contain dark:block"
            style={{ filter: "drop-shadow(0 0 50px rgba(99,102,241,0.45))" }}
          />
        </div>
      </div>
    </section>
  );
}

export default HeroFallback;
