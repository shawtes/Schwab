import { create } from "zustand";
import { devtools } from "zustand/middleware";
import { ConnectionState, Side, Timeframe } from "./types";

interface UiState {
  symbol: string;
  timeframe: Timeframe;
  side: Side;
  size: number;
  commandPaletteOpen: boolean;
  modalOpen: boolean;
  setModalOpen: (open: boolean) => void;
  setSymbol: (symbol: string) => void;
  setTimeframe: (tf: Timeframe) => void;
  setSide: (side: Side) => void;
  setSize: (size: number) => void;
  toggleCommandPalette: (open?: boolean) => void;
  closeModal: () => void;
}

export const useUiStore = create<UiState>()(
  devtools((set) => ({
    symbol: "AAPL",
    timeframe: "5m",
    side: "buy",
    size: 100,
    commandPaletteOpen: false,
    modalOpen: false,
    setModalOpen: (open) => set({ modalOpen: open }),
    setSymbol: (symbol) => set({ symbol }),
    setTimeframe: (timeframe) => set({ timeframe }),
    setSide: (side) => set({ side }),
    setSize: (size) => set({ size }),
    toggleCommandPalette: (open) =>
      set((state) => ({ commandPaletteOpen: open ?? !state.commandPaletteOpen })),
    closeModal: () => set({ modalOpen: false })
  }))
);

interface ConnectionStore {
  status: ConnectionState;
  lastHeartbeat?: number;
  error?: string;
  setStatus: (status: ConnectionState) => void;
  setHeartbeat: (ts: number) => void;
  setError: (msg?: string) => void;
}

export const useConnectionStore = create<ConnectionStore>()(
  devtools((set) => ({
    status: "connecting",
    lastHeartbeat: undefined,
    error: undefined,
    setStatus: (status) => set({ status }),
    setHeartbeat: (ts) => set({ lastHeartbeat: ts }),
    setError: (msg) => set({ error: msg })
  }))
);

