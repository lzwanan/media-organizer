import { defineConfig, presetWind, presetAttributify, presetTypography } from "unocss";

export default defineConfig({
  presets: [presetWind(), presetAttributify(), presetTypography()],
  shortcuts: {
    "page-container": "min-h-screen bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-100 transition-colors duration-300",
    "card-hover": "transition-all duration-300 hover:-translate-y-1 hover:shadow-xl",
    "glass": "bg-white/70 dark:bg-gray-900/70 backdrop-blur-xl border border-gray-200/60 dark:border-gray-700/40",
  },
  theme: {
    colors: {
      brand: {
        50: "#eef2ff",
        100: "#e0e7ff",
        200: "#c7d2fe",
        300: "#a5b4fc",
        400: "#818cf8",
        500: "#6366f1",
        600: "#4f46e5",
        700: "#4338ca",
        800: "#3730a3",
        900: "#312e81",
      },
    },
  },
});
