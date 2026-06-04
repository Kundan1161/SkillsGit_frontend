"use client";

import React, { useEffect, useRef } from "react";
import Link from "next/link";
import { ArrowRight, Zap, Shield, MessageCircle, TrendingUp, Video, Music, FileText, Image as ImageIcon, File, FileCode } from "lucide-react";

// Orbiting cards list with screen coordinates and properties matching reference mockup
const NODES = [
  { 
    id: "knowledge-capture",
    side: "left",
    emoji: "📂",
    title: "Knowledge Capture",
    sub: "Any format",
    top: 0.12,
    left: 0.02,
    floatDelay: "0s",
  },
  { 
    id: "ai-processing",
    side: "left",
    emoji: "⚙️",
    title: "AI Processing",
    sub: "Transcribe, extract, structure",
    top: 0.44,
    left: 0,
    floatDelay: "-1.7s",
  },
  { 
    id: "smart-vault",
    side: "left",
    emoji: "🗄️",
    title: "Smart Vault",
    sub: "Organised markdown vault",
    top: 0.76,
    left: 0.04,
    floatDelay: "-3.1s",
  },
  { 
    id: "expert-persona",
    side: "right",
    emoji: "👤",
    title: "Expert Persona",
    sub: "Digital twin of you",
    top: 0.13,
    right: 0.02,
    floatDelay: "-0.8s",
  },
  { 
    id: "subscribers",
    side: "right",
    emoji: "👥",
    title: "Subscribers",
    sub: "Ask questions 24/7",
    top: 0.46,
    right: 0,
    floatDelay: "-2.4s",
  },
  { 
    id: "recurring-income",
    side: "right",
    emoji: "💰",
    title: "Recurring Income",
    sub: "Earn every month",
    top: 0.75,
    right: 0.04,
    floatDelay: "-4s",
  },
];

// Bright pink neon palette — no dingy purples, so every particle reads as a
// glowing neon dot on both light and dark backgrounds.
const BRAIN_PARTICLE_COLORS = ["#ffffff", "#fff1fb", "#ffd6f3", "#fbb6e6", "#f472b6", "#ec4899", "#f0abfc"] as const;

function pickBrainParticleColor() {
  return BRAIN_PARTICLE_COLORS[Math.floor(Math.random() * BRAIN_PARTICLE_COLORS.length)] ?? "#ff7ad9";
}

// Splits text into per-word spans; hovering a word flows a gradient across it.
function HoverText({ text, gradient }: { text: string; gradient?: boolean }) {
  return (
    <>
      {text.split(" ").map((word, wi, arr) => (
        <span key={wi}>
          <span className={gradient ? "hero-letter hero-grad-static" : "hero-letter"}>
            {word}
          </span>
          {wi < arr.length - 1 ? " " : ""}
        </span>
      ))}
    </>
  );
}

