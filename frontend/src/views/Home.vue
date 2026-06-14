<template>
  <div class="max-w-2xl mx-auto px-6 py-16">
    <!-- Hero -->
    <header class="mb-12">
      <h1 class="text-[32px] font-bold tracking-tight text-gray-900 dark:text-white mb-3">
        {{ $t("home.title") }}
      </h1>
      <p class="text-[15px] text-gray-500 dark:text-gray-400 leading-relaxed max-w-lg">
        {{ $t("home.subtitle") }}
      </p>
    </header>

    <!-- Card -->
    <SectionCard>
      <div class="space-y-8">
        <!-- Folder input -->
        <FolderInput
          v-model="targetDir"
          :placeholder="$t('home.targetDirPlaceholder')"
          :recent-paths="recentPaths"
          @save-recent="saveRecentPath"
        >
          <template #label>{{ $t("home.targetDir") }}</template>
          <template #hint>
            <span v-if="recentPaths.length">
              Recent:&nbsp;
              <button
                v-for="p in recentPaths"
                :key="p"
                @click="targetDir = p"
                class="text-indigo-500 hover:text-indigo-600 dark:text-indigo-400 dark:hover:text-indigo-300 transition-colors"
              >{{ p }}</button>
            </span>
          </template>
        </FolderInput>

        <!-- Strategy -->
        <StrategyPicker
          v-model="strategy"
          :options="strategies"
        >
          <template #label>{{ $t("home.strategy") }}</template>
        </StrategyPicker>

        <!-- CTA -->
        <Button
          :label="scanning ? $t('toast.scanning') : (targetDir.trim() ? $t('home.startScan') : $t('home.startScanDisabled'))"
          :disabled="!targetDir.trim() || scanning"
          :loading="scanning"
          severity="primary"
          class="w-full !h-12 !text-[15px] !font-semibold !rounded-xl"
          @click="startScan"
        />
      </div>
    </SectionCard>

    <!-- Features -->
    <div class="mt-10 grid grid-cols-3 gap-6 text-center">
      <div v-for="f in features" :key="f.title">
        <div class="w-9 h-9 mx-auto mb-3 rounded-xl flex items-center justify-center"
          :class="f.bg"
        >
          <svg class="w-4 h-4" :class="f.color" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" :d="f.icon" />
          </svg>
        </div>
        <div class="text-[13px] font-semibold text-gray-700 dark:text-gray-300 mb-1">
          {{ f.title }}
        </div>
        <div class="text-[12px] text-gray-400 dark:text-gray-500 leading-relaxed">
          {{ f.desc }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { useToast } from "primevue/usetoast";
import Button from "primevue/button";
import SectionCard from "@/components/SectionCard.vue";
import FolderInput from "@/components/FolderInput.vue";
import StrategyPicker from "@/components/StrategyPicker.vue";
import { fetchScan } from "@/api/client";
import { useScanStore } from "@/stores/scan";

const router = useRouter();
const { t } = useI18n();
const toast = useToast();
const scanStore = useScanStore();
const targetDir = ref("");
const strategy = ref("smart");
const scanning = ref(false);
const recentPaths = ref<string[]>([]);

const strategies = computed(() => [
  { value: "smart", icon: "🧠", label: t("home.strategies.smart.label"), desc: t("home.strategies.smart.desc") },
  { value: "inplace", icon: "📂", label: t("home.strategies.inplace.label"), desc: t("home.strategies.inplace.desc") },
  { value: "rename-only", icon: "✏️", label: t("home.strategies.renameOnly.label"), desc: t("home.strategies.renameOnly.desc") },
]);

const features = computed(() => [
  {
    title: t("home.features.detect.title"), desc: t("home.features.detect.desc"),
    icon: "M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z",
    bg: "bg-indigo-50 dark:bg-indigo-500/10", color: "text-indigo-600 dark:text-indigo-400",
  },
  {
    title: t("home.features.preview.title"), desc: t("home.features.preview.desc"),
    icon: "M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z M15 12a3 3 0 11-6 0 3 3 0 016 0z",
    bg: "bg-emerald-50 dark:bg-emerald-500/10", color: "text-emerald-600 dark:text-emerald-400",
  },
  {
    title: t("home.features.rollback.title"), desc: t("home.features.rollback.desc"),
    icon: "M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z",
    bg: "bg-amber-50 dark:bg-amber-500/10", color: "text-amber-600 dark:text-amber-400",
  },
]);

function saveRecentPath(p: string) {
  if (!recentPaths.value.includes(p)) {
    recentPaths.value.unshift(p);
    if (recentPaths.value.length > 5) recentPaths.value.pop();
  }
}

async function startScan() {
  const dir = targetDir.value.trim();
  if (!dir) return;

  scanning.value = true;
  try {
    const result = await fetchScan(dir);
    scanStore.setResult(result);
    router.push("/scan");
  } catch (e: any) {
    const msg = e.response?.data?.detail || e.message || t('toast.scanFailed');
    toast.add({ severity: "error", summary: t('common.error'), detail: msg, life: 5000 });
  } finally {
    scanning.value = false;
  }
}
</script>
