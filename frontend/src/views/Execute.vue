<template>
  <div class="max-w-2xl mx-auto px-6 py-12">
    <router-link to="/scan"
      class="inline-flex items-center gap-1 text-sm text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 mb-6 transition-colors">
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
      </svg>
      {{ $t('execute.backToPreview') }}
    </router-link>

    <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">{{ $t('execute.title') }}</h1>
    <p class="text-sm text-gray-400 dark:text-gray-500 mb-8">{{ $t('execute.subtitle') }}</p>

    <SectionCard>
      <div class="space-y-3">
        <div v-for="item in items" :key="item.path"
          class="flex items-center gap-3 py-1.5">
          <span v-if="item.status === 'preview'" class="w-5 h-5 rounded-full bg-indigo-100 dark:bg-indigo-500/20 flex items-center justify-center shrink-0">
            <svg class="w-3 h-3 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </span>
          <span v-else-if="item.status === 'skipped'" class="w-5 h-5 rounded-full bg-amber-100 dark:bg-amber-500/20 flex items-center justify-center shrink-0 text-xs text-amber-600">!</span>
          <span v-else-if="item.status === 'failed'" class="w-5 h-5 rounded-full bg-red-100 dark:bg-red-500/20 flex items-center justify-center shrink-0 text-xs text-red-600">✕</span>

          <div class="flex-1 min-w-0">
            <div class="text-xs text-gray-400 truncate font-mono">{{ item.path }}</div>
            <div class="text-sm text-gray-700 dark:text-gray-300 truncate">→ {{ item.target }}</div>
          </div>
          <span v-if="item.error" class="text-[11px] text-red-500 shrink-0">{{ item.error }}</span>
        </div>
      </div>
    </SectionCard>

    <div class="mt-8 text-center">
      <button
        @click="confirmExecute"
        :disabled="executing"
        class="px-6 py-3 rounded-xl bg-indigo-500 hover:bg-indigo-600 text-white text-sm font-semibold transition-colors disabled:opacity-40"
      >
        {{ executing ? $t('execute.executing') : $t('execute.confirmBtn') }}
      </button>
      <p class="mt-3 text-xs text-red-400 dark:text-red-500">{{ $t('execute.warning') }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { useToast } from "primevue/usetoast";
import { useScanStore } from "@/stores/scan";
import { fetchExecute } from "@/api/client";
import SectionCard from "@/components/SectionCard.vue";

const router = useRouter();
const { t } = useI18n();
const toast = useToast();
const scanStore = useScanStore();
const executing = ref(false);
const items = computed(() => (scanStore as any).execResult?.items ?? []);

async function confirmExecute() {
  if (!scanStore.result) return;
  executing.value = true;
  const execItems = scanStore.result.items
    .filter(n => n.type === "file" && n.recognized?.target_name)
    .map(n => ({ path: n.path, target_dir: n.recognized!.target_dir || "", target_name: n.recognized!.target_name || "" }));
  try {
    const result = await fetchExecute(execItems, scanStore.result.root_path, false);
    toast.add({ severity: "success", summary: t('common.done'), detail: `${result.success} ${t('execute.renamed')}, ${result.failed} ${t('execute.failed')}`, life: 5000 });
    router.push(`/report/${result.task_id}`);
  } catch (e: any) {
    toast.add({ severity: "error", summary: t('common.error'), detail: e.message || t('toast.execFailed'), life: 5000 });
  } finally {
    executing.value = false;
  }
}
</script>
