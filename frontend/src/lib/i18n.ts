/**
 * i18n - Internationalization Support
 * 
 * Simple, type-safe translation system
 * Default language: Turkish (tr)
 * Supported languages: Turkish (tr), English (en)
 */

export type Language = 'tr' | 'en'

export type TranslationKey = keyof typeof translations.tr

interface Translations {
  tr: Record<string, string>
  en: Record<string, string>
}

/**
 * Translation dictionary
 */
export const translations: Translations = {
  // Turkish (Default)
  tr: {
    // Brand
    'brand.name': 'AI Anabasis SEO Spider',
    'brand.tagline': 'Derin tarama. Akıllı düzeltme. Hızlı yayın.',
    
    // Navigation
    'nav.dashboard': 'Gösterge Paneli',
    'nav.projects': 'Projeler',
    'nav.scans': 'Taramalar',
    'nav.history': 'Geçmiş',
    'nav.settings': 'Ayarlar',
    'nav.monitoring': 'İzleme',
    
    // Dashboard
    'dashboard.title': 'Gösterge Paneli',
    'dashboard.subtitle': 'AI destekli web sitesi zekası bir bakışta',
    'dashboard.activeScans': 'Aktif Taramalar',
    'dashboard.totalFiles': 'Toplam Dosya',
    'dashboard.issuesFound': 'Bulunan Sorunlar',
    'dashboard.issuesFixed': 'Düzeltilen Sorunlar',
    'dashboard.recentScans': 'Son Taramalar',
    'dashboard.liveActivity': 'Canlı Aktivite Akışı',
    'dashboard.noActivity': 'Henüz aktivite yok',
    
    // Status
    'status.pending': 'Beklemede',
    'status.uploading': 'Yükleniyor',
    'status.chunking': 'Parçalanıyor',
    'status.analyzing': 'Analiz Ediliyor',
    'status.completed': 'Tamamlandı',
    'status.failed': 'Başarısız',
    'status.superseded': 'Geçersiz',
    'status.conflict': 'Çakışma',
    'status.approved': 'Onaylandı',
    'status.rejected': 'Reddedildi',
    'status.applied': 'Uygulandı',
    
    // Severity
    'severity.critical': 'Kritik',
    'severity.high': 'Yüksek',
    'severity.medium': 'Orta',
    'severity.low': 'Düşük',
    
    // Actions
    'action.approve': 'Onayla',
    'action.reject': 'Reddet',
    'action.edit': 'Düzenle',
    'action.apply': 'Uygula',
    'action.rollback': 'Geri Al',
    'action.search': 'Ara',
    'action.upload': 'Yükle',
    'action.download': 'İndir',
    'action.delete': 'Sil',
    'action.cancel': 'İptal',
    'action.save': 'Kaydet',
    'action.reset': 'Sıfırla',
    
    // Common
    'common.loading': 'Yükleniyor...',
    'common.error': 'Hata',
    'common.success': 'Başarılı',
    'common.warning': 'Uyarı',
    'common.info': 'Bilgi',
    'common.confirm': 'Onayla',
    'common.close': 'Kapat',
    'common.back': 'Geri',
    'common.next': 'İleri',
    'common.previous': 'Önceki',
    'common.total': 'Toplam',
    'common.progress': 'İlerleme',
    'common.confidence': 'Güven',
    'common.line': 'Satır',
    'common.file': 'Dosya',
    'common.files': 'Dosyalar',
    'common.code': 'Kod',
    'common.reason': 'Sebep',
    'common.noData': 'Veri yok',
    'common.created': 'Oluşturuldu',
    'common.action': 'İşlem',
    
    // File types
    'file.php': 'PHP Dosyası',
    'file.html': 'HTML Dosyası',
    'file.js': 'JavaScript Dosyası',
    'file.css': 'CSS Dosyası',
    'file.tsx': 'TypeScript React',
    
    // Projects
    'projects.subtitle': 'SEO analiz projelerinizi yönetin',
    'projects.totalProjects': 'Toplam Proje',
    'projects.activeScans': 'Aktif Tarama',
    'projects.completedScans': 'Tamamlanan Tarama',
    'projects.noProjects': 'Henüz proje yok',
    'projects.uploadFirst': 'Başlamak için bir dosya yükleyin',
    
    // Scans
    'scans.subtitle': 'Tarama detayları ve sorunlar',
    'scans.startAnalysis': 'Analizi Başlat',
    'scans.analyzing': 'Analiz Ediliyor...',
    'scans.issuesList': 'Sorun Listesi',
    'scans.approved': 'Onaylanan',
    
    // Monitoring
    'monitoring.subtitle': 'Sistem sağlığı ve performans metrikleri',
    'monitoring.rateLimiter': 'Hız Sınırlayıcı',
    'monitoring.utilization': 'Kullanım',
    'monitoring.activeRequests': 'Aktif İstek',
    'monitoring.queueSize': 'Kuyruk Boyutu',
    'monitoring.avgWaitTime': 'Ort. Bekleme',
    'monitoring.totalRequests': 'Toplam İstek',
    'monitoring.circuitBreakers': 'Devre Kesiciler',
    'monitoring.allHealthy': 'Tüm sistemler sağlıklı',
    'monitoring.failures': 'Başarısızlık',
    'monitoring.remainingAttempts': 'Kalan Deneme',
    'monitoring.tripped': 'Devrede',
    'monitoring.active': 'Aktif',
    'monitoring.memoryLimits': 'Bellek Limitleri',
    'monitoring.maxExtractedSize': 'Maks. Çıkarılmış Boyut',
    'monitoring.noActiveJobs': 'Aktif iş yok',
    
    // History
    'history.subtitle': 'Uygulanan yamalar ve değişiklik geçmişi',
    'history.successfulPatches': 'Başarılı Yama',
    'history.failedPatches': 'Başarısız Yama',
    'history.rolledBack': 'Geri Alındı',
    'history.patchHistory': 'Yama Geçmişi',
    'history.noHistory': 'Henüz geçmiş yok',
    'history.original': 'Orijinal',
    'history.patched': 'Yamalı',
    
    // Issue types
    'issue.schema_missing': 'Schema Eksik',
    'issue.meta_issue': 'Meta Sorunu',
    'issue.title_length': 'Başlık Uzunluğu',
    'issue.h_tag_issue': 'H Etiketi Sorunu',
    'issue.link_naturalness': 'Link Doğallığı',
    'issue.image_alt_missing': 'Görsel Alt Eksik',
    'issue.performance_hint': 'Performans Önerisi',
    'issue.js_error': 'JavaScript Hatası',
    'issue.css_suggestion': 'CSS Önerisi',
    
    // Messages
    'message.noData': 'Veri bulunamadı',
    'message.noIssues': 'Sorun bulunamadı',
    'message.analysisStarted': 'Analiz başlatıldı',
    'message.patchApplied': 'Yama uygulandı',
    'message.circuitBreakerTripped': 'Devre kesici devreye girdi',
    'message.uploadSuccess': 'Yükleme başarılı',
    'message.uploadFailed': 'Yükleme başarısız',
    
    // Settings
    'settings.title': 'Ayarlar',
    'settings.language': 'Dil',
    'settings.theme': 'Tema',
    'settings.notifications': 'Bildirimler',
    'settings.apiKey': 'API Anahtarı',
    'settings.general': 'Genel',
    'settings.advanced': 'Gelişmiş',
  },
  
  // English
  en: {
    // Brand
    'brand.name': 'AI Anabasis SEO Spider',
    'brand.tagline': 'Deep crawl. Smart fix. Ship faster.',
    
    // Navigation
    'nav.dashboard': 'Dashboard',
    'nav.projects': 'Projects',
    'nav.scans': 'Scans',
    'nav.history': 'History',
    'nav.settings': 'Settings',
    'nav.monitoring': 'Monitoring',
    
    // Dashboard
    'dashboard.title': 'Dashboard',
    'dashboard.subtitle': 'AI-powered website intelligence at a glance',
    'dashboard.activeScans': 'Active Scans',
    'dashboard.totalFiles': 'Total Files',
    'dashboard.issuesFound': 'Issues Found',
    'dashboard.issuesFixed': 'Issues Fixed',
    'dashboard.recentScans': 'Recent Scans',
    'dashboard.liveActivity': 'Live Activity Feed',
    'dashboard.noActivity': 'No activity yet',
    
    // Status
    'status.pending': 'Pending',
    'status.uploading': 'Uploading',
    'status.chunking': 'Chunking',
    'status.analyzing': 'Analyzing',
    'status.completed': 'Completed',
    'status.failed': 'Failed',
    'status.superseded': 'Superseded',
    'status.conflict': 'Conflict',
    'status.approved': 'Approved',
    'status.rejected': 'Rejected',
    'status.applied': 'Applied',
    
    // Severity
    'severity.critical': 'Critical',
    'severity.high': 'High',
    'severity.medium': 'Medium',
    'severity.low': 'Low',
    
    // Actions
    'action.approve': 'Approve',
    'action.reject': 'Reject',
    'action.edit': 'Edit',
    'action.apply': 'Apply',
    'action.rollback': 'Rollback',
    'action.search': 'Search',
    'action.upload': 'Upload',
    'action.download': 'Download',
    'action.delete': 'Delete',
    'action.cancel': 'Cancel',
    'action.save': 'Save',
    'action.reset': 'Reset',
    
    // Common
    'common.loading': 'Loading...',
    'common.error': 'Error',
    'common.success': 'Success',
    'common.warning': 'Warning',
    'common.info': 'Info',
    'common.confirm': 'Confirm',
    'common.close': 'Close',
    'common.back': 'Back',
    'common.next': 'Next',
    'common.previous': 'Previous',
    'common.total': 'Total',
    'common.progress': 'Progress',
    'common.confidence': 'Confidence',
    'common.line': 'Line',
    'common.file': 'File',
    'common.files': 'Files',
    'common.code': 'Code',
    'common.reason': 'Reason',
    'common.noData': 'No data',
    'common.created': 'Created',
    'common.action': 'Action',
    
    // File types
    'file.php': 'PHP File',
    'file.html': 'HTML File',
    'file.js': 'JavaScript File',
    'file.css': 'CSS File',
    'file.tsx': 'TypeScript React',
    
    // Projects
    'projects.subtitle': 'Manage your SEO analysis projects',
    'projects.totalProjects': 'Total Projects',
    'projects.activeScans': 'Active Scans',
    'projects.completedScans': 'Completed Scans',
    'projects.noProjects': 'No projects yet',
    'projects.uploadFirst': 'Upload a file to get started',
    
    // Scans
    'scans.subtitle': 'Scan details and issues',
    'scans.startAnalysis': 'Start Analysis',
    'scans.analyzing': 'Analyzing...',
    'scans.issuesList': 'Issues List',
    'scans.approved': 'Approved',
    
    // Monitoring
    'monitoring.subtitle': 'System health and performance metrics',
    'monitoring.rateLimiter': 'Rate Limiter',
    'monitoring.utilization': 'Utilization',
    'monitoring.activeRequests': 'Active Requests',
    'monitoring.queueSize': 'Queue Size',
    'monitoring.avgWaitTime': 'Avg. Wait Time',
    'monitoring.totalRequests': 'Total Requests',
    'monitoring.circuitBreakers': 'Circuit Breakers',
    'monitoring.allHealthy': 'All systems healthy',
    'monitoring.failures': 'Failures',
    'monitoring.remainingAttempts': 'Remaining Attempts',
    'monitoring.tripped': 'Tripped',
    'monitoring.active': 'Active',
    'monitoring.memoryLimits': 'Memory Limits',
    'monitoring.maxExtractedSize': 'Max Extracted Size',
    'monitoring.noActiveJobs': 'No active jobs',
    
    // History
    'history.subtitle': 'Applied patches and change history',
    'history.successfulPatches': 'Successful Patches',
    'history.failedPatches': 'Failed Patches',
    'history.rolledBack': 'Rolled Back',
    'history.patchHistory': 'Patch History',
    'history.noHistory': 'No history yet',
    'history.original': 'Original',
    'history.patched': 'Patched',
    
    // Issue types
    'issue.schema_missing': 'Schema Missing',
    'issue.meta_issue': 'Meta Issue',
    'issue.title_length': 'Title Length',
    'issue.h_tag_issue': 'H Tag Issue',
    'issue.link_naturalness': 'Link Naturalness',
    'issue.image_alt_missing': 'Image Alt Missing',
    'issue.performance_hint': 'Performance Hint',
    'issue.js_error': 'JavaScript Error',
    'issue.css_suggestion': 'CSS Suggestion',
    
    // Messages
    'message.noData': 'No data found',
    'message.noIssues': 'No issues found',
    'message.analysisStarted': 'Analysis started',
    'message.patchApplied': 'Patch applied',
    'message.circuitBreakerTripped': 'Circuit breaker tripped',
    'message.uploadSuccess': 'Upload successful',
    'message.uploadFailed': 'Upload failed',
    
    // Settings
    'settings.title': 'Settings',
    'settings.language': 'Language',
    'settings.theme': 'Theme',
    'settings.notifications': 'Notifications',
    'settings.apiKey': 'API Key',
    'settings.general': 'General',
    'settings.advanced': 'Advanced',
  },
}

