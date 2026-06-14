<template>
  <div class="max-w-3xl mx-auto px-6 py-12">
    <template v-if="!scanStore.result">
      <div class="text-center py-20 text-gray-400 dark:text-gray-600">
        <p class="text-lg">No scan data. Go back and scan a directory.</p>
        <router-link to="/" class="mt-4 inline-block text-indigo-500 hover:text-indigo-600 text-sm font-medium">
          ← Back to Home
        </router-link>
      </div>
    </template>

    <template v-else>
      <!-- Header -->
      <header class="mb-8">
        <router-link to="/"
          class="inline-flex items-center gap-1 text-sm text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 mb-4 transition-colors">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          {{ $t("nav.home") }}
        </router-link>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-1">
          {{ scanStore.result.root_path }}
        </h1>
        <p class="text-sm text-gray-400 dark:text-gray-500 mb-4">
          {{ scanStore.result.total_count }} files · {{ scanStore.dirs.length }} folders
          <span v-if="junkCount" class="text-red-500"> · {{ junkCount }} junk</span>
          <span v-if="emptyCount" class="text-gray-400"> · {{ emptyCount }} empty dirs</span>
          {{ scanStore.result.root_type ? '· ' + scanStore.result.root_type : '' }}
        </p>

        <!-- Filter tabs -->
        <div class="flex items-center justify-between mb-6 flex-wrap gap-3">
          <div class="flex gap-2 flex-wrap">
            <button v-for="f in filters" :key="f.key"
              @click="activeFilter = f.key"
              class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors"
              :class="activeFilter === f.key
                ? 'bg-indigo-500 text-white'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'"
            >
              {{ f.label }}
              <span class="ml-1 opacity-70">{{ f.count }}</span>
            </button>
          </div>
          <div class="flex items-center gap-2 text-xs">
            <span class="text-gray-400">命名:</span>
            <button v-for="s in namingStyles" :key="s.key" @click="namingStyle = s.key"
              class="px-2.5 py-1 rounded-lg font-medium transition-colors"
              :class="namingStyle === s.key
                ? 'bg-indigo-100 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400'
                : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'"
            >{{ s.label }}</button>
          </div>
        </div>
      </header>

      <!-- File Tree -->
      <SectionCard>
        <div class="space-y-0.5">
          <TreeNode
            v-for="node in rootChildren"
            :key="node.path"
            :node="node"
            :tree="scanStore.tree"
            :selected-paths="selectedPaths"
            @toggle-select="toggleSelect"
          />
        </div>

        <!-- Empty state -->
        <div v-if="scanStore.result.items.length === 0"
          class="py-12 text-center text-gray-400 dark:text-gray-600 text-sm">
          No files or folders found in this directory.
        </div>
      </SectionCard>

      <!-- Bottom bar -->
      <div class="mt-8 flex justify-between items-center">
        <div class="flex items-center gap-4 text-sm text-gray-400">
          <span>{{ scanStore.files.length }} files</span>
          <span v-if="selectedCount > 0" class="text-indigo-500 font-semibold">
            {{ selectedCount }} selected
          </span>
        </div>
        <div class="flex gap-3">
          <button v-if="selectedCount > 0"
            @click="deleteSelected"
            class="px-5 py-2.5 rounded-xl bg-red-500 hover:bg-red-600 text-white text-sm font-semibold
                   transition-colors active:scale-[0.98]"
          >
            Delete ({{ selectedCount }})
          </button>
          <button
            class="px-5 py-2.5 rounded-xl bg-indigo-500 hover:bg-indigo-600 text-white text-sm font-semibold
                   transition-colors active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed"
            disabled
          >
            Continue
          </button>
        </div>
      </div>

      <!-- Confirm dialog -->
      <Dialog v-model:visible="showConfirm" header="Confirm Delete" :modal="true" :style="{ width: '400px' }">
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Delete {{ selectedCount }} selected items? This action cannot be undone.
        </p>
        <template #footer>
          <button @click="showConfirm = false"
            class="px-4 py-2 rounded-lg text-sm text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800">Cancel</button>
          <button @click="confirmDelete"
            class="px-4 py-2 rounded-lg text-sm bg-red-500 hover:bg-red-600 text-white font-semibold">Delete</button>
        </template>
      </Dialog>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, reactive, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { useToast } from "primevue/usetoast";
