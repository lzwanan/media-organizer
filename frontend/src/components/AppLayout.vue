<template>
  <div class="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-950 transition-colors">
    <!-- Navbar -->
    <header class="sticky top-0 z-50 border-b border-gray-200/60 dark:border-gray-800/60 bg-white/80 dark:bg-gray-950/80 backdrop-blur-xl">
      <div class="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
        <!-- Brand -->
        <router-link to="/" class="flex items-center gap-2.5 text-gray-900 dark:text-white no-underline">
          <svg class="w-7 h-7 text-indigo-500" viewBox="0 0 64 64" fill="currentColor">
            <path d="M18 16h16l6 8-6 8H18l-6-8 6-8z" opacity="0.9"/>
            <path d="M36 16h14l4 8-4 8H36l-4-8 4-8z" opacity="0.55"/>
            <rect x="20" y="38" width="24" height="4" rx="2" opacity="0.4"/>
          </svg>
          <span class="text-[15px] font-semibold tracking-tight">Media Organizer</span>
        </router-link>

        <!-- Nav links -->
        <nav class="flex items-center gap-0.5">
          <NavItem to="/">{{ $t("nav.home") }}</NavItem>
          <NavItem to="/history">{{ $t("nav.history") }}</NavItem>
          <NavItem to="/settings">{{ $t("nav.settings") }}</NavItem>

          <div class="w-px h-5 bg-gray-200 dark:bg-gray-800 mx-2" />

          <!-- Language toggle -->
          <button
            @click="toggleLocale"
            class="px-2 py-1 rounded-lg text-[12px] font-semibold text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors tracking-wide"
          >
            {{ currentLocale === 'zh-CN' ? 'EN' : '中' }}
          </button>

          <!-- Theme toggle -->
          <button
            @click="appStore.toggleDarkMode()"
            class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            aria-label="Toggle theme"
          >
            <svg v-if="appStore.darkMode" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
            </svg>
            <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
            </svg>
          </button>
        </nav>
      </div>
    </header>

    <!-- Main content — fills remaining space -->
    <main class="flex-1">
      <slot />
    </main>

    <!-- Status bar -->
    <StatusBar />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useI18n } from "vue-i18n";
import NavItem from "./NavItem.vue";
import StatusBar from "./StatusBar.vue";
import { useAppStore } from "@/stores/app";
import { fetchStatus } from "@/api/client";
import { saveLocale } from "@/i18n";

const { locale } = useI18n();
const appStore = useAppStore();

const currentLocale = locale;

function toggleLocale() {
  const next = locale.value === "zh-CN" ? "en-US" : "zh-CN";
  locale.value = next;
  saveLocale(next);
}

onMounted(async () => {
  appStore.init();
  try {
    const res = await fetchStatus();
    appStore.setBackendStatus("online", res.version);
  } catch {
    appStore.setBackendStatus("offline");
  }
});
</script>
