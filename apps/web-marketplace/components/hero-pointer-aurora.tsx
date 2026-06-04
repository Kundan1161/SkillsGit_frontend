"use client";

import { useEffect, useRef } from "react";

export function HeroPointerAurora() {
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let frame = 0;

    const update = (event: PointerEvent) => {
      if (frame) cancelAnimationFrame(frame);

      frame = requestAnimationFrame(() => {
        const root = rootRef.current;
        if (!root) return;

        const x = event.clientX / window.innerWidth;
        const y = event.clientY / window.innerHeight;
        const rotateY = (x - 0.5) * 18;
        const rotateX = (0.5 - y) * 14;

        root.style.setProperty("--pointer-x", `${(x * 100).toFixed(2)}%`);
        root.style.setProperty("--pointer-y", `${(y * 100).toFixed(2)}%`);
        root.style.setProperty("--tilt-x", `${rotateX.toFixed(2)}deg`);
        root.style.setProperty("--tilt-y", `${rotateY.toFixed(2)}deg`);
        root.style.setProperty("--drift-x", `${((x - 0.5) * 34).toFixed(2)}px`);
        root.style.setProperty("--drift-y", `${((y - 0.5) * 28).toFixed(2)}px`);
      });
    };

    window.addEventListener("pointermove", update, { passive: true });

    return () => {
      window.removeEventListener("pointermove", update);
      if (frame) cancelAnimationFrame(frame);
    };
  }, []);

  return (
    <div ref={rootRef} className="hero-pointer-aurora" aria-hidden>
      <div className="hero-pointer-glow" />
      <div className="hero-orb hero-orb-a" />
      <div className="hero-orb hero-orb-b" />
      <div className="hero-orb hero-orb-c" />
      <div className="hero-depth-plane">
        <span />
        <span />
        <span />
      </div>
      <div className="hero-light-ribbon hero-light-ribbon-a" />
      <div className="hero-light-ribbon hero-light-ribbon-b" />
      <div className="hero-particles">
        {Array.from({ length: 18 }, (_, index) => (
          <i key={index} />
        ))}
      </div>

      <style>{`
        .hero-pointer-aurora {
          --pointer-x: 70%;
          --pointer-y: 42%;
          --tilt-x: 0deg;
          --tilt-y: 0deg;
          --drift-x: 0px;
          --drift-y: 0px;
          position: fixed;
          inset: 0;
          z-index: 0;
          overflow: hidden;
          pointer-events: none;
          perspective: 1100px;
          transform-style: preserve-3d;
        }

        .hero-pointer-glow {
          position: absolute;
          inset: -18%;
          background:
            radial-gradient(circle at var(--pointer-x) var(--pointer-y), rgba(124, 58, 237, 0.16), rgba(124, 58, 237, 0.055) 15rem, transparent 32rem),
            radial-gradient(circle at calc(var(--pointer-x) + 12%) calc(var(--pointer-y) + 8%), rgba(59, 130, 246, 0.105), transparent 26rem),
            radial-gradient(circle at 82% 78%, rgba(168, 85, 247, 0.085), transparent 30rem);
          filter: blur(8px);
          opacity: 0.68;
          transform: translate3d(calc(var(--drift-x) * -0.35), calc(var(--drift-y) * -0.35), -80px);
          transition: background 160ms linear;
        }

        .hero-orb {
          position: absolute;
          border-radius: 999px;
          background:
            radial-gradient(circle at 34% 28%, rgba(255,255,255,0.7), rgba(255,255,255,0.14) 22%, rgba(124,58,237,0.07) 48%, transparent 72%);
          border: 1px solid rgba(124, 58, 237, 0.08);
          box-shadow: inset 18px 20px 60px rgba(255,255,255,0.3), 0 40px 120px rgba(124,58,237,0.09);
          transform-style: preserve-3d;
          will-change: transform;
        }

        .hero-orb-a {
          right: 7%;
          top: 16%;
          width: 210px;
          height: 210px;
          animation: hero-orb-float 9s ease-in-out infinite;
          transform: translate3d(var(--drift-x), var(--drift-y), 80px);
        }

        .hero-orb-b {
          right: 31%;
          bottom: 14%;
          width: 130px;
          height: 130px;
          opacity: 0.5;
          animation: hero-orb-float 11s ease-in-out 1.4s infinite reverse;
          transform: translate3d(calc(var(--drift-x) * -0.8), calc(var(--drift-y) * 0.7), 40px);
        }

        .hero-orb-c {
          left: 39%;
          top: 22%;
          width: 88px;
          height: 88px;
          opacity: 0.32;
          animation: hero-orb-float 8s ease-in-out 0.7s infinite;
          transform: translate3d(calc(var(--drift-x) * 0.5), calc(var(--drift-y) * -0.9), 20px);
        }

        .hero-depth-plane {
          position: absolute;
          right: -5%;
          bottom: -17%;
          width: 70%;
          height: 52%;
          transform: rotateX(68deg) rotateZ(-7deg) rotateY(var(--tilt-y)) translate3d(var(--drift-x), var(--drift-y), -120px);
          transform-style: preserve-3d;
          border-radius: 50%;
          background:
            linear-gradient(90deg, rgba(124,58,237,0.16) 1px, transparent 1px),
            linear-gradient(rgba(124,58,237,0.12) 1px, transparent 1px),
            radial-gradient(ellipse at 50% 50%, rgba(124,58,237,0.1), transparent 68%);
          background-size: 48px 48px, 48px 48px, auto;
          mask-image: radial-gradient(ellipse at center, black 18%, transparent 72%);
          opacity: 0.42;
        }

        .hero-depth-plane span {
          position: absolute;
          inset: 8%;
          border: 1px solid rgba(124, 58, 237, 0.18);
          border-radius: 50%;
        }

        .hero-depth-plane span:nth-child(2) { inset: 22%; border-style: dashed; }
        .hero-depth-plane span:nth-child(3) { inset: 36%; opacity: 0.8; }

        .hero-light-ribbon {
          position: absolute;
          right: 9%;
          top: 27%;
          width: 52%;
          height: 18%;
          border-radius: 999px;
          background: linear-gradient(90deg, transparent, rgba(124,58,237,0.105), rgba(59,130,246,0.09), transparent);
          filter: blur(24px);
          transform-origin: center;
          transform: rotate(-13deg) translate3d(calc(var(--drift-x) * 0.6), calc(var(--drift-y) * 0.4), 50px);
          animation: hero-ribbon-pulse 7s ease-in-out infinite;
        }

        .hero-light-ribbon-b {
          right: 2%;
          top: 54%;
          width: 46%;
          height: 14%;
          opacity: 0.48;
          transform: rotate(13deg) translate3d(calc(var(--drift-x) * -0.4), calc(var(--drift-y) * 0.5), 30px);
          animation-delay: 1.6s;
        }

        .hero-particles i {
          position: absolute;
          width: 5px;
          height: 5px;
          border-radius: 999px;
          background: rgba(124, 58, 237, 0.32);
          box-shadow: 0 0 12px rgba(124, 58, 237, 0.32);
          animation: hero-particle-drift 6s ease-in-out infinite;
        }

        .hero-particles i:nth-child(1) { left: 53%; top: 19%; animation-delay: .1s; }
        .hero-particles i:nth-child(2) { left: 62%; top: 13%; animation-delay: .8s; }
        .hero-particles i:nth-child(3) { left: 77%; top: 20%; animation-delay: 1.3s; }
        .hero-particles i:nth-child(4) { left: 89%; top: 31%; animation-delay: .4s; }
        .hero-particles i:nth-child(5) { left: 68%; top: 34%; animation-delay: 1.8s; }
        .hero-particles i:nth-child(6) { left: 55%; top: 47%; animation-delay: 2.1s; }
        .hero-particles i:nth-child(7) { left: 82%; top: 49%; animation-delay: .9s; }
        .hero-particles i:nth-child(8) { left: 93%; top: 58%; animation-delay: 1.5s; }
        .hero-particles i:nth-child(9) { left: 73%; top: 67%; animation-delay: .2s; }
        .hero-particles i:nth-child(10) { left: 60%; top: 78%; animation-delay: 1.1s; }
        .hero-particles i:nth-child(11) { left: 86%; top: 79%; animation-delay: 2.5s; }
        .hero-particles i:nth-child(12) { left: 47%; top: 62%; animation-delay: 1.7s; }
        .hero-particles i:nth-child(13) { left: 96%; top: 42%; animation-delay: 2.9s; }
        .hero-particles i:nth-child(14) { left: 51%; top: 30%; animation-delay: 3.2s; }
        .hero-particles i:nth-child(15) { left: 70%; top: 8%; animation-delay: 2.2s; }
        .hero-particles i:nth-child(16) { left: 91%; top: 15%; animation-delay: 3.5s; }
        .hero-particles i:nth-child(17) { left: 42%; top: 39%; animation-delay: 2.7s; }
        .hero-particles i:nth-child(18) { left: 78%; top: 88%; animation-delay: 3.9s; }

        @keyframes hero-orb-float {
          0%, 100% { margin-top: 0; margin-left: 0; }
          50% { margin-top: -18px; margin-left: 10px; }
        }

        @keyframes hero-ribbon-pulse {
          0%, 100% { opacity: 0.28; filter: blur(24px); }
          50% { opacity: 0.55; filter: blur(30px); }
        }

        @keyframes hero-particle-drift {
          0%, 100% { opacity: 0.14; transform: translate3d(0, 0, 20px) scale(0.75); }
          50% { opacity: 0.5; transform: translate3d(var(--drift-x), var(--drift-y), 80px) scale(1.2); }
        }

        @media (max-width: 1023px) {
          .hero-pointer-aurora {
            opacity: 0.62;
          }

          .hero-depth-plane,
          .hero-light-ribbon {
            display: none;
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .hero-pointer-aurora *,
          .hero-pointer-aurora *::before,
          .hero-pointer-aurora *::after {
            animation: none !important;
            transition: none !important;
          }
        }
      `}</style>
    </div>
  );
}
