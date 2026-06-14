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
        <p class="text-sm text-gray-400 dark:text-gray-500">
          {{ scanStore.result.total_count }} files · {{ scanStore.dirs.length }} folders
          {{ scanStore.result.root_type ? '· ' + scanStore.result.root_type : '' }}
        </p>
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
        <span class="text-sm text-gray-400">
          {{ scanStore.files.length }} of {{ scanStore.result.total_count }} files selected
        </span>
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
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useScanStore } from "@/stores/scan";
import type { FileNodeResponse } from "@/api/client";
import SectionCard from "@/components/SectionCard.vue";
import TreeNode from "@/components/TreeNode.vue";

const router = useRouter();
const scanStore = useScanStore();

onMounted(() => {
  if (!scanStore.result) {
    router.replace("/");
  }
});

/** Root-level children (depth 0 items directly under root_path) */
const rootChildren = computed(() => {
  if (!scanStore.result) return [];
  const root = scanStore.result.root_path;
  const tree = scanStore.tree;
  return tree[root] ?? [];
});
</script>
