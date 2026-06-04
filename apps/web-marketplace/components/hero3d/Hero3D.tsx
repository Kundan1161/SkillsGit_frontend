"use client";

import { Suspense, useEffect, useMemo, useRef, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { useTheme } from "next-themes";
import { HeroCopy } from "./HeroCopy";
import { HeroFallback } from "./HeroFallback";
import { BrainScene, type SceneQuality } from "./BrainScene";
import type { BrainPalette } from "./BrainParticles";

function webglSupported() {
  try {
    const c = document.createElement("canvas");
    return !!(window.WebGLRenderingContext && (c.getContext("webgl2") || c.getContext("webgl")));
  } catch {
    return false;
  }
}

export default function Hero3D() {
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme === "dark";

  const [can3D, setCan3D] = useState<boolean | null>(null);
  const [active, setActive] = useState(true);
  const sectionRef = useRef<HTMLElement>(null);

  // Capability gate: skip 3D on small screens, no WebGL, or reduced-motion.
  useEffect(() => {
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const small = window.matchMedia("(max-width: 1023px)").matches;
    setCan3D(!reduced && !small && webglSupported());
  }, []);

  // Pause rendering when the hero scrolls out of view.
  useEffect(() => {
    const el = sectionRef.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => {
        const e = entries[0];
        if (e) setActive(e.isIntersecting);
      },
      { threshold: 0.05 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, [can3D]);

  const palette = useMemo<BrainPalette>(
    () =>
      isDark
        ? { organic: "#8b5cf6", digital: "#22d3ee", hot: "#ffffff" }
        : { organic: "#6d28d9", digital: "#2563eb", hot: "#7c3aed" },
    [isDark]
  );

  const quality = useMemo<SceneQuality>(
    () => ({
      bloom: isDark ? 1.0 : 0.0,
      dof: true,
      stars: isDark ? 700 : 250,
    }),
    [isDark]
  );

  if (can3D === null) return <HeroFallback />;
  if (!can3D) return <HeroFallback />;

  return (
    <section
      ref={sectionRef}
      className="relative flex items-center overflow-hidden"
      style={{ background: "var(--color-bg)", minHeight: "100svh", color: "var(--color-fg)" }}
    >
      <div className="relative z-10 mx-auto grid w-full max-w-[1440px] grid-cols-1 items-center gap-12 px-6 pb-10 pt-[5.5rem] md:pb-24 lg:grid-cols-[45%_55%] lg:px-12 xl:px-16">
        <HeroCopy />

        <div className="relative hidden lg:block" style={{ height: "clamp(520px, 82vh, 820px)" }}>
          <div className="absolute inset-0">
            <Canvas
              frameloop={active ? "always" : "never"}
              dpr={[1, 1.75]}
              camera={{ position: [0, 0, 8.4], fov: 38 }}
              gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
            >
              <Suspense fallback={null}>
                <BrainScene palette={palette} additive={isDark} quality={quality} />
              </Suspense>
            </Canvas>
          </div>
        </div>
      </div>
    </section>
  );
}
