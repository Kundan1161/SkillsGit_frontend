"use client";

import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { sampleCycle } from "./breathingCycle";
import { KNOWLEDGE_NODES } from "./nodes";
import type { BrainPalette } from "./BrainParticles";

const PER_NODE = 70;

const vertexShader = /* glsl */ `
  uniform float uTime;
  uniform float uInhale;
  uniform float uSize;
  uniform float uPixelRatio;
  attribute vec3 aStart;
  attribute vec3 aControl;
  attribute float aSeed;
  varying float vAlpha;

  void main() {
    // Wrap progress along the bezier; faster while inhaling.
    float speed = 0.16 + 0.18 * uInhale;
    float prog = fract(aSeed + uTime * speed * (0.6 + aSeed * 0.8));

    vec3 target = vec3(0.0); // brain center
    vec3 a = mix(aStart, aControl, prog);
    vec3 b = mix(aControl, target, prog);
    vec3 pos = mix(a, b, prog);

    // Brightest mid-flight, gated by the inhale so streams flow on inhale.
    float bell = sin(prog * 3.14159);
    vAlpha = bell * uInhale;

    vec4 mv = modelViewMatrix * vec4(pos, 1.0);
    gl_PointSize = uSize * uPixelRatio * (1.0 / -mv.z) * (0.7 + bell * 0.6);
    gl_Position = projectionMatrix * mv;
  }
`;

const fragmentShader = /* glsl */ `
  uniform vec3 uColor;
  varying float vAlpha;
  void main() {
    if (vAlpha <= 0.01) discard;
    vec2 c = gl_PointCoord - 0.5;
    float d = length(c);
    if (d > 0.5) discard;
    float a = smoothstep(0.5, 0.0, d) * vAlpha;
    gl_FragColor = vec4(uColor, a);
  }
`;

export function DataStreams({ palette }: { palette: BrainPalette }) {
  const matRef = useRef<THREE.ShaderMaterial>(null);

  const geo = useMemo(() => {
    const total = KNOWLEDGE_NODES.length * PER_NODE;
    const position = new Float32Array(total * 3); // unused but required
    const aStart = new Float32Array(total * 3);
    const aControl = new Float32Array(total * 3);
    const aSeed = new Float32Array(total);

    let i = 0;
    for (const node of KNOWLEDGE_NODES) {
      const [sx, sy, sz] = node.pos;
      for (let k = 0; k < PER_NODE; k++) {
        // Slight scatter around the source so streams aren't a single line.
        const jx = (Math.random() - 0.5) * 0.25;
        const jy = (Math.random() - 0.5) * 0.25;
        const jz = (Math.random() - 0.5) * 0.25;
        aStart[i * 3] = sx + jx;
        aStart[i * 3 + 1] = sy + jy;
        aStart[i * 3 + 2] = sz + jz;

        // Control point bends the path into a curved neural pathway:
        // pull toward center but bow outward/up.
        aControl[i * 3] = sx * 0.45 + (Math.random() - 0.5) * 0.5;
        aControl[i * 3 + 1] = sy * 0.45 + 0.4 + (Math.random() - 0.5) * 0.5;
        aControl[i * 3 + 2] = sz * 0.5 + 0.4 + (Math.random() - 0.5) * 0.4;

        aSeed[i] = Math.random();
        i++;
      }
    }

    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(position, 3));
    g.setAttribute("aStart", new THREE.BufferAttribute(aStart, 3));
    g.setAttribute("aControl", new THREE.BufferAttribute(aControl, 3));
    g.setAttribute("aSeed", new THREE.BufferAttribute(aSeed, 1));
    return g;
  }, []);

  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uInhale: { value: 0 },
      uSize: { value: 22 },
      uPixelRatio: { value: typeof window !== "undefined" ? Math.min(window.devicePixelRatio, 2) : 1 },
      uColor: { value: new THREE.Color(palette.hot) },
    }),
    [palette.hot]
  );

  useFrame((state) => {
    if (!matRef.current) return;
    const s = sampleCycle(state.clock.elapsedTime);
    matRef.current.uniforms.uTime!.value = state.clock.elapsedTime;
    matRef.current.uniforms.uInhale!.value = Math.max(s.inhale, s.phase === "transform" ? 0.25 : 0);
  });

  return (
    <points geometry={geo}>
      <shaderMaterial
        ref={matRef}
        uniforms={uniforms}
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        transparent
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}
