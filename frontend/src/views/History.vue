<template>
  <div class="max-w-2xl mx-auto px-6 py-12">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-8">{{ $t("nav.history") }}</h1>

    <div v-if="items.length === 0 && !loading" class="py-20 text-center text-gray-400 dark:text-gray-600">
      {{ $t('history.empty') }}
    </div>

    <SectionCard v-else>
      <div class="space-y-1">
        <div v-for="h in items" :key="h.id"
          class="flex items-center gap-4 px-3 py-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
          <div class="flex-1 min-w-0">
            <div class="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">{{ h.root_path }}</div>
            <div class="text-xs text-gray-400 mt-0.5">{{ h.timestamp }}</div>
          </div>
          <div class="flex items-center gap-3 text-xs shrink-0">
            <span class="text-emerald-600 dark:text-emerald-400">{{ h.success_count }} ✓</span>
            <span v-if="h.failed_count" class="text-red-500">{{ h.failed_count }} ✕</span>
            <span v-if="h.skipped_count" class="text-amber-500">{{ h.skipped_count }} ⊘</span>
          </div>
        </div>
      </div>
    </SectionCard>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import api from "@/api/client";
import SectionCard from "@/components/SectionCard.vue";

const items = ref<any[]>([]);
const loading = ref(true);

onMounted(async () => {
  try {
    const { data } = await api.get("/history");
    items.value = data.items || [];
  } finally {
    loading.value = false;
  }
});
</script>
