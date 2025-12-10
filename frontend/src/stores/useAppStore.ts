import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

interface AppState {
  // UI State
  sidebarCollapsed: boolean
  commandPaletteOpen: boolean
  
  // Active selections
  activeJobId: string | null
  activeScanId: string | null
  
  // Actions
  toggleSidebar: () => void
  setSidebarCollapsed: (collapsed: boolean) => void
  toggleCommandPalette: () => void
  setActiveJobId: (jobId: string | null) => void
  setActiveScanId: (scanId: string | null) => void
}

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        // Initial state
        sidebarCollapsed: false,
        commandPaletteOpen: false,
        activeJobId: null,
        activeScanId: null,
        
        // Actions
        toggleSidebar: () =>
          set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
        
        setSidebarCollapsed: (collapsed) =>
          set({ sidebarCollapsed: collapsed }),
        
        toggleCommandPalette: () =>
          set((state) => ({ commandPaletteOpen: !state.commandPaletteOpen })),
        
        setActiveJobId: (jobId) =>
          set({ activeJobId: jobId }),
        
        setActiveScanId: (scanId) =>
          set({ activeScanId: scanId }),
      }),
      {
        name: 'app-storage',
        partialize: (state) => ({
          sidebarCollapsed: state.sidebarCollapsed,
        }),
      }
    ),
    { name: 'AppStore' }
  )
)

