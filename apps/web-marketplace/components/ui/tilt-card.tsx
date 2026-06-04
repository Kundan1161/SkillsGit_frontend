"use client";

import { useRef, type ReactNode } from "react";

interface TiltCardProps {
  children: ReactNode;
  className?: string;
  style?: React.CSSProperties;
  intensity?: number; // degrees of tilt, default 12
  scale?: number;     // hover scale, default 1.03
}

export function TiltCard({
  children,
  className = "",
  style,
  intensity = 12,
  scale = 1.03,
}: TiltCardProps) {
  const ref = useRef<HTMLDivElement>(null);
  const rafRef = useRef<number | null>(null);

  const onMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return;
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    rafRef.current = requestAnimationFrame(() => {
      if (!ref.current) return;
      const { left, top, width, height } = ref.current.getBoundingClientRect();
      const x = (e.clientX - left) / width  - 0.5; // -0.5 → 0.5
      const y = (e.clientY - top)  / height - 0.5;
      ref.current.style.transition = "transform 0.1s ease, box-shadow 0.1s ease";
      ref.current.style.transform  =
        `perspective(900px) rotateY(${x * intensity}deg) rotateX(${-y * intensity}deg) scale(${scale}) translateZ(8px)`;
    });
  };

  const onLeave = () => {
    if (!ref.current) return;
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    ref.current.style.transition = "transform 0.6s cubic-bezier(0.16,1,0.3,1), box-shadow 0.4s ease";
    ref.current.style.transform  = "perspective(900px) rotateY(0deg) rotateX(0deg) scale(1) translateZ(0)";
  };

  return (
    <div
      ref={ref}
      className={className}
      style={{ ...style, transformStyle: "preserve-3d", willChange: "transform" }}
      onMouseMove={onMove}
      onMouseLeave={onLeave}
    >
      {children}
    </div>
  );
}
