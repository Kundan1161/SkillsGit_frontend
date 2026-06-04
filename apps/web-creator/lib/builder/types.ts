/**
 * Shape definitions for the React Flow canvas state, mirroring
 * `prompts/skill-creator/01-visual-builder.md`.
 *
 * Phase 0: types only; no compiler / parser yet.
 */

import type { Edge as XYEdge, Node as XYNode } from "@xyflow/react";

export type NodeKind =
  | "context"
  | "decision"
  | "parameter"
  | "action"
  | "output"
  | "example"
  | "note";

export interface ContextData extends Record<string, unknown> {
  title: string;
  description: string;
  trigger_keywords: string[];
  example_invocations: string[];
}

export interface DecisionBranch {
  label: string;
  instruction: string;
}

export interface DecisionData extends Record<string, unknown> {
  title: string;
  question: string;
  branches: DecisionBranch[];
}

export interface ParameterData extends Record<string, unknown> {
  name: string;
  label: string;
  type: "text" | "file" | "url" | "json" | "number" | "choice";
  required: boolean;
  description: string;
  choices?: string[];
}

export interface ActionData extends Record<string, unknown> {
  title: string;
  instruction: string;
  uses_tool?: string;
}

export interface OutputData extends Record<string, unknown> {
  name: string;
  type: "text" | "markdown" | "json" | "file";
  description: string;
  schema?: string;
}

export interface ExampleData extends Record<string, unknown> {
  title: string;
  input_summary: string;
  output_summary: string;
  full_example_md?: string;
}

export interface NoteData extends Record<string, unknown> {
  text: string;
}

export type NodeData =
  | ({ kind: "context" } & ContextData)
  | ({ kind: "decision" } & DecisionData)
  | ({ kind: "parameter" } & ParameterData)
  | ({ kind: "action" } & ActionData)
  | ({ kind: "output" } & OutputData)
  | ({ kind: "example" } & ExampleData)
  | ({ kind: "note" } & NoteData);

/**
 * React Flow node + edge specialisations. We re-export `xyflow`'s
 * generic types parameterised with our data so consumers don't
 * have to repeat the union everywhere.
 */
export type BuilderNode = XYNode<NodeData, NodeKind>;

export interface BuilderEdgeData extends Record<string, unknown> {
  branchLabel?: string;
}
export type BuilderEdge = XYEdge<BuilderEdgeData>;