/**
 * i18n Class - Translation manager
 */
class I18n {
  private currentLanguage: Language = 'tr' // Default: Turkish
  
  constructor() {
    // Load saved language from localStorage
    const savedLang = localStorage.getItem('language') as Language
    if (savedLang && (savedLang === 'tr' || savedLang === 'en')) {
      this.currentLanguage = savedLang
    }
  }
  
  /**
   * Get current language
   */
  getLanguage(): Language {
    return this.currentLanguage
  }
  
  /**
   * Set language
   */
  setLanguage(lang: Language): void {
    this.currentLanguage = lang
    localStorage.setItem('language', lang)
    
    // Trigger custom event for components to re-render
    window.dispatchEvent(new CustomEvent('languageChange', { detail: lang }))
  }
  
  /**
   * Translate key
   */
  t(key: TranslationKey): string {
    return translations[this.currentLanguage][key] || key
  }
  
  /**
   * Get all translations for current language
   */
  getTranslations(): Record<string, string> {
    return translations[this.currentLanguage]
  }
}

// Export singleton instance
export const i18n = new I18n()

/**
 * React hook for translations
 */
export function useTranslation() {
  const [language, setLanguageState] = React.useState<Language>(i18n.getLanguage())
  
  React.useEffect(() => {
    const handleLanguageChange = (e: CustomEvent<Language>) => {
      setLanguageState(e.detail)
    }
    
    window.addEventListener('languageChange', handleLanguageChange as EventListener)
    
    return () => {
      window.removeEventListener('languageChange', handleLanguageChange as EventListener)
    }
  }, [])
  
  const t = (key: TranslationKey): string => {
    return i18n.t(key)
  }
  
  const setLanguage = (lang: Language): void => {
    i18n.setLanguage(lang)
  }
  
  return { t, language, setLanguage }
}

// Import React for hook
import React from 'react'

