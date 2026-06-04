"use client";

import { create } from "zustand";
import type {
  BuilderEdge,
  BuilderNode,
  NodeKind,
} from "@/lib/builder/types";

/**
 * Zustand store for the visual builder canvas.
 *
 * Phase 0 stub — only the shape and basic setters are implemented.
 * Compilation, autosave, undo/redo, and graph mutations land in Phase 3
 * per `prompts/skill-creator/01-visual-builder.md`.
 */
export interface BuilderState {
  nodes: BuilderNode[];
  edges: BuilderEdge[];
  selectedNodeId: string | null;

  // basic setters — wired so the React Flow change handlers can drive state
  setNodes: (nodes: BuilderNode[]) => void;
  setEdges: (edges: BuilderEdge[]) => void;
  setSelectedNodeId: (id: string | null) => void;

  // future API (Phase 3 — left unimplemented intentionally):
  // addNode(kind, position): void;
  // updateNodeData(id, patch): void;
  // removeSelected(): void;
  // undo(): void;
  // redo(): void;
}

export const useBuilderStore = create<BuilderState>((set) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  setSelectedNodeId: (id) => set({ selectedNodeId: id }),
}));

/**
 * Convenience selector hook for the currently-selected node.
 */
export function useSelectedNode(): BuilderNode | null {
  return useBuilderStore((s) => {
    if (!s.selectedNodeId) return null;
    return s.nodes.find((n) => n.id === s.selectedNodeId) ?? null;
  });
}

/**
 * Static node-kind metadata used by the palette and inspector.
 */
export interface NodeKindMeta {
  kind: NodeKind;
  label: string;
  description: string;
  /** Tailwind ring / accent color hint used in the palette chip. */
  accent: string;
}

export const NODE_KIND_META: NodeKindMeta[] = [
  {
    kind: "context",
    label: "Context",
    description: "Who the agent is and when to use this skill.",
    accent: "ring-info/60",
  },
  {
    kind: "decision",
    label: "Decision",
    description: "Branch on a question (If yes / If no).",
    accent: "ring-warning/60",
  },
  {
    kind: "parameter",
    label: "Parameter",
    description: "Input the agent should collect from the user.",
    accent: "ring-brand-500/60",
  },
  {
    kind: "action",
    label: "Action",
    description: "Do this step. The workhorse node.",
    accent: "ring-success/60",
  },
  {
    kind: "output",
    label: "Output",
    description: "What the agent produces — terminal node.",
    accent: "ring-price/60",
  },
  {
    kind: "example",
    label: "Example",
    description: "Worked example to anchor behavior.",
    accent: "ring-rating/60",
  },
  {
    kind: "note",
    label: "Note",
    description: "Authoring-only note. Not exported.",
    accent: "ring-fg-subtle/60",
  },
];
