import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translation files
import enTranslations from '../public/locales/en/common.json';
import hiTranslations from '../public/locales/hi/common.json';
import taTranslations from '../public/locales/ta/common.json';
import teTranslations from '../public/locales/te/common.json';

const resources = {
  en: {
    common: enTranslations,
  },
  hi: {
    common: hiTranslations,
  },
  ta: {
    common: taTranslations,
  },
  te: {
    common: teTranslations,
  },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    lng: localStorage.getItem('language') || 'en', // Default language
    fallbackLng: 'en', // Fallback language
    debug: process.env.NODE_ENV === 'development',

    ns: ['common'], // Default namespace
    defaultNS: 'common',

    interpolation: {
      escapeValue: false, // React already escapes values
    },

    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      lookupLocalStorage: 'language',
    },

    react: {
      useSuspense: false,
    },
  });

export default i18n;