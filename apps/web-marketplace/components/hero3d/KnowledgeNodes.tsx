"use client";

import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import * as THREE from "three";
import { sampleCycle } from "./breathingCycle";
import { KNOWLEDGE_NODES } from "./nodes";
import type { BrainPalette } from "./BrainParticles";

function Node({
  label,
  pos,
  index,
  palette,
}: {
  label: string;
  pos: [number, number, number];
  index: number;
  palette: BrainPalette;
}) {
  const dot = useRef<THREE.Mesh>(null);
  const glowMat = useRef<THREE.MeshBasicMaterial>(null);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    const s = sampleCycle(t);
    const pulse = 0.5 + 0.5 * Math.sin(t * 1.6 + index * 0.8);
    // Nodes brighten and swell as the brain breathes in (sending knowledge).
    const intensity = 0.45 + pulse * 0.25 + s.inhale * 0.5;
    if (dot.current) {
      const sc = 0.05 * (0.85 + pulse * 0.25 + s.inhale * 0.4);
      dot.current.scale.setScalar(sc);
    }
    if (glowMat.current) glowMat.current.opacity = Math.min(1, intensity);
  });

  return (
    <group position={pos}>
      <mesh ref={dot}>
        <sphereGeometry args={[1, 16, 16]} />
        <meshBasicMaterial ref={glowMat} color={palette.digital} transparent opacity={0.6} />
      </mesh>
      <Html
        center
        distanceFactor={8}
        position={[0, -0.001, 0]}
        style={{ pointerEvents: "none" }}
        zIndexRange={[10, 0]}
      >
        <div
          style={{
            transform: "translateY(-18px)",
            whiteSpace: "nowrap",
            fontSize: "11px",
            fontWeight: 600,
            letterSpacing: "0.02em",
            color: "var(--color-fg)",
            background: "var(--color-bg)",
            boxShadow: "var(--shadow-neu-sm)",
            borderRadius: "9999px",
            padding: "4px 10px",
            opacity: 0.92,
          }}
        >
          {label}
        </div>
      </Html>
    </group>
  );
}

export function KnowledgeNodes({ palette }: { palette: BrainPalette }) {
  return (
    <group>
      {KNOWLEDGE_NODES.map((n, i) => (
        <Node key={n.label} label={n.label} pos={n.pos} index={i} palette={palette} />
      ))}
    </group>
  );
}
