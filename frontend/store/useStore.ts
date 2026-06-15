import { create } from "zustand";
import type {
  GTMStrategy,
  ContentAsset,
  AgentEvent,
  KnowledgeDocument,
  StrategyRecord,
} from "@/types";

interface AppStore {
  // Strategy
  currentStrategy: GTMStrategy | null;
  strategies: StrategyRecord[];
  setStrategy: (strategy: GTMStrategy | null) => void;
  setStrategies: (strategies: StrategyRecord[]) => void;

  // Content
  contentAssets: ContentAsset[];
  addContentAsset: (asset: ContentAsset) => void;
  setContentAssets: (assets: ContentAsset[]) => void;

  // Agent Events
  agentEvents: AgentEvent[];
  addAgentEvent: (event: AgentEvent) => void;
  clearAgentEvents: () => void;

  // Knowledge
  knowledgeDocs: KnowledgeDocument[];
  setKnowledgeDocs: (docs: KnowledgeDocument[]) => void;
}

export const useStore = create<AppStore>((set) => ({
  // Strategy
  currentStrategy: null,
  strategies: [],
  setStrategy: (strategy) => set({ currentStrategy: strategy }),
  setStrategies: (strategies) => set({ strategies }),

  // Content
  contentAssets: [],
  addContentAsset: (asset) =>
    set((state) => ({ contentAssets: [...state.contentAssets, asset] })),
  setContentAssets: (assets) => set({ contentAssets: assets }),

  // Agent Events
  agentEvents: [],
  addAgentEvent: (event) =>
    set((state) => ({ agentEvents: [...state.agentEvents, event] })),
  clearAgentEvents: () => set({ agentEvents: [] }),

  // Knowledge
  knowledgeDocs: [],
  setKnowledgeDocs: (docs) => set({ knowledgeDocs: docs }),
}));
