"use client";

import { useEffect, useRef } from "react";

// A soft aura light that smoothly trails the cursor. The native cursor stays
// visible. Disabled on touch / reduced-motion.
export function CustomCursor() {
  const auraRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (!window.matchMedia("(pointer: fine)").matches) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const aura = auraRef.current;
    if (!aura) return;

    let mx = window.innerWidth / 2;
    let my = window.innerHeight / 2;
    let ax = mx, ay = my;
    let visible = 0;
    let raf = 0;

    const onMove = (e: MouseEvent) => { mx = e.clientX; my = e.clientY; visible = 1; };
    const onLeave = () => { visible = 0; };
    window.addEventListener("mousemove", onMove, { passive: true });
    document.addEventListener("mouseleave", onLeave);

    let shownT = 0;
    const tick = () => {
      ax += (mx - ax) * 0.12;
      ay += (my - ay) * 0.12;
      shownT += (visible - shownT) * 0.08;
      aura.style.transform = `translate3d(${ax}px, ${ay}px, 0) translate(-50%, -50%)`;
      aura.style.opacity = String(shownT);
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("mousemove", onMove);
      document.removeEventListener("mouseleave", onLeave);
    };
  }, []);

  return <div ref={auraRef} className="cursor-aura" aria-hidden />;
}
