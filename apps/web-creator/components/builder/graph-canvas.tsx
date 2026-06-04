"use client";

import { useCallback } from "react";
import {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  type NodeChange,
  type EdgeChange,
  applyNodeChanges,
  applyEdgeChanges,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

import { Sparkles } from "lucide-react";
import { useBuilderStore } from "@/lib/builder/store";
import type { BuilderEdge, BuilderNode } from "@/lib/builder/types";

/**
 * Phase 0 React Flow stub.
 *
 * - Renders the canvas with controls, minimap, and a dotted background.
 * - Wires node/edge change handlers to the Zustand store so dragging
 *   existing nodes (when there are any) feels real.
 * - Drop-handling for the palette's drag payload is a TODO for Phase 3.
 * - Empty-state overlay sits above the canvas until the first node lands.
 */
function CanvasInner() {
  const nodes = useBuilderStore((s) => s.nodes);
  const edges = useBuilderStore((s) => s.edges);
  const setNodes = useBuilderStore((s) => s.setNodes);
  const setEdges = useBuilderStore((s) => s.setEdges);
  const setSelectedNodeId = useBuilderStore((s) => s.setSelectedNodeId);

  const onNodesChange = useCallback(
    (changes: NodeChange<BuilderNode>[]) => {
      setNodes(applyNodeChanges(changes, nodes));
    },
    [nodes, setNodes],
  );

  const onEdgesChange = useCallback(
    (changes: EdgeChange<BuilderEdge>[]) => {
      setEdges(applyEdgeChanges(changes, edges));
    },
    [edges, setEdges],
  );

  return (
    <div className="relative h-full w-full bg-bg-muted">
      <ReactFlow<BuilderNode, BuilderEdge>
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onSelectionChange={({ nodes: selected }) => {
          setSelectedNodeId(selected[0]?.id ?? null);
        }}
        fitView
        proOptions={{ hideAttribution: true }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={16}
          size={1}
          className="!bg-bg-muted"
        />
        <Controls className="!rounded-md !border !border-border !bg-bg-raised" />
        <MiniMap
          pannable
          zoomable
          maskColor="rgb(15 23 42 / 0.7)"
          className="!rounded-md !border !border-border !bg-bg-raised"
        />
      </ReactFlow>

      {nodes.length === 0 ? (
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
          <div className="rounded-lg border border-dashed border-border bg-bg-raised/80 px-6 py-5 text-center shadow-md backdrop-blur">
            <Sparkles
              className="mx-auto mb-2 h-6 w-6 text-brand-500"
              aria-hidden
            />
            <p className="text-sm font-medium text-fg">
              Drag a node from the left to begin
            </p>
            <p className="mt-1 text-xs text-fg-muted">
              Or start from a template in the gallery.
            </p>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export function GraphCanvas() {
  return (
    <ReactFlowProvider>
      <CanvasInner />
    </ReactFlowProvider>
  );
}
