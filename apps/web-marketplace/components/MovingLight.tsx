"use client";

import { useEffect, useRef } from "react";

// A soft spotlight that slowly drifts across the page. Every element marked
// with `data-lit` reacts to it: a highlight appears on the side facing the
// light and brightens as the light moves closer — as if lit by a real source.
export function MovingLight() {
  const spotRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    if (window.matchMedia("(pointer: coarse)").matches) return; // skip on touch/mobile

    const spot = spotRef.current;
    if (!spot) return;
    let raf = 0;

    const tick = (t: number) => {
      const w = window.innerWidth;
      const h = window.innerHeight;
      // Slow wandering path across the viewport.
      const lx = w * (0.5 + 0.42 * Math.sin(t * 0.00018));
      const ly = h * (0.42 + 0.34 * Math.sin(t * 0.00026 + 1.3));

      spot.style.transform = `translate3d(${lx}px, ${ly}px, 0) translate(-50%, -50%)`;

      const els = document.querySelectorAll<HTMLElement>("[data-lit]");
      els.forEach((el) => {
        const r = el.getBoundingClientRect();
        if (r.bottom < -50 || r.top > h + 50 || r.right < 0 || r.left > w) {
          el.style.setProperty("--lit", "0");
          return;
        }
        el.style.setProperty("--lx", `${lx - r.left}px`);
        el.style.setProperty("--ly", `${ly - r.top}px`);
        const cx = r.left + r.width / 2;
        const cy = r.top + r.height / 2;
        const d = Math.hypot(lx - cx, ly - cy);
        const v = Math.max(0, 1 - d / 560);
        el.style.setProperty("--lit", (v * 0.9).toFixed(3));
      });

      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, []);

  return <div ref={spotRef} className="moving-light" aria-hidden />;
}
