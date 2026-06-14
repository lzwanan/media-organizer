import { createI18n } from "vue-i18n";
import zhCN from "./zh-CN";
import enUS from "./en-US";

const STORAGE_KEY = "media-organizer-locale";

function getSavedLocale(): string {
  return localStorage.getItem(STORAGE_KEY) || "zh-CN";
}

function saveLocale(locale: string) {
  localStorage.setItem(STORAGE_KEY, locale);
}

const i18n = createI18n({
  legacy: false,
  locale: getSavedLocale(),
  fallbackLocale: "zh-CN",
  messages: {
    "zh-CN": zhCN,
    "en-US": enUS,
  },
});

export { saveLocale };
export default i18n;
