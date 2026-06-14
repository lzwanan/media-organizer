<template>
  <div class="max-w-2xl mx-auto px-6 py-16 text-center">
    <div class="w-16 h-16 mx-auto mb-6 rounded-2xl bg-emerald-100 dark:bg-emerald-500/20 flex items-center justify-center">
      <svg class="w-8 h-8 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    </div>
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">{{ $t('report.title') }}</h1>
    <p class="text-gray-400 dark:text-gray-500 mb-8">{{ $t('report.subtitle') }}</p>

    <SectionCard>
      <div class="grid grid-cols-3 gap-6 text-center">
        <div>
          <div class="text-2xl font-bold text-emerald-500">{{ success }}</div>
          <div class="text-xs text-gray-400 mt-1">{{ $t('report.renamed') }}</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-red-500">{{ failed }}</div>
          <div class="text-xs text-gray-400 mt-1">{{ $t('report.failed') }}</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-amber-500">{{ skipped }}</div>
          <div class="text-xs text-gray-400 mt-1">{{ $t('report.skipped') }}</div>
        </div>
      </div>
    </SectionCard>

    <div class="mt-8 flex gap-3 justify-center">
      <router-link to="/" class="px-6 py-2.5 rounded-xl bg-indigo-500 hover:bg-indigo-600 text-white text-sm font-semibold transition-colors no-underline">
        {{ $t('report.backHome') }}
      </router-link>
      <router-link to="/history" class="px-6 py-2.5 rounded-xl bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 text-sm font-semibold hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors no-underline">
        {{ $t('report.viewHistory') }}
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useScanStore } from "@/stores/scan";
import SectionCard from "@/components/SectionCard.vue";

const scanStore = useScanStore();
const execResult = (scanStore as any).execResult;
const success = execResult?.success ?? 0;
const failed = execResult?.failed ?? 0;
const skipped = execResult?.skipped ?? 0;
</script>
