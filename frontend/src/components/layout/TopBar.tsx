import { Search, Bell, Command } from 'lucide-react'
import { useAppStore } from '@/stores/useAppStore'
import { LanguageSwitcher } from '@/components/ui/LanguageSwitcher'
import { useTranslation } from '@/lib/i18n'

export function TopBar() {
  const toggleCommandPalette = useAppStore((state) => state.toggleCommandPalette)
  const { t } = useTranslation()

  return (
    <header className="sticky top-0 z-30 h-16 border-b border-glass-border bg-background-secondary/80 backdrop-blur-lg">
      <div className="flex h-full items-center justify-between px-6">
        {/* Search */}
        <button
          onClick={toggleCommandPalette}
          className="flex items-center space-x-2 rounded-lg border border-glass-border bg-background-tertiary px-4 py-2 text-sm text-text-secondary hover:border-accent-primary/50 hover:text-text-primary transition-all"
        >
          <Search className="h-4 w-4" />
          <span>{t('action.search')}...</span>
          <kbd className="ml-auto inline-flex h-5 items-center gap-1 rounded border border-glass-border bg-background-primary px-1.5 font-mono text-xs text-text-tertiary">
            <Command className="h-3 w-3" />K
          </kbd>
        </button>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          {/* Language Switcher */}
          <LanguageSwitcher />
          
          {/* Notifications */}
          <button className="relative rounded-lg p-2 hover:bg-background-tertiary transition-colors">
            <Bell className="h-5 w-5 text-text-secondary" />
            <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-severity-critical" />
          </button>
        </div>
      </div>
    </header>
  )
}

