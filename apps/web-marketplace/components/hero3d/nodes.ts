// Knowledge sources that orbit the brain. Positions are in the brain group's
// local space (the brain itself spans roughly ±1 unit). Shared by the labelled
// nodes and the data-stream particles so streams launch from the right spot.

export interface KnowledgeNode {
  label: string;
  pos: [number, number, number];
}

export const KNOWLEDGE_NODES: KnowledgeNode[] = [
  { label: "GitHub", pos: [-1.95, 0.85, 0.4] },
  { label: "Videos", pos: [-2.15, -0.05, 0.6] },
  { label: "Audio", pos: [-1.9, -0.95, 0.4] },
  { label: "PDFs", pos: [1.95, 0.85, 0.4] },
  { label: "Case Studies", pos: [2.15, -0.05, 0.6] },
  { label: "Projects", pos: [1.9, -0.95, 0.4] },
  { label: "Notes", pos: [-0.7, 1.55, 0.5] },
  { label: "Conversations", pos: [0.7, 1.55, 0.5] },
];
