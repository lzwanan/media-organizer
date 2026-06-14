<template>
  <div :class="['app-shell', { 'app-dark': appStore.darkMode }]">
    <!-- Toast container -->
    <Toast position="top-right" />

    <!-- Navbar -->
    <nav class="glass sticky top-0 z-50 px-6 py-3 flex items-center justify-between">
      <router-link to="/" class="flex items-center gap-3 text-gray-900 dark:text-gray-100 no-underline">
        <div class="w-9 h-9 rounded-xl bg-brand-500 flex items-center justify-center text-white font-bold text-lg">
          M
        </div>
        <span class="text-lg font-semibold tracking-tight">Media Organizer</span>
      </router-link>

      <div class="flex items-center gap-1">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200
                 text-gray-600 dark:text-gray-400
                 hover:bg-gray-100 dark:hover:bg-gray-800
                 hover:text-gray-900 dark:hover:text-gray-100"
          active-class="!bg-brand-50 !text-brand-700 dark:!bg-brand-950 dark:!text-brand-400"
        >
          <span class="mr-1">{{ item.icon }}</span>
          {{ item.label }}
        </router-link>

        <!-- Dark mode toggle -->
        <button
          class="ml-2 w-8 h-8 rounded-lg flex items-center justify-center transition-colors
                 hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500"
          @click="appStore.toggleDarkMode()"
        >
          <span class="text-lg">{{ appStore.darkMode ? '🌙' : '☀️' }}</span>
        </button>
      </div>
    </nav>

    <!-- Page content -->
    <main class="px-6 py-8 max-w-7xl mx-auto">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Status bar -->
    <footer class="fixed bottom-0 left-0 right-0 px-6 py-2 text-xs flex items-center gap-3 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-t border-gray-200/50 dark:border-gray-700/50">
      <span
        class="inline-flex items-center gap-1.5"
        :class="appStore.isOnline ? 'text-green-600' : 'text-red-500'"
      >
        <span class="w-2 h-2 rounded-full inline-block" :class="appStore.isOnline ? 'bg-green-500 animate-pulse' : 'bg-red-500'" />
        {{ appStore.isOnline ? '服务在线' : '服务离线' }}
      </span>
      <span class="text-gray-400" v-if="appStore.backendVersion">v{{ appStore.backendVersion }}</span>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import Toast from "primevue/toast";
import { useAppStore } from "@/stores/app";
import { fetchStatus } from "@/api/client";

const appStore = useAppStore();

const navItems = [
  { path: "/", label: "首页", icon: "🏠" },
  { path: "/history", label: "历史", icon: "📋" },
  { path: "/settings", label: "设置", icon: "⚙️" },
];

onMounted(async () => {
  try {
    const res = await fetchStatus();
    appStore.setBackendStatus("online", res.version);
  } catch {
    appStore.setBackendStatus("offline");
  }
});
</script>
