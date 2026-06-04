// Single source of truth for the brain's breathing timeline.
//
// One ~10s loop tells the story:
//   inhale    (0   – 3.5s) : brain swells, knowledge streams flow inward
//   transform (3.5 – 5.5s) : organic brain morphs into a digital neural network
//   exhale    (5.5 – 10s)  : brain settles, intelligence radiates outward
//
// Everything (particle shader uniforms, data streams, node pulses, camera) reads
// from this so the whole scene stays in lockstep. The envelope is always in
// motion — no flat "hold" — so the motion reads as living breath.

export const CYCLE = {
  inhaleEnd: 3.5,
  transformEnd: 5.5,
  duration: 10.0,
} as const;

export type BreathPhase = "inhale" | "transform" | "exhale";

export interface BreathState {
  phase: BreathPhase;
  /** 0 = fully exhaled, 1 = fully inhaled. Drives the brain's swell. */
  breath: number;
  /** 0 = organic brain, 1 = full digital neural network. */
  digital: number;
  /** >0 only while actively breathing in — drives knowledge stream intensity. */
  inhale: number;
  /** 0..1 progress through the current phase. */
  phaseProgress: number;
}

// Smootherstep — C2 continuous, no popping at phase seams.
const ease = (x: number) => {
  const t = Math.min(Math.max(x, 0), 1);
  return t * t * t * (t * (t * 6 - 15) + 10);
};

export function sampleCycle(time: number): BreathState {
  const t = time % CYCLE.duration;

  if (t < CYCLE.inhaleEnd) {
    const p = ease(t / CYCLE.inhaleEnd);
    return {
      phase: "inhale",
      breath: p,
      digital: p * 0.35,
      inhale: Math.sin(p * Math.PI), // peaks mid-inhale
      phaseProgress: p,
    };
  }

  if (t < CYCLE.transformEnd) {
    const p = ease((t - CYCLE.inhaleEnd) / (CYCLE.transformEnd - CYCLE.inhaleEnd));
    return {
      phase: "transform",
      // Gently crest past full and ease back — never frozen.
      breath: 1.0 - 0.12 * Math.sin(p * Math.PI),
      digital: 0.35 + 0.65 * ease(p),
      inhale: 0.15 * (1 - p),
      phaseProgress: p,
    };
  }

  const p = ease((t - CYCLE.transformEnd) / (CYCLE.duration - CYCLE.transformEnd));
  return {
    phase: "exhale",
    breath: 1.0 - p,
    digital: 1.0 - p, // dissolve back toward organic
    inhale: 0,
    phaseProgress: p,
  };
}
