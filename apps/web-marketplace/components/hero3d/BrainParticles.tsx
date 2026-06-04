"use client";

import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { sampleCycle } from "./breathingCycle";
import type { BrainCloud } from "./brainSampling";

export interface BrainPalette {
  organic: string;
  digital: string;
  hot: string;
}

const vertexShader = /* glsl */ `
  uniform float uTime;
  uniform float uBreath;
  uniform float uDigital;
  uniform float uSize;
  uniform float uPixelRatio;
  attribute vec3 aLattice;
  attribute vec3 aRandom;
  varying float vTwinkle;

  void main() {
    // Organic shape morphs toward the structured digital lattice.
    vec3 pos = mix(position, aLattice, uDigital * 0.65);

    // Organic drift — alive when organic, calms as it goes digital.
    float organic = 1.0 - uDigital;
    vec3 n;
    n.x = sin(uTime * 0.6 + pos.y * 4.0 + aRandom.y);
    n.y = sin(uTime * 0.5 + pos.z * 4.0 + aRandom.y * 1.3);
    n.z = sin(uTime * 0.7 + pos.x * 4.0 + aRandom.y * 0.7);
    pos += n * 0.022 * organic;

    // Breathing swell + subtle always-on aliveness pulse.
    float swell = 1.0 + uBreath * 0.07 + sin(uTime * 1.9) * 0.006;
    pos *= swell;

    vec4 mv = modelViewMatrix * vec4(pos, 1.0);
    gl_PointSize = uSize * uPixelRatio * (0.55 + aRandom.x) * (1.0 / -mv.z) * (1.0 + uBreath * 0.35);
    gl_Position = projectionMatrix * mv;
    vTwinkle = aRandom.y;
  }
`;

const fragmentShader = /* glsl */ `
  uniform float uTime;
  uniform float uDigital;
  uniform float uInhale;
  uniform vec3 uColorOrganic;
  uniform vec3 uColorDigital;
  uniform vec3 uColorHot;
  varying float vTwinkle;

  void main() {
    vec2 c = gl_PointCoord - 0.5;
    float d = length(c);
    if (d > 0.5) discard;
    float alpha = smoothstep(0.5, 0.0, d);

    vec3 col = mix(uColorOrganic, uColorDigital, uDigital);
    float tw = 0.5 + 0.5 * sin(uTime * 3.0 + vTwinkle * 6.2831);
    col = mix(col, uColorHot, tw * 0.22 + uInhale * 0.25);

    gl_FragColor = vec4(col, alpha * 0.72);
  }
`;

// Lines reuse the same swell/morph so they track the particles.
const lineVertex = /* glsl */ `
  uniform float uBreath;
  uniform float uDigital;
  attribute vec3 aLattice;
  void main() {
    vec3 pos = mix(position, aLattice, uDigital * 0.65);
    float swell = 1.0 + uBreath * 0.07;
    pos *= swell;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
  }
`;

const lineFragment = /* glsl */ `
  uniform float uDigital;
  uniform vec3 uColorDigital;
  void main() {
    gl_FragColor = vec4(uColorDigital, uDigital * 0.32);
  }
`;

export function BrainParticles({
  cloud,
  palette,
  additive,
  sizeScale = 1,
}: {
  cloud: BrainCloud;
  palette: BrainPalette;
  additive: boolean;
  sizeScale?: number;
}) {
  const pointsMat = useRef<THREE.ShaderMaterial>(null);
  const lineMat = useRef<THREE.ShaderMaterial>(null);

  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uBreath: { value: 0 },
      uDigital: { value: 0 },
      uInhale: { value: 0 },
      uSize: { value: 18 * sizeScale },
      uPixelRatio: { value: typeof window !== "undefined" ? Math.min(window.devicePixelRatio, 2) : 1 },
      uColorOrganic: { value: new THREE.Color(palette.organic) },
      uColorDigital: { value: new THREE.Color(palette.digital) },
      uColorHot: { value: new THREE.Color(palette.hot) },
    }),
    [palette.organic, palette.digital, palette.hot, sizeScale]
  );

  // Point geometry.
  const pointGeo = useMemo(() => {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(cloud.positions, 3));
    g.setAttribute("aLattice", new THREE.BufferAttribute(cloud.lattice, 3));
    g.setAttribute("aRandom", new THREE.BufferAttribute(cloud.randoms, 3));
    return g;
  }, [cloud]);

  // Non-indexed line geometry (two verts per segment, carrying position + lattice).
  const lineGeo = useMemo(() => {
    const segs = cloud.lineIndices.length / 2;
    const pos = new Float32Array(segs * 2 * 3);
    const lat = new Float32Array(segs * 2 * 3);
    for (let s = 0; s < segs; s++) {
      const a = cloud.lineIndices[s * 2]!;
      const b = cloud.lineIndices[s * 2 + 1]!;
      for (let k = 0; k < 3; k++) {
        pos[s * 6 + k] = cloud.positions[a * 3 + k]!;
        pos[s * 6 + 3 + k] = cloud.positions[b * 3 + k]!;
        lat[s * 6 + k] = cloud.lattice[a * 3 + k]!;
        lat[s * 6 + 3 + k] = cloud.lattice[b * 3 + k]!;
      }
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    g.setAttribute("aLattice", new THREE.BufferAttribute(lat, 3));
    return g;
  }, [cloud]);

  useFrame((state) => {
    const s = sampleCycle(state.clock.elapsedTime);
    for (const mat of [pointsMat.current, lineMat.current]) {
      if (!mat) continue;
      const u = mat.uniforms;
      u.uTime!.value = state.clock.elapsedTime;
      u.uBreath!.value = s.breath;
      u.uDigital!.value = s.digital;
      if (u.uInhale) u.uInhale.value = s.inhale;
    }
  });

  return (
    <group>
      <points geometry={pointGeo}>
        <shaderMaterial
          ref={pointsMat}
          uniforms={uniforms}
          vertexShader={vertexShader}
          fragmentShader={fragmentShader}
          transparent
          depthWrite={false}
          blending={additive ? THREE.AdditiveBlending : THREE.NormalBlending}
        />
      </points>
      <lineSegments geometry={lineGeo}>
        <shaderMaterial
          ref={lineMat}
          uniforms={uniforms}
          vertexShader={lineVertex}
          fragmentShader={lineFragment}
          transparent
          depthWrite={false}
          blending={additive ? THREE.AdditiveBlending : THREE.NormalBlending}
        />
      </lineSegments>
    </group>
  );
}
