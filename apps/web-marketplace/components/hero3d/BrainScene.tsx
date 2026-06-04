"use client";

import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Stars } from "@react-three/drei";
import { EffectComposer, Bloom, DepthOfField, Vignette } from "@react-three/postprocessing";
import * as THREE from "three";
import { BrainImage } from "./BrainImage";
import { KnowledgeNodes } from "./KnowledgeNodes";
import { DataStreams } from "./DataStreams";
import type { BrainPalette } from "./BrainParticles";

export interface SceneQuality {
  bloom: number;
  dof: boolean;
  stars: number;
}

function BrainGroup({ palette, isDark }: { palette: BrainPalette; isDark: boolean }) {
  const group = useRef<THREE.Group>(null);
  const target = useRef({ x: 0, y: 0 });

  useFrame((state) => {
    if (!group.current) return;
    // Subtle pointer parallax + slow idle drift. The brain billboard always
    // faces camera, so this mainly shifts the orbiting nodes/streams.
    const t = state.clock.elapsedTime;
    target.current.y = state.pointer.x * 0.16 + Math.sin(t * 0.08) * 0.06;
    target.current.x = -state.pointer.y * 0.1;
    group.current.rotation.y += (target.current.y - group.current.rotation.y) * 0.04;
    group.current.rotation.x += (target.current.x - group.current.rotation.x) * 0.04;
  });

  return (
    <group ref={group}>
      <BrainImage isDark={isDark} />
      <KnowledgeNodes palette={palette} />
      <DataStreams palette={palette} />
    </group>
  );
}

export function BrainScene({
  palette,
  additive,
  quality,
}: {
  palette: BrainPalette;
  additive: boolean;
  quality: SceneQuality;
}) {
  return (
    <>
      {/* Canvas stays transparent so it blends with the page's theme bg. */}
      <ambientLight intensity={0.6} />

      {quality.stars > 0 && (
        <Stars radius={40} depth={30} count={quality.stars} factor={3} saturation={0} fade speed={0.4} />
      )}

      <BrainGroup palette={palette} isDark={additive} />

      <EffectComposer enableNormalPass={false}>
        {/* Bloom is the cinematic glow on the dark stage. On the light theme it
            washes the bright brain into a white haze, so we keep it minimal and
            only bloom the very brightest highlights. */}
        <Bloom
          intensity={quality.bloom}
          luminanceThreshold={additive ? 0.2 : 0.82}
          luminanceSmoothing={0.9}
          mipmapBlur
        />
        <Vignette eskil={false} offset={0.4} darkness={additive ? 0.55 : 0.0} />
      </EffectComposer>
    </>
  );
}
