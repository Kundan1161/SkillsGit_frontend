// Builds the brain point cloud.
//
// Primary path: sample the alpha silhouette of the existing brain image into a
// recognizable, volumetric 3D point cloud — no external 3D asset required.
// Each particle also carries a "digital lattice" target position (quantized to a
// grid) so the vertex shader can morph organic → structured neural network.
// A sparse set of nearest-neighbour line segments gives the "neural connections
// illuminate" effect during the transform phase.
//
// If a real mesh is dropped at /models/brain.glb later, swap this loader for a
// THREE MeshSurfaceSampler over the loaded geometry — the rest of the pipeline
// (attributes, shader, lines) is identical.

export interface BrainCloud {
  /** xyz organic positions, length = count*3 */
  positions: Float32Array;
  /** xyz quantized "digital lattice" positions, length = count*3 */
  lattice: Float32Array;
  /** per-particle randoms (size jitter, twinkle phase, depth), length = count*3 */
  randoms: Float32Array;
  /** index pairs into the particle array for neural connection lines */
  lineIndices: Uint32Array;
  count: number;
}

const IMG_SRC = "/images/hero-brain-transparent.webp";

function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}

export async function buildBrainCloud(count: number): Promise<BrainCloud> {
  const img = await loadImage(IMG_SRC);

  // Downscale to a manageable sampling buffer.
  const W = 360;
  const H = Math.max(1, Math.round((img.naturalHeight / img.naturalWidth) * W));
  const canvas = document.createElement("canvas");
  canvas.width = W;
  canvas.height = H;
  const ctx = canvas.getContext("2d", { willReadFrequently: true })!;
  ctx.drawImage(img, 0, 0, W, H);
  const data = ctx.getImageData(0, 0, W, H).data;

  const aspect = W / H;
  const positions = new Float32Array(count * 3);
  const lattice = new Float32Array(count * 3);
  const randoms = new Float32Array(count * 3);

  // Rejection-sample points where the silhouette is opaque.
  let placed = 0;
  let guard = 0;
  const maxGuard = count * 200;
  while (placed < count && guard < maxGuard) {
    guard++;
    const px = Math.floor(Math.random() * W);
    const py = Math.floor(Math.random() * H);
    const alpha = data[(py * W + px) * 4 + 3] ?? 0;
    if (alpha < 110) continue;

    // Normalised, centered coords. x scaled by aspect so the brain isn't squashed.
    const nx = ((px / W) * 2 - 1) * aspect;
    const ny = -((py / H) * 2 - 1);

    // Fake volume: thicker toward the silhouette interior. Distance from the
    // vertical mid-line gives a lobed bulge; a random sign spreads front/back.
    const interior = 1 - Math.min(1, Math.abs(nx) / (0.92 * aspect));
    const thickness = 0.34 * Math.sqrt(Math.max(0, interior));
    const nz = (Math.random() * 2 - 1) * thickness;

    const i3 = placed * 3;
    // Scale the whole cloud down to a tidy ~1.4 unit brain.
    const s = 0.78;
    const x = nx * s;
    const y = ny * s;
    const z = nz;
    positions[i3] = x;
    positions[i3 + 1] = y;
    positions[i3 + 2] = z;

    // Digital lattice target: quantize to a grid for a structured network look.
    const q = 0.085;
    lattice[i3] = Math.round(x / q) * q;
    lattice[i3 + 1] = Math.round(y / q) * q;
    lattice[i3 + 2] = Math.round(z / q) * q;

    randoms[i3] = Math.random(); // size jitter
    randoms[i3 + 1] = Math.random() * Math.PI * 2; // twinkle phase
    randoms[i3 + 2] = Math.random(); // misc

    placed++;
  }

  // Neural connection lines: connect a subset of particles to a near neighbour
  // found in a coarse spatial hash. Kept sparse so it reads as a network, cheap
  // to build, and light to render.
  const cell = 0.16;
  const hash = new Map<string, number[]>();
  const key = (x: number, y: number, z: number) =>
    `${Math.floor(x / cell)},${Math.floor(y / cell)},${Math.floor(z / cell)}`;
  for (let i = 0; i < placed; i++) {
    const k = key(positions[i * 3]!, positions[i * 3 + 1]!, positions[i * 3 + 2]!);
    const arr = hash.get(k);
    if (arr) arr.push(i);
    else hash.set(k, [i]);
  }

  const linePairs: number[] = [];
  const lineCap = Math.min(2600, Math.floor(placed * 0.4));
  const stride = Math.max(1, Math.floor(placed / lineCap));
  for (let i = 0; i < placed; i += stride) {
    const x = positions[i * 3]!;
    const y = positions[i * 3 + 1]!;
    const z = positions[i * 3 + 2]!;
    let best = -1;
    let bestD = Infinity;
    // search this cell + neighbours
    for (let dx = -1; dx <= 1; dx++)
      for (let dy = -1; dy <= 1; dy++)
        for (let dz = -1; dz <= 1; dz++) {
          const arr = hash.get(
            `${Math.floor(x / cell) + dx},${Math.floor(y / cell) + dy},${Math.floor(z / cell) + dz}`
          );
          if (!arr) continue;
          for (const j of arr) {
            if (j === i) continue;
            const ddx = positions[j * 3]! - x;
            const ddy = positions[j * 3 + 1]! - y;
            const ddz = positions[j * 3 + 2]! - z;
            const d = ddx * ddx + ddy * ddy + ddz * ddz;
            if (d < bestD) {
              bestD = d;
              best = j;
            }
          }
        }
    if (best >= 0) {
      linePairs.push(i, best);
    }
  }

  return {
    positions: positions.subarray(0, placed * 3),
    lattice: lattice.subarray(0, placed * 3),
    randoms: randoms.subarray(0, placed * 3),
    lineIndices: new Uint32Array(linePairs),
    count: placed,
  };
}
