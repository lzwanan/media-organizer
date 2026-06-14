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
        <div class="flex gap-2 mb-6 flex-wrap">
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
      </header>

      <!-- File Tree -->
      <SectionCard>
        <div class="space-y-0.5">
          <!-- Root files -->
          <TreeNode
            v-for="node in rootChildren"
            :key="node.path"
            :node="node"
            :tree="scanStore.tree"
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
          <span>·</span>
          <span class="text-emerald-600 dark:text-emerald-400">{{ scanStore.recognizedCount }} recognized</span>
          <span v-if="scanStore.files.length !== scanStore.recognizedCount" class="text-amber-500">
            {{ scanStore.files.length - scanStore.recognizedCount }} pending
          </span>
        </div>
        <button
          class="px-5 py-2.5 rounded-xl bg-indigo-500 hover:bg-indigo-600 text-white text-sm font-semibold
                 transition-colors active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed"
          disabled
        >
          Continue to Preview
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useScanStore } from "@/stores/scan";
import type { FileNodeResponse } from "@/api/client";
import SectionCard from "@/components/SectionCard.vue";
import TreeNode from "@/components/TreeNode.vue";

const router = useRouter();
const scanStore = useScanStore();
const activeFilter = ref("all");

onMounted(() => {
  if (!scanStore.result) {
    router.replace("/");
  }
});

const allItems = computed(() => scanStore.result?.items ?? []);

const junkCount = computed(() => allItems.value.filter(n => n.junk).length);
const emptyCount = computed(() => allItems.value.filter(n => n.empty).length);
const movieCount = computed(() => allItems.value.filter(n => n.recognized?.media_type === "movie").length);
const tvCount = computed(() => allItems.value.filter(n => n.recognized?.media_type === "tv").length);

const filters = computed(() => [
  { key: "all", label: "All", count: allItems.value.length },
  { key: "movie", label: "Movies", count: movieCount.value },
  { key: "tv", label: "TV", count: tvCount.value },
  { key: "junk", label: "Junk", count: junkCount.value },
  { key: "empty", label: "Empty", count: emptyCount.value },
]);

/** Root-level children filtered */
const rootChildren = computed(() => {
  if (!scanStore.result) return [];
  const root = scanStore.result.root_path;
  const tree = scanStore.tree;
  const all = tree[root] ?? [];

  if (activeFilter.value === "all") return all;
  if (activeFilter.value === "junk") return all.filter(n => n.junk);
  if (activeFilter.value === "empty") return all.filter(n => n.empty);
  if (activeFilter.value === "movie") return all.filter(n => n.recognized?.media_type === "movie");
  if (activeFilter.value === "tv") return all.filter(n => n.recognized?.media_type === "tv");
  return all;
});
</script>
