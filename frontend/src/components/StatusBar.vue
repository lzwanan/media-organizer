<template>
  <footer class="border-t border-gray-200/60 dark:border-gray-800/60 bg-white/80 dark:bg-gray-950/80 backdrop-blur-xl">
    <div class="max-w-6xl mx-auto px-6 h-9 flex items-center gap-3 text-xs">
      <span class="flex items-center gap-1.5" :class="appStore.isOnline ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-500'">
        <span class="w-1.5 h-1.5 rounded-full" :class="appStore.isOnline ? 'bg-emerald-500' : 'bg-red-500'" />
        {{ appStore.isOnline ? $t('status.connected') : $t('status.disconnected') }}
      </span>
      <span class="text-gray-300 dark:text-gray-700">·</span>
      <span class="text-gray-400 dark:text-gray-600">v{{ appStore.backendVersion || '—' }}</span>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { useAppStore } from "@/stores/app";
const appStore = useAppStore();
</script>
