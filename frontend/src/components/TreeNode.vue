<template>
  <div>
    <!-- Directory -->
    <div v-if="node.type === 'directory'" class="flex items-center gap-1">
      <input type="checkbox" :checked="isSelected" @change="$emit('toggle-select', node.path)"
        class="w-4 h-4 rounded border-gray-300 dark:border-gray-600 text-indigo-500 shrink-0" />
      <button @click="expanded = !expanded"
        class="flex-1 flex items-center gap-2 px-2 py-2 ml-0.5 rounded-lg text-left hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
        <svg class="w-4 h-4 text-gray-400 transition-transform duration-200 shrink-0" :class="{ 'rotate-90': expanded }"
          fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
        </svg>
        <svg class="w-4 h-4 text-amber-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round"
            d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z" />
        </svg>
        <div class="flex-1 min-w-0 text-left">
          <div class="flex items-center gap-2">
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300 truncate max-w-[420px]" :title="node.name">{{ node.name }}</span>
            <span v-if="node.junk" class="text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-red-100 dark:bg-red-500/20 text-red-600 dark:text-red-400">{{ $t('scan.filters.junk') }}</span>
            <span v-if="node.empty" class="text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-500">{{ $t('scan.filters.empty') }}</span>
          </div>
          <div v-if="recInfo?.target_name && recInfo.target_name !== node.name" class="mt-0.5">
            <span class="text-xs text-indigo-500 dark:text-indigo-400">→ {{ recInfo.target_name }}</span>
          </div>
        </div>
        <span class="text-xs text-gray-400 shrink-0">{{ childCount(node.path) }} items</span>
      </button>
    </div>

    <!-- Children (expand for dirs) -->
    <div v-if="node.type === 'directory'"
      class="overflow-hidden transition-all duration-200"
      :class="expanded ? 'max-h-[2000px] opacity-100' : 'max-h-0 opacity-0'">
      <div class="ml-5 border-l border-gray-100 dark:border-gray-800 pl-2">
        <TreeNode v-for="child in children(node.path)" :key="child.path" :node="child" :tree="tree"
          :selected-paths="selectedPaths" @toggle-select="(p: string) => $emit('toggle-select', p)" />
      </div>
    </div>

    <!-- File -->
    <div v-else class="flex items-center gap-1">
      <input type="checkbox" :checked="isSelected" @change="$emit('toggle-select', node.path)"
        class="w-4 h-4 rounded border-gray-300 dark:border-gray-600 text-indigo-500 shrink-0" />
      <div class="flex-1 px-2 py-2 ml-0.5 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
        <div class="flex items-center gap-2">
          <svg class="w-4 h-4 text-gray-300 dark:text-gray-600 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
          </svg>
          <span class="text-xs text-gray-500 dark:text-gray-500 truncate flex-1 font-mono max-w-[500px]" :title="node.name">{{ node.name }}</span>
          <span v-if="node.junk" class="text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-red-100 dark:bg-red-500/20 text-red-600 dark:text-red-400 shrink-0">{{ $t('scan.filters.junk') }}</span>
          <span v-else-if="recInfo" class="text-[10px] font-semibold px-1.5 py-0.5 rounded-full shrink-0"
            :class="confidenceClass(recInfo.confidence)">{{ Math.round(recInfo.confidence * 100) }}%</span>
          <span class="text-[10px] text-gray-400 shrink-0">{{ formatSize(node.size) }}</span>
        </div>
        <div v-if="recInfo?.target_name" class="flex items-center gap-2 mt-1 pl-6">
          <svg class="w-4 h-4 text-indigo-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
          <span class="text-sm font-medium text-indigo-600 dark:text-indigo-400 truncate max-w-[500px]" :title="recInfo.target_name">{{ recInfo.target_name }}</span>
        </div>
        <div v-if="!recInfo && !node.junk" class="flex items-center gap-2 mt-1 pl-6">
          <span class="text-xs text-amber-500">⚠ {{ $t('scan.pending') }}</span>
        </div>
        <div v-if="node.junk" class="flex items-center gap-2 mt-1 pl-6">
          <span class="text-xs text-red-400">🗑 {{ $t('scan.suggestedRemove') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import type { FileNodeResponse, RecognizedInfo } from "@/api/client";

const props = defineProps<{
  node: FileNodeResponse;
  tree: Record<string, FileNodeResponse[]>;
  selectedPaths: Set<string>;
}>();

defineEmits<{
  "toggle-select": [path: string];
}>();

const expanded = ref(false);
const recInfo = computed<RecognizedInfo | null>(() => props.node.recognized);
const isSelected = computed(() => props.selectedPaths.has(props.node.path));

function children(parentPath: string): FileNodeResponse[] {
  return props.tree[parentPath] ?? [];
}
function childCount(parentPath: string): number {
  return children(parentPath).length;
}
function confidenceClass(conf: number): string {
  if (conf >= 0.85) return "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400";
  if (conf >= 0.50) return "bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400";
  return "bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400";
}
function formatSize(bytes: number): string {
  if (bytes === 0) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}
</script>
