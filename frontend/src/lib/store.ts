'use client';
import { create } from 'zustand';
import type { Module } from './mock';

type State = { module: Module; selectedInvestigation: string; sidebarOpen: boolean; notifications: number; setModule: (module: Module) => void; selectInvestigation: (id: string) => void; toggleSidebar: () => void; clearNotifications: () => void };

const STORAGE_KEY = 'lokii-ui-state';

const defaultState = { module: 'Overview' as Module, selectedInvestigation: 'INV-2026-0418', sidebarOpen: true, notifications: 4 };

function readPersistedState(): Partial<Pick<State, 'module' | 'selectedInvestigation' | 'sidebarOpen' | 'notifications'>> {
  if (typeof window === 'undefined') {
    return {};
  }

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};

    return JSON.parse(raw) as Partial<State>;
  } catch {
    return {};
  }
}

function persistState(state: Partial<State>) {
  if (typeof window === 'undefined') {
    return;
  }

  const current = readPersistedState();
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...current, ...state }));
}

export const useLokiiStore = create<State>((set) => {
  return {
    ...defaultState,
    setModule: (module) => set((state) => {
      const next = { ...state, module };
      persistState({ module });
      return next;
    }),
    selectInvestigation: (selectedInvestigation) => set((state) => {
      const next = { ...state, selectedInvestigation, module: 'Investigation Workspace' as Module };
      persistState({ selectedInvestigation, module: 'Investigation Workspace' });
      return next;
    }),
    toggleSidebar: () => set((state) => {
      const next = { ...state, sidebarOpen: !state.sidebarOpen };
      persistState({ sidebarOpen: next.sidebarOpen });
      return next;
    }),
    clearNotifications: () => set((state) => {
      const next = { ...state, notifications: 0 };
      persistState({ notifications: 0 });
      return next;
    }),
  };
});

export function hydrateLokiiStore() {
  const persisted = readPersistedState();
  if (Object.keys(persisted).length > 0) {
    useLokiiStore.setState((state) => ({ ...state, ...persisted }));
  }
}
