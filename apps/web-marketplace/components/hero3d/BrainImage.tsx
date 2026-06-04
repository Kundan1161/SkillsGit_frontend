"use client";

import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Billboard, useTexture } from "@react-three/drei";
import * as THREE from "three";
import { sampleCycle } from "./breathingCycle";

// The brain itself is the user's existing artwork rather than a particle cloud.
// It breathes (scale swell), and during the transform phase a digital-overlay
// image crossfades in so the organic brain "becomes digital". Knowledge streams
// and nodes (rendered alongside) flow into it.
export function BrainImage({ isDark }: { isDark: boolean }) {
  const baseRef = useRef<THREE.Mesh>(null);
  const baseMat = useRef<THREE.MeshBasicMaterial>(null);
  const digitalMat = useRef<THREE.MeshBasicMaterial>(null);

  const overlaySrc = isDark ? "/digital_brain_overlay.png" : "/digital_brain_overlay_light.png";
  const textures = useTexture(["/images/hero-brain-transparent.webp", overlaySrc]);
  const brainTex = textures[0]!;
  const digitalTex = textures[1]!;

  // Size the plane to the artwork's aspect ratio (~target height of 4 units).
  const [w, h] = useMemo(() => {
    const img = brainTex.image as HTMLImageElement | undefined;
    const aspect = img && img.height ? img.width / img.height : 1.1;
    const height = 4.0;
    return [height * aspect, height];
  }, [brainTex]);

  useFrame((state) => {
    const s = sampleCycle(state.clock.elapsedTime);
    const swell = 1 + s.breath * 0.07 + Math.sin(state.clock.elapsedTime * 1.9) * 0.006;
    if (baseRef.current) baseRef.current.scale.setScalar(swell);
    // Organic dims slightly as the digital overlay takes over.
    if (baseMat.current) baseMat.current.opacity = 1 - s.digital * 0.35;
    if (digitalMat.current) digitalMat.current.opacity = s.digital;
  });

  return (
    <Billboard>
      <mesh ref={baseRef}>
        <planeGeometry args={[w, h]} />
        <meshBasicMaterial
          ref={baseMat}
          map={brainTex}
          transparent
          depthWrite={false}
          toneMapped={false}
        />
        {/* Digital overlay sits just in front, fades in during transform. */}
        <mesh position={[0, 0, 0.01]}>
          <planeGeometry args={[w, h]} />
          <meshBasicMaterial
            ref={digitalMat}
            map={digitalTex}
            transparent
            opacity={0}
            depthWrite={false}
            toneMapped={false}
            blending={isDark ? THREE.AdditiveBlending : THREE.NormalBlending}
          />
        </mesh>
      </mesh>
    </Billboard>
  );
}
