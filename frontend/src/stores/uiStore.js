import { create } from 'zustand'

export const useUIStore = create((set) => ({
  sidebarOpen: true,
  theme: localStorage.getItem('theme') || 'dark',
  language: localStorage.getItem('language') || 'th',

  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setTheme: (theme) => {
    localStorage.setItem('theme', theme)
    document.documentElement.setAttribute('data-theme', theme)
    set({ theme })
  },
  setLanguage: (language) => {
    localStorage.setItem('language', language)
    set({ language })
  },
}))