import Dialog from "primevue/dialog";
import { useScanStore } from "@/stores/scan";
import { fetchRenamePreview, type FileNodeResponse } from "@/api/client";
import SectionCard from "@/components/SectionCard.vue";
import TreeNode from "@/components/TreeNode.vue";

const router = useRouter();
const { t } = useI18n();
const toast = useToast();
const scanStore = useScanStore();
const activeFilter = ref("all");
const namingStyle = ref("en");
const selectedPaths = reactive<Set<string>>(new Set());
const showConfirm = ref(false);

const namingStyles = [
  { key: "zh", label: "中" },
  { key: "en", label: "EN" },
  { key: "bilingual", label: "中+EN" },
  { key: "en_first", label: "EN+中" },
];

onMounted(() => {
  if (!scanStore.result) {
    router.replace("/");
  }
});

const allItems = computed(() => scanStore.result?.items ?? []);

const movieCount = computed(() => allItems.value.filter(n => n.recognized?.media_type === "movie").length);
const tvCount = computed(() => allItems.value.filter(n => n.recognized?.media_type === "tv").length);

const filters = computed(() => [
  { key: "all", label: t("scan.filters.all"), count: allItems.value.length },
  { key: "movie", label: t("scan.filters.movie"), count: movieCount.value },
  { key: "tv", label: t("scan.filters.tv"), count: tvCount.value },
]);

/** Root-level children filtered */
const rootChildren = computed(() => {
  if (!scanStore.result) return [];
  const root = scanStore.result.root_path;
  const tree = scanStore.tree;
  const all = tree[root] ?? [];

  if (activeFilter.value === "all") return all;
  if (activeFilter.value === "movie") return all.filter(n => n.recognized?.media_type === "movie");
  if (activeFilter.value === "tv") return all.filter(n => n.recognized?.media_type === "tv");
  return all;
});

const selectedCount = computed(() => selectedPaths.size);

function toggleSelect(path: string) {
  if (selectedPaths.has(path)) {
    selectedPaths.delete(path);
  } else {
    selectedPaths.add(path);
  }
}

function deleteSelected() {
  showConfirm.value = true;
}

function confirmDelete() {
  showConfirm.value = false;
  const count = selectedPaths.size;
  // Remove selected nodes from store
  if (scanStore.result) {
    scanStore.result.items = scanStore.result.items.filter(i => !selectedPaths.has(i.path));
  }
  selectedPaths.clear();
  toast.add({ severity: "success", summary: "Deleted", detail: `${count} items removed from list.`, life: 3000 });
}

/** 命名风格切换 → 调 API 刷新目标名 */
watch(namingStyle, async (style) => {
  if (!scanStore.result) return;
  const items = scanStore.result.items
    .filter(n => n.recognized)
    .map(n => ({
      path: n.path,
      original_name: n.name,
      title: n.recognized!.title,
      year: n.recognized!.year,
      season: n.recognized!.season,
      episode: n.recognized!.episode,
      quality: n.recognized!.quality,
      edition: n.recognized!.edition,
      media_type: n.recognized!.media_type,
      extension: n.extension,
    }));
  if (items.length === 0) return;
  try {
    const res = await fetchRenamePreview(items, style);
    const map = new Map(res.items.map(i => [i.path, i]));
    for (const node of scanStore.result.items) {
      const updated = map.get(node.path);
      if (updated && node.recognized) {
        node.recognized.target_name = updated.target_name;
        node.recognized.target_dir = updated.target_dir;
        node.recognized.target_path = updated.target_path;
      }
    }
  } catch {
    toast.add({ severity: "error", summary: "Error", detail: "Failed to update names", life: 3000 });
  }
});
</script>