export function BreathingBrainHero() {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const mouseRef = useRef({ x: 0, y: 0, targetX: 0, targetY: 0 });

  const lightImageRef = useRef<HTMLImageElement | null>(null);
  const darkImageRef = useRef<HTMLImageElement | null>(null);
  const digitalImageRef = useRef<HTMLImageElement | null>(null);
  const digitalLightImageRef = useRef<HTMLImageElement | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const imgL = new Image();
    imgL.src = "/reg-brain.png";
    imgL.onload = () => {
      lightImageRef.current = imgL;
    };

    const imgD = new Image();
    imgD.src = "/reg-brain.png";
    imgD.onload = () => {
      darkImageRef.current = imgD;
    };

    // Digital neural-network version of the brain — faded in as the brain grows.
    const dig = new Image();
    dig.src = "/digital_brain_overlay.png";
    dig.onload = () => {
      digitalImageRef.current = dig;
    };
    const digL = new Image();
    digL.src = "/digital_brain_overlay.png";
    digL.onload = () => {
      digitalLightImageRef.current = digL;
    };

  }, []);

  useEffect(() => {
    if (!canvasRef.current || !containerRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    let width = canvas.width;
    let height = canvas.height;

    const resize = () => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      width = rect.width;
      height = rect.height;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    resize();
    window.addEventListener("resize", resize);

    const getImageRect = (
      img: HTMLImageElement,
      originX: number,
      originY: number,
      maxWidth: number,
      maxHeight: number,
      offsetX = 0,
      offsetY = 0
    ) => {
      const ratio = img.naturalWidth / img.naturalHeight || 1;
      let drawWidth = maxWidth;
      let drawHeight = drawWidth / ratio;

      if (drawHeight > maxHeight) {
        drawHeight = maxHeight;
        drawWidth = drawHeight * ratio;
      }

      return {
        x: originX - drawWidth / 2 + offsetX,
        y: originY - drawHeight / 2 + offsetY,
        width: drawWidth,
        height: drawHeight,
      };
    };

    const drawBrainParticle = (
      x: number,
      y: number,
      size: number,
      color: string,
      glow: number,
      alpha: number,
      isDarkMode: boolean,
      digitalAmount = 0
    ) => {
      const visibleAlpha = Math.min(0.82, Math.max(0, alpha));
      if (visibleAlpha <= 0.01) return;

      const glowSize = size * (isDarkMode ? 7.2 : 5.9) * glow * (1 + digitalAmount * 0.34);
      const coreSize = size * (isDarkMode ? 1.18 : 1.05) * (1 + digitalAmount * 0.18);
      const halo = ctx.createRadialGradient(x, y, 0, x, y, glowSize);
      halo.addColorStop(0, `rgba(255,255,255,${visibleAlpha * 0.42})`);
      halo.addColorStop(0.25, `rgba(255,214,243,${visibleAlpha * 0.34})`);
      halo.addColorStop(0.62, `rgba(232,121,249,${visibleAlpha * 0.16})`);
      halo.addColorStop(1, "rgba(217,70,239,0)");

      ctx.fillStyle = halo;
      ctx.globalAlpha = 1;
      ctx.beginPath();
      ctx.arc(x, y, glowSize, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = digitalAmount > 0.35 ? "#fff1fb" : color;
      ctx.globalAlpha = visibleAlpha;
      ctx.beginPath();
      // Single particle style across the whole hero — always a soft round dot.
      ctx.arc(x, y, coreSize, 0, Math.PI * 2);
      ctx.fill();
    };

    // Same round-glow look as drawBrainParticle, just smaller — so the streaming
    // particles match the brain particles instead of being square "neon" bits.
    const drawTinyNeonParticle = (
      x: number,
      y: number,
      size: number,
      alpha: number,
      color: string
    ) => {
      const visibleAlpha = Math.min(0.95, Math.max(0, alpha));
      if (visibleAlpha <= 0.01) return;

      const glowSize = size * 5.8;
      const halo = ctx.createRadialGradient(x, y, 0, x, y, glowSize);
      halo.addColorStop(0, `rgba(255,255,255,${visibleAlpha * 0.4})`);
      halo.addColorStop(0.3, `rgba(232,121,249,${visibleAlpha * 0.2})`);
      halo.addColorStop(1, "rgba(217,70,239,0)");
      ctx.fillStyle = halo;
      ctx.globalAlpha = 1;
      ctx.beginPath();
      ctx.arc(x, y, glowSize, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = color;
      ctx.globalAlpha = visibleAlpha;
      const coreSize = Math.max(1.0, size * 1.4);
      ctx.beginPath();
      ctx.arc(x, y, coreSize, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalAlpha = 1;
    };

    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const clamp = (v: number) => Math.max(-0.6, Math.min(0.6, v));
      const x = clamp((e.clientX - rect.left) / rect.width - 0.5);
      const y = clamp((e.clientY - rect.top) / rect.height - 0.5);
      mouseRef.current.targetX = x;
      mouseRef.current.targetY = y;
    };
    window.addEventListener("mousemove", handleMouseMove);

    const numParticles = 240;
    const particles: Array<{
      x: number;
      y: number;
      z: number;
      ox: number;
      oy: number;
      oz: number;
      size: number;
      color: string;
      glow: number;
      speed: number;
      phase: number;
    }> = [];

    for (let i = 0; i < numParticles; i++) {
      let px = 0, py = 0, pz = 0;
      const rand = Math.random();

      if (rand < 0.42) {
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.random() * Math.PI;
        const rx = 0.4 + Math.random() * 0.12;
        const ry = 0.5 + Math.random() * 0.15;
        const rz = 0.7 + Math.random() * 0.15;
        const fold = 1 + 0.12 * Math.sin(6 * theta) * Math.cos(6 * phi);
        px = -0.22 + rx * Math.cos(theta) * Math.sin(phi) * fold;
        py = 0.08 + ry * Math.sin(theta) * Math.sin(phi) * fold;
        pz = rz * Math.cos(phi) * fold;
      } else if (rand < 0.84) {
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.random() * Math.PI;
        const rx = 0.4 + Math.random() * 0.12;
        const ry = 0.5 + Math.random() * 0.15;
        const rz = 0.7 + Math.random() * 0.15;
        const fold = 1 + 0.12 * Math.sin(6 * theta) * Math.cos(6 * phi);
        px = 0.22 + rx * Math.cos(theta) * Math.sin(phi) * fold;
        py = 0.08 + ry * Math.sin(theta) * Math.sin(phi) * fold;
        pz = rz * Math.cos(phi) * fold;
      } else if (rand < 0.95) {
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.random() * Math.PI;
        const rx = 0.32;
        const ry = 0.24;
        const rz = 0.28;
        px = rx * Math.cos(theta) * Math.sin(phi);
        py = -0.42 + ry * Math.sin(theta);
        pz = -0.45 + rz * Math.cos(phi);
      } else {
        py = -0.35 - Math.random() * 0.45;
        const radius = 0.15 * (1 + (py + 0.35));
        const angle = Math.random() * Math.PI * 2;
        px = Math.cos(angle) * radius;
        pz = -0.15 + Math.sin(angle) * radius;
      }

      particles.push({
        x: px,
        y: py,
        z: pz,
        ox: px,
        oy: py,
        oz: pz,
        size: 0.82 + Math.random() * 1.45,
        color: pickBrainParticleColor(),
        glow: 0.34 + Math.random() * 0.48,
        speed: 0.02 + Math.random() * 0.03,
        phase: Math.random() * Math.PI * 2,
      });
    }

    const connections: number[][] = [];
    for (let i = 0; i < numParticles; i++) {
      const dists: Array<{ index: number; dist: number }> = [];
      const pi = particles[i];
      if (!pi) continue;
      for (let j = 0; j < numParticles; j++) {
        if (i === j) continue;
        const pj = particles[j];
        if (!pj) continue;
        const dx = pi.ox - pj.ox;
        const dy = pi.oy - pj.oy;
        const dz = pi.oz - pj.oz;
        dists.push({ index: j, dist: dx * dx + dy * dy + dz * dz });
      }
      dists.sort((a, b) => a.dist - b.dist);
      connections.push(dists.slice(0, 2).map(d => d.index));
    }

    const streams: Array<{
      nodeIndex: number;
      progress: number;
      speed: number;
      offsetY: number;
      size: number;
      color: string;
      glow: number;
      phase: number;
    }> = [];

    // A single, cohesive stream of particles flows continuously from each card
    // into the brain — the one inflow particle system in the hero.
    const STREAMS_PER_NODE = 6;
    for (let n = 0; n < NODES.length; n++) {
      for (let s = 0; s < STREAMS_PER_NODE; s++) {
        streams.push({
          nodeIndex: n,
          progress: (s / STREAMS_PER_NODE + Math.random() * 0.12) % 1,
          speed: 0.28 + Math.random() * 0.16,
          offsetY: (Math.random() - 0.5) * 0.3,
          size: 0.9 + Math.random() * 1.25,
          color: pickBrainParticleColor(),
          glow: 0.34 + Math.random() * 0.48,
          phase: Math.random() * Math.PI * 2,
        });
      }
    }

    let cycleTime = 0;
    let lastFrameTime = performance.now();
    const cycleDuration = 8.8;
    const easeInOut = (value: number) => {
      const t = Math.min(Math.max(value, 0), 1);
      return t * t * t * (t * (t * 6 - 15) + 10);
    };

    const tick = () => {
      const now = performance.now();
      const deltaSeconds = Math.min((now - lastFrameTime) / 1000, 0.028);
      lastFrameTime = now;

      const mouse = mouseRef.current;
      // Snappy, sensitive tracking toward the pointer.
      mouse.x += (mouse.targetX - mouse.x) * 0.14;
      mouse.y += (mouse.targetY - mouse.y) * 0.14;
      ctx.clearRect(0, 0, width, height);

      cycleTime += deltaSeconds;
      const t = cycleTime % cycleDuration;
      
      let phase: "inhale" | "transform" | "exhale" = "inhale";
      let phaseProgress = 0;

      if (t < 3.25) {
        phase = "inhale";
        phaseProgress = easeInOut(t / 3.25);
      } else if (t < 5.3) {
        phase = "transform";
        phaseProgress = easeInOut((t - 3.25) / 2.05);
      } else {
        phase = "exhale";
        phaseProgress = easeInOut((t - 5.3) / 3.5);
      }

      let currentBrainScale = 1.0;
      let particleOpacity = 0.0;
      let lineOpacity = 0.0;
      let baseImgOpacity = 1.0;
      let digitalAmount = 0.0;

      if (phase === "inhale") {
        currentBrainScale = 1.0 + phaseProgress * 0.085;
        particleOpacity = phaseProgress * 0.46;
        lineOpacity = phaseProgress * 0.16;
        baseImgOpacity = 1.0 - phaseProgress * 0.07;
        digitalAmount = phaseProgress * 0.38;
      } else if (phase === "transform") {
        currentBrainScale = 1.085 - Math.sin(phaseProgress * Math.PI) * 0.006;
        particleOpacity = 0.48 + phaseProgress * 0.42;
        lineOpacity = 0.22 + phaseProgress * 0.66;
        baseImgOpacity = 0.9;
        digitalAmount = 0.38 + Math.sin(phaseProgress * Math.PI) * 0.62;
      } else {
        currentBrainScale = 1.085 - phaseProgress * 0.085;
        particleOpacity = 0.84 * (1.0 - phaseProgress);
        lineOpacity = 0.78 * (1.0 - phaseProgress);
        baseImgOpacity = 0.9 + phaseProgress * 0.1;
        digitalAmount = 0.34 * (1.0 - phaseProgress);
      }

      const isDark = typeof document !== "undefined" && document.documentElement.classList.contains("dark");
      const angleY = cycleTime * 0.075 + mouse.x * 0.42;
      const angleX = Math.sin(cycleTime * 0.05) * 0.075 - mouse.y * 0.42;

      const cosY = Math.cos(angleY);
      const sinY = Math.sin(angleY);
      const cosX = Math.cos(angleX);
      const sinX = Math.sin(angleX);

      const focalLength = 340;
      const zoom = Math.min(width, height) * 0.36;
      const centerX = width * 0.5;
      const centerY = height * 0.46;
      const breathFloat = -zoom * 0.065 * Math.sin((cycleTime / cycleDuration) * Math.PI * 2 - Math.PI * 0.35);
      const brainCenterY = centerY + breathFloat;

      // 1. Draw subtle grid texture inside canvas
      ctx.strokeStyle = isDark 
        ? "rgba(124, 58, 237, 0.02)" 
        : "rgba(124, 58, 237, 0.06)";
      ctx.lineWidth = 1;
      const gridSize = 45;
      for (let x = 0; x < width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // 3. Draw Neumorphic Brain Image
      const activeImg = isDark ? darkImageRef.current : lightImageRef.current;
      // Kept small — the CSS perspective tilt now carries most of the motion.
      const brainOffsetX = mouse.x * 5 * currentBrainScale;
      const brainOffsetY = -mouse.y * 5 * currentBrainScale;
      const brainRect = activeImg
        ? getImageRect(
            activeImg,
            centerX,
            brainCenterY,
            zoom * 2.85 * currentBrainScale,
            zoom * 2.08 * currentBrainScale,
            brainOffsetX,
            brainOffsetY
          )
        : null;

      // 2b. Hovering dotted pattern BEHIND the brain. Drawn before the brain and
      // skipped wherever a dot would fall inside the brain's silhouette, so the
      // dots only show around/behind it (never over it).
      {
        const hover = Math.sin(cycleTime * 0.6) * (zoom * 0.03);
        const spacing = Math.max(20, zoom * 0.085);
        const radius = zoom * 1.95;
        const baseAlpha = isDark ? 0.5 : 0.32;
        const bcx = brainRect ? brainRect.x + brainRect.width * 0.52 : centerX;
        const bcy = brainRect ? brainRect.y + brainRect.height * 0.5 : brainCenterY;
        const brx = brainRect ? brainRect.width * 0.5 : 0;
        const bry = brainRect ? brainRect.height * 0.45 : 0;
        ctx.fillStyle = isDark ? "rgba(196, 181, 253, 1)" : "rgba(124, 58, 237, 1)";
        for (let gx = centerX - radius; gx <= centerX + radius; gx += spacing) {
          for (let gy = brainCenterY - radius; gy <= brainCenterY + radius; gy += spacing) {
            const dx = gx - centerX;
            const dy = gy - brainCenterY;
            const d = Math.sqrt(dx * dx + dy * dy);
            if (d > radius) continue;
            // Skip dots that land inside the brain silhouette.
            if (brainRect) {
              const nx = (gx - bcx) / brx;
              const ny = (gy + hover - bcy) / bry;
              if (nx * nx + ny * ny <= 1.0) continue;
            }
            const fade = 1 - d / radius;
            const a = fade * fade * baseAlpha;
            if (a < 0.015) continue;
            ctx.globalAlpha = a;
            ctx.beginPath();
            ctx.arc(gx, gy + hover, zoom * 0.006 + 0.6, 0, Math.PI * 2);
            ctx.fill();
          }
        }
        ctx.globalAlpha = 1;
      }

      // Soft contact shadow beneath the floating brain. It sits lower and gets
      // smaller/fainter as the brain rises on the inhale (breathFloat is more
      // negative), so the hover reads as real distance from the ground.
      if (brainRect) {
        const lift = -breathFloat / Math.max(1, zoom); // ~0 (low) .. higher when risen
        const shCy = brainRect.y + brainRect.height * 0.9 + zoom * 0.06;
        const shW = brainRect.width * (0.4 - lift * 0.05);
        const shH = shW * 0.2;
        // Constant strong base so the shadow is always visible; only a subtle
        // breath-driven variation on top.
        const shAlpha = (isDark ? 0.5 : 0.32) * (0.92 - lift * 0.15);
        const sh = ctx.createRadialGradient(centerX, shCy, 0, centerX, shCy, shW);
        sh.addColorStop(0, `rgba(28, 18, 45, ${shAlpha})`);
        sh.addColorStop(0.55, `rgba(28, 18, 45, ${shAlpha * 0.4})`);
        sh.addColorStop(1, "rgba(28, 18, 45, 0)");
        ctx.save();
        ctx.translate(centerX, shCy);
        ctx.scale(1, shH / shW);
        ctx.translate(-centerX, -shCy);
        ctx.fillStyle = sh;
        ctx.beginPath();
        ctx.arc(centerX, shCy, shW, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }

      if (activeImg && baseImgOpacity > 0.01) {
        const prevBase = ctx.globalCompositeOperation;
        // The artwork has a white background, so "multiply" lets the white drop
        // out and only the brain's shading show through on the light page.
        ctx.globalCompositeOperation = "multiply";
        ctx.globalAlpha = baseImgOpacity;
        ctx.drawImage(activeImg, brainRect!.x, brainRect!.y, brainRect!.width, brainRect!.height);
        ctx.globalAlpha = 1.0;
        ctx.globalCompositeOperation = prevBase;
      }

      // As the brain grows (digitalAmount rises on inhale → peaks at transform),
      // fade a digital "circuit" version of the brain in over the top — a faded
      // digital appearance inside the brain.
      const digitalImg = isDark ? digitalImageRef.current : digitalLightImageRef.current;
      if (brainRect && digitalImg && digitalAmount > 0.02) {
        const prevComp = ctx.globalCompositeOperation;
        // "lighten" / "screen" so the image's gray background drops out and only
        // the glowing neural brain shows through.
        ctx.globalCompositeOperation = isDark ? "screen" : "lighten";
        ctx.globalAlpha = Math.min(0.9, digitalAmount) * baseImgOpacity;
        ctx.drawImage(digitalImg, brainRect.x, brainRect.y, brainRect.width, brainRect.height);
        ctx.globalAlpha = 1.0;
        ctx.globalCompositeOperation = prevComp;
      }


      const isInsideBrainArea = (x: number, y: number) => {
        if (!brainRect) return true;
        const nx = (x - (brainRect.x + brainRect.width * 0.52)) / (brainRect.width * 0.47);
        const ny = (y - (brainRect.y + brainRect.height * 0.5)) / (brainRect.height * 0.42);
        return nx * nx + ny * ny <= 1.12;
      };

      // 5. Draw Dotted connection lines from cards to brain
      const brainTargets = [
        { x: centerX - zoom * 0.45, y: brainCenterY - zoom * 0.15 },
        { x: centerX - zoom * 0.52, y: brainCenterY + zoom * 0.05 },
        { x: centerX - zoom * 0.38, y: brainCenterY + zoom * 0.2 },
        { x: centerX + zoom * 0.45, y: brainCenterY - zoom * 0.15 },
        { x: centerX + zoom * 0.52, y: brainCenterY + zoom * 0.05 },
        { x: centerX + zoom * 0.38, y: brainCenterY + zoom * 0.2 },
      ];

      NODES.forEach((node, idx) => {
        const target = brainTargets[idx];
        if (!target) return;

        const isLeft = node.side === "left";
        const cardX = isLeft ? width * (node.left ?? 0.12) : width * (1.0 - (node.right ?? 0.12));
        const cardY = height * node.top;

        // Draw dotted spline line from card tip to brain target
        ctx.strokeStyle = isDark 
          ? `rgba(240, 171, 252, ${lineOpacity * (0.22 + (phase === "inhale" ? phaseProgress * 0.2 : 0))})` 
          : `rgba(236, 72, 153, ${lineOpacity * (0.32 + (phase === "inhale" ? phaseProgress * 0.26 : 0))})`;
        ctx.lineWidth = 1;
        ctx.setLineDash([3, 4]);
        ctx.beginPath();
        ctx.moveTo(cardX, cardY);
        ctx.quadraticCurveTo(
          (cardX + target.x) / 2,
          (cardY + target.y) / 2 + (isLeft ? 30 : -30),
          target.x,
          target.y
        );
        ctx.stroke();
        ctx.setLineDash([]);
      });

      // 6. Project Brain Particles to 2D
      const projectedBrain: Array<{
        x: number;
        y: number;
        z: number;
        scrX: number;
        scrY: number;
        size: number;
        color: string;
        glow: number;
        opacity: number;
      }> = [];

      for (let i = 0; i < numParticles; i++) {
        const p = particles[i];
        if (!p) continue;
        
        const jitter = Math.sin(cycleTime * 1.6 + p.phase) * 0.0035;
        let px = p.ox * currentBrainScale + jitter;
        let py = p.oy * currentBrainScale + jitter;
        let pz = p.oz * currentBrainScale + jitter;

        if (phase === "transform") {
          const structFactor = phaseProgress * 0.055;
          const conn = connections[i];
          if (conn && conn[0] !== undefined) {
            const nIdx = conn[0];
            const neighbor = particles[nIdx];
            if (neighbor) {
              px += (neighbor.ox * currentBrainScale - px) * structFactor;
              py += (neighbor.oy * currentBrainScale - py) * structFactor;
              pz += (neighbor.oz * currentBrainScale - pz) * structFactor;
            }
          }
        }

        const rx = px * cosY - pz * sinY;
        let rz = px * sinY + pz * cosY;
        const ry = py * cosX - rz * sinX;
        rz = py * sinX + rz * cosX;

        const pScale = focalLength / (focalLength + rz);
        const scrX = centerX + rx * pScale * zoom;
        const scrY = brainCenterY + ry * pScale * zoom;

        projectedBrain.push({
          x: rx,
          y: ry,
          z: rz,
          scrX,
          scrY,
          size: p.size * pScale * (phase === "transform" ? 1.45 : 1.05),
          color: p.color,
          glow: p.glow,
          // Each particle smoothly fades in and out on its own staggered cycle
          // (varied phase + speed) so the brain gently shimmers rather than
          // holding a constant opacity.
          opacity:
            particleOpacity *
            pScale *
            (0.12 + 0.88 * (0.5 + 0.5 * Math.sin(cycleTime * (0.8 + p.speed * 9) + p.phase * 3.0))),
        });
      }

      // (Brain-surface particle shimmer, neural lines and digital scan-lines
      // removed — the brain is kept clean.)

      // 10. Draw data stream particles traveling from nodes to brain
      streams.forEach((stream) => {
        const target = brainTargets[stream.nodeIndex];
        if (!target) return;

        const node = NODES[stream.nodeIndex];
        if (!node) return;

        const isLeft = node.side === "left";
        const startX = isLeft ? width * (node.left ?? 0.12) : width * (1.0 - (node.right ?? 0.12));
        const startY = height * node.top;

        stream.progress += stream.speed * deltaSeconds;
        if (stream.progress > 1.0) {
          stream.progress = 0;
          stream.offsetY = (Math.random() - 0.5) * 0.26;
          stream.color = pickBrainParticleColor();
          stream.glow = 0.46 + Math.random() * 0.58;
          stream.phase = Math.random() * Math.PI * 2;
        }

        const travelAlpha = Math.sin(stream.progress * Math.PI);
        // Particles are released ONLY while the brain is inhaling.
        const streamAlpha = phase === "inhale" ? travelAlpha * (0.35 + 0.65 * phaseProgress) : 0;

        if (streamAlpha > 0.01) {
          const cpX = (startX + target.x) / 2;
          const cpY = (startY + target.y) / 2 + stream.offsetY * zoom * 1.2;

          const p = stream.progress;
          const currX = (1 - p) * (1 - p) * startX + 2 * (1 - p) * p * cpX + p * p * target.x;
          const currY = (1 - p) * (1 - p) * startY + 2 * (1 - p) * p * cpY + p * p * target.y;
          const settlePulse = 0.9 + Math.sin(cycleTime * 0.85 + stream.phase) * 0.1;
          const streamSize = stream.size * (1.1 + p * 0.3) * settlePulse;

          // Neumorphic bead — opaque soft-raised violet dot with a top-left
          // highlight + soft drop shadow, matching the page's neumorphism theme.
          const op = Math.min(1, travelAlpha * 2.6);
          const prevComp = ctx.globalCompositeOperation;
          ctx.globalCompositeOperation = "source-over";
          ctx.save();
          ctx.shadowColor = "rgba(70, 45, 130, 0.5)";
          ctx.shadowBlur = 4;
          ctx.shadowOffsetX = streamSize * 0.45;
          ctx.shadowOffsetY = streamSize * 0.45;
          ctx.fillStyle = `rgba(124, 58, 237, ${op})`;
          ctx.beginPath();
          ctx.arc(currX, currY, streamSize * 1.3, 0, Math.PI * 2);
          ctx.fill();
          ctx.restore();
          ctx.fillStyle = `rgba(221, 212, 255, ${op * 0.85})`;
          ctx.beginPath();
          ctx.arc(currX - streamSize * 0.4, currY - streamSize * 0.4, streamSize * 0.5, 0, Math.PI * 2);
          ctx.fill();
          ctx.globalCompositeOperation = prevComp;
        }
      });

      // 11. Draw Exhale Outward-bound Wavefronts (Ripples)
      if (phase === "exhale") {
        const rippleRadius = phaseProgress * zoom * 1.8;
        const rippleAlpha = Math.max(0, (1.0 - phaseProgress) * 0.28);
        
        if (rippleAlpha > 0.01) {
          ctx.strokeStyle = isDark
            ? `rgba(139, 92, 246, ${rippleAlpha})`
            : `rgba(124, 58, 237, ${rippleAlpha * 0.45})`;
          ctx.lineWidth = isDark ? 2.5 : 1.5;
          ctx.shadowBlur = isDark ? 15 : 5;
          ctx.shadowColor = isDark ? "rgba(139, 92, 246, 0.4)" : "rgba(124, 58, 237, 0.15)";
          
          ctx.beginPath();
          ctx.ellipse(centerX, centerY, rippleRadius, rippleRadius * 0.65, 0, 0, Math.PI * 2);
          ctx.stroke();
          
          ctx.shadowBlur = 0;
        }
      }

      animationFrameId = requestAnimationFrame(tick);
    };

    animationFrameId = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("resize", resize);
      window.removeEventListener("mousemove", handleMouseMove);
    };
  }, []);

  return (
    <section 
      className="relative flex items-center overflow-hidden" 
      style={{ 
        background: "var(--color-bg)",
        minHeight: "100svh",
        color: "var(--color-fg)",
        backgroundImage: `radial-gradient(circle, rgba(124,58,237,0.07) 1px, transparent 1px)`,
        backgroundSize: "44px 44px",
        backgroundPosition: "center center"
      }}
    >
      <div className="relative z-10 mx-auto w-full max-w-[1440px] px-6 pb-10 pt-[5.5rem] md:pb-44 lg:px-12 xl:px-16">
        <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-[45%_55%]">

          {/* ══ LEFT HALF — Premium Neumorphic Copy & CTAs ══ */}
          <div className="flex flex-col gap-6 lg:gap-8">
            
            {/* Social proof pill — neumorphic raised */}
            <div className="inline-flex w-fit items-center gap-2.5 px-4 py-2 rounded-full" style={{ background: "var(--color-bg)", boxShadow: "var(--shadow-neu-sm)" }}>
              <div className="flex -space-x-1.5 mr-1">
                <img className="h-5 w-5 rounded-full border border-bg object-cover" src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=100&h=100&q=80" alt="expert" />
                <img className="h-5 w-5 rounded-full border border-bg object-cover" src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=100&h=100&q=80" alt="expert" />
                <img className="h-5 w-5 rounded-full border border-bg object-cover" src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=100&h=100&q=80" alt="expert" />
              </div>
              <span className="tag-label" style={{ color: "#7c3aed" }}>
                2,400+ Experts Earning Passively
              </span>
            </div>

            {/* Premium bold typography headline */}
            <div className="flex flex-col gap-4">
              <h1 
                className="text-fg"
                style={{ 
                  fontSize: "clamp(2.8rem, 5vw, 5.2rem)", 
                  fontWeight: 900, 
                  letterSpacing: "-0.04em", 
                  lineHeight: 0.94 
                }}
              >
                <HoverText text="Turn Your Expertise" /><br />
                <HoverText text="Into a " />
                <HoverText text="Digital Asset" gradient />
              </h1>

              <p className="text-base md:text-lg leading-relaxed text-fg-muted max-w-[44ch] font-medium">
                Upload once. We transform your knowledge into an AI expert that answers questions, solves problems, and earns for you 24/7.
              </p>
            </div>

            {/* Premium CTA Buttons */}
            <div className="flex flex-col gap-4 sm:flex-row sm:flex-wrap">
              <Link 
                href="/creator/dashboard"
                className="inline-flex items-center justify-center gap-3 px-8 py-4 text-base font-bold text-white transition-all duration-300"
                style={{ 
                  borderRadius: "1rem",
                  background: "linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%)",
                  boxShadow: "var(--shadow-brand)",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "translateY(-3px) scale(1.025)";
                  e.currentTarget.style.boxShadow = "8px 8px 28px rgba(124, 58, 237, 0.55), -4px -4px 14px rgba(255, 255, 255, 0.6)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0) scale(1)";
                  e.currentTarget.style.boxShadow = "var(--shadow-brand)";
                }}
              >
                Create Your Expert AI <ArrowRight className="h-5 w-5" />
              </Link>
              
              <Link 
                href="/explore"
                className="inline-flex items-center justify-center gap-2 px-8 py-4 text-base font-semibold text-fg transition-all duration-300"
                style={{ 
                  borderRadius: "1rem", 
                  background: "var(--color-bg-raised)", 
                  border: "1px solid var(--color-border)",
                  boxShadow: "var(--shadow-neu-sm)",
                  backdropFilter: "blur(12px)"
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = "var(--color-bg-muted)";
                  e.currentTarget.style.boxShadow = "var(--shadow-neu-md)";
                  e.currentTarget.style.transform = "translateY(-3px)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "var(--color-bg-raised)";
                  e.currentTarget.style.boxShadow = "var(--shadow-neu-sm)";
                  e.currentTarget.style.transform = "translateY(0)";
                }}
              >
                Explore Experts
              </Link>
            </div>

            {/* Quick value props — neumorphic grid */}
            <div className="grid grid-cols-2 gap-3 mt-2 max-w-sm">
              {[
                { Icon: Zap,           label: "Live in 10 minutes", desc: "Quick setup" },
                { Icon: Shield,        label: "Verified citations",  desc: "Sources you trust" },
                { Icon: MessageCircle, label: "Unlimited questions", desc: "From your subscribers" },
                { Icon: TrendingUp,    label: "Passive income",      desc: "Earn every month" },
              ].map(({ Icon, label, desc }, idx) => (
                <div
                  key={idx}
                  className="chip-hover flex items-start gap-2.5 px-3 py-2.5"
                  style={{ background: "var(--color-bg)", boxShadow: "var(--shadow-neu-xs)", borderRadius: "0.875rem" }}
                >
                  <div
                    className="flex h-8 w-8 shrink-0 items-center justify-center mt-0.5"
                    style={{ background: "var(--color-bg)", boxShadow: "var(--shadow-neu-sm)", borderRadius: "0.65rem" }}
                  >
                    <Icon className="h-4 w-4" style={{ color: "#7c3aed" }} />
                  </div>
                  <div>
                    <p className="text-xs font-black" style={{ color: "var(--color-fg)", letterSpacing: "-0.01em" }}>{label}</p>
                    <p style={{ fontSize: "0.6rem", color: "var(--color-fg-subtle)" }}>{desc}</p>
                  </div>
                </div>
              ))}
            </div>

          </div>

          {/* ══ RIGHT HALF — 3D Pedestal, Brain, and Neumorphic Orbiting Cards ══ */}
          <div 
            ref={containerRef} 
            className="relative hidden w-full items-center justify-center lg:flex" 
            style={{ 
              height: "clamp(520px, 80vh, 800px)",
              minHeight: 520
            }}
          >
            {/* Canvas layer renders pedestal, curves, and breathing brain particles */}
            <canvas ref={canvasRef} className="absolute z-10 w-full h-full cursor-grab" />

            {/* Absolute overlay HTML Neumorphic Nodes representing orbiting items */}
            {NODES.map((node) => {
              const isLeft = node.side === "left";
              return (
                <div
                  key={node.id}
                  className="hero-orbit-card absolute z-20 select-none"
                  style={{
                    top: `${node.top * 100}%`,
                    ...(isLeft ? { left: `${(node.left ?? 0.12) * 100}%` } : { right: `${(node.right ?? 0.12) * 100}%` }),
                    animationDelay: node.floatDelay,
                  }}
                >
                  <div
                    className="flex items-center gap-3 px-4 py-2.5 transition-all duration-300"
                    style={{
                      background: "var(--color-bg)",
                      boxShadow: "var(--shadow-neu-md)",
                      borderRadius: "1rem",
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = "translateY(-4px) scale(1.04)";
                      e.currentTarget.style.boxShadow = "var(--shadow-neu-lg)";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = "translateY(0) scale(1)";
                      e.currentTarget.style.boxShadow = "var(--shadow-neu-md)";
                    }}
                  >
                    <div className="flex h-8 w-8 items-center justify-center text-base shrink-0" style={{ background: "var(--color-bg)", boxShadow: "var(--shadow-neu-xs)", borderRadius: "0.65rem" }}>
                      {node.emoji}
                    </div>
                    <div className="flex flex-col min-w-0">
                      <span className="text-[10px] font-bold text-fg leading-tight">
                        {node.title}
                      </span>
                      <span className="text-[8px] text-fg-subtle mt-0.5 leading-none">
                        {node.sub}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}

          </div>

        </div>
      </div>

      {/* ── FOOTER SUPPORTS & TRUSTED BAR (at bottom of hero) ── */}
      <div 
        className="absolute bottom-6 left-6 right-6 z-20 hidden flex-col items-center justify-between gap-6 px-8 py-5 md:flex md:flex-row"
        style={{
          background: "var(--color-bg)",
          boxShadow: "var(--shadow-neu-md)",
          borderRadius: "1.25rem",
        }}
      >
        <div className="flex flex-col gap-2">
          <span className="font-mono text-[9px] font-black uppercase tracking-widest text-fg-subtle">
            Supports All Major Formats
          </span>
          <div className="flex flex-wrap items-center gap-5 mt-0.5">
            {[
              { Icon: Video, label: "Video" },
              { Icon: Music, label: "Audio" },
              { Icon: FileText, label: "PDF" },
              { Icon: ImageIcon, label: "Images" },
              { Icon: File, label: "Docs" },
              { Icon: FileText, label: "Notes" },
              { Icon: FileCode, label: "Markdown" },
            ].map(({ Icon, label }) => (
              <div key={label} className="flex items-center gap-1.5 text-xs text-fg-muted font-bold">
                <Icon className="h-4 w-4" style={{ color: "#7c3aed" }} />
                {label}
              </div>
            ))}
            <span className="text-xs text-fg-subtle font-bold">& More</span>
          </div>
        </div>

        <div className="flex flex-col gap-2 items-start md:items-end">
          <span className="font-mono text-[9px] font-black uppercase tracking-widest text-fg-subtle">
            Trusted By Experts Worldwide
          </span>
          <div className="flex items-center gap-3 mt-0.5">
            <div className="flex -space-x-2">
              <img className="h-6 w-6 rounded-full border border-bg-raised object-cover" src="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=100&h=100&q=80" alt="expert" />
              <img className="h-6 w-6 rounded-full border border-bg-raised object-cover" src="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=100&h=100&q=80" alt="expert" />
              <img className="h-6 w-6 rounded-full border border-bg-raised object-cover" src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=100&h=100&q=80" alt="expert" />
              <img className="h-6 w-6 rounded-full border border-bg-raised object-cover" src="https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=100&h=100&q=80" alt="expert" />
            </div>
            <span className="text-xs font-bold text-fg">+2.4K</span>
          </div>
        </div>
      </div>
    </section>
  );
}
