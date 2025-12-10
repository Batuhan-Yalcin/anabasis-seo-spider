import { Globe } from 'lucide-react'
import { useTranslation, type Language } from '@/lib/i18n'
import { cn } from '@/lib/utils'

export function LanguageSwitcher() {
  const { language, setLanguage } = useTranslation()

  const languages: { code: Language; label: string; flag: string }[] = [
    { code: 'tr', label: 'Türkçe', flag: '🇹🇷' },
    { code: 'en', label: 'English', flag: '🇬🇧' },
  ]

  return (
    <div className="relative group">
      <button className="flex items-center space-x-2 rounded-lg p-2 hover:bg-background-tertiary transition-colors">
        <Globe className="h-5 w-5 text-text-secondary" />
        <span className="text-sm text-text-secondary">
          {languages.find((l) => l.code === language)?.flag}
        </span>
      </button>

      {/* Dropdown */}
      <div className="absolute right-0 top-full mt-2 w-40 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
        <div className="glass-card p-2 space-y-1">
          {languages.map((lang) => (
            <button
              key={lang.code}
              onClick={() => setLanguage(lang.code)}
              className={cn(
                'w-full flex items-center space-x-2 rounded-lg px-3 py-2 text-sm transition-colors',
                language === lang.code
                  ? 'bg-accent-primary/10 text-accent-primary'
                  : 'text-text-secondary hover:bg-background-tertiary hover:text-text-primary'
              )}
            >
              <span>{lang.flag}</span>
              <span>{lang.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

