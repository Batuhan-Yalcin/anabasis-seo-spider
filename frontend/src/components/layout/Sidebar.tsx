import { NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  LayoutDashboard,
  FolderOpen,
  Search,
  History,
  Settings,
  Activity,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'
import { useAppStore } from '@/stores/useAppStore'
import { useTranslation } from '@/lib/i18n'
import { cn } from '@/lib/utils'

const navigationKeys = [
  { key: 'nav.dashboard', href: '/', icon: LayoutDashboard },
  { key: 'nav.projects', href: '/projects', icon: FolderOpen },
  { key: 'nav.scans', href: '/scans', icon: Search },
  { key: 'nav.history', href: '/history', icon: History },
  { key: 'nav.settings', href: '/settings', icon: Settings },
  { key: 'nav.monitoring', href: '/monitoring', icon: Activity },
] as const

export function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useAppStore()
  const { t } = useTranslation()

  return (
    <motion.aside
      initial={false}
      animate={{ width: sidebarCollapsed ? 80 : 256 }}
      className="fixed left-0 top-0 z-40 h-screen border-r border-glass-border bg-background-secondary"
    >
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center justify-between px-4 border-b border-glass-border">
          {!sidebarCollapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center space-x-2"
            >
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-accent-primary to-accent-secondary" />
              <div>
                <h1 className="text-sm font-bold text-text-primary">AI Anabasis</h1>
                <p className="text-xs text-text-tertiary">SEO Spider</p>
              </div>
            </motion.div>
          )}
          
          <button
            onClick={toggleSidebar}
            className="rounded-lg p-2 hover:bg-background-tertiary transition-colors"
          >
            {sidebarCollapsed ? (
              <ChevronRight className="h-4 w-4 text-text-secondary" />
            ) : (
              <ChevronLeft className="h-4 w-4 text-text-secondary" />
            )}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 p-4">
          {navigationKeys.map((item) => (
            <NavLink
              key={item.key}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  'flex items-center rounded-lg px-3 py-2.5 text-sm font-medium transition-all',
                  'hover:bg-background-tertiary hover:text-text-primary',
                  isActive
                    ? 'bg-gradient-to-r from-accent-primary/10 to-accent-secondary/10 text-accent-primary border-l-2 border-accent-primary'
                    : 'text-text-secondary'
                )
              }
            >
              <item.icon className="h-5 w-5 shrink-0" />
              {!sidebarCollapsed && (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="ml-3"
                >
                  {t(item.key as any)}
                </motion.span>
              )}
            </NavLink>
          ))}
        </nav>

        {/* User profile */}
        <div className="border-t border-glass-border p-4">
          <div className="flex items-center space-x-3">
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-accent-primary to-accent-secondary" />
            {!sidebarCollapsed && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <p className="text-sm font-medium text-text-primary">Admin User</p>
                <p className="text-xs text-text-tertiary">admin@anabasis.ai</p>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </motion.aside>
  )
}

