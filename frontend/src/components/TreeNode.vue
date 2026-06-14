<template>
  <div>
    <!-- Directory -->
    <button
      v-if="node.type === 'directory'"
      @click="expanded = !expanded"
      class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left
             hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors group"
    >
      <svg
        class="w-4 h-4 text-gray-400 transition-transform duration-200 shrink-0"
        :class="{ 'rotate-90': expanded }"
        fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
      </svg>
      <svg class="w-4 h-4 text-amber-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round"
          d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z" />
      </svg>
      <span class="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">{{ node.name }}</span>
      <span class="text-xs text-gray-400 ml-auto opacity-0 group-hover:opacity-100 transition-opacity">
        {{ childCount(node.path) }} items
      </span>
    </button>

    <!-- Children (expandable) -->
    <div
      v-if="node.type === 'directory'"
      class="overflow-hidden transition-all duration-200"
      :class="expanded ? 'max-h-[2000px] opacity-100' : 'max-h-0 opacity-0'"
    >
      <div class="ml-5 border-l border-gray-100 dark:border-gray-800 pl-2">
        <TreeNode
          v-for="child in children(node.path)"
          :key="child.path"
          :node="child"
          :tree="tree"
        />
      </div>
    </div>

    <!-- File -->
    <div
      v-else
      class="flex items-center gap-2 px-3 py-2 rounded-lg text-left
             hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
    >
      <svg class="w-4 h-4 text-gray-300 dark:text-gray-600 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round"
          d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
      </svg>
      <span class="text-sm text-gray-600 dark:text-gray-400 truncate flex-1">{{ node.name }}</span>
      <span class="text-xs text-gray-400 shrink-0">{{ formatSize(node.size) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import type { FileNodeResponse } from "@/api/client";

const props = defineProps<{
  node: FileNodeResponse;
  tree: Record<string, FileNodeResponse[]>;
}>();

const expanded = ref(false);

function children(parentPath: string): FileNodeResponse[] {
  return props.tree[parentPath] ?? [];
}

function childCount(parentPath: string): number {
  return children(parentPath).length;
}

function formatSize(bytes: number): string {
  if (bytes === 0) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}
</script>
