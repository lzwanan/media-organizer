<template>
  <div class="max-w-2xl mx-auto px-6 py-16">
    <!-- Hero -->
    <header class="mb-12">
      <h1 class="text-[32px] font-bold tracking-tight text-gray-900 dark:text-white mb-3">
        Organize your media library
      </h1>
      <p class="text-[15px] text-gray-500 dark:text-gray-400 leading-relaxed max-w-lg">
        Automatically rename and restructure your movie and TV files
        into Plex, Emby, and Jellyfin compatible formats.
      </p>
    </header>

    <!-- Card -->
    <SectionCard>
      <div class="space-y-8">
        <!-- Folder input -->
        <FolderInput
          v-model="targetDir"
          placeholder="Paste a directory path…"
          @browse="browseDirectory"
        >
          <template #label>Target directory</template>
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
          <template #label>Strategy</template>
        </StrategyPicker>

        <!-- CTA -->
        <Button
          :label="targetDir.trim() ? 'Start Scan' : 'Enter a directory to begin'"
          :disabled="!targetDir.trim()"
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
import { ref } from "vue";
import { useToast } from "primevue/usetoast";
import Button from "primevue/button";
import SectionCard from "@/components/SectionCard.vue";
import FolderInput from "@/components/FolderInput.vue";
import StrategyPicker from "@/components/StrategyPicker.vue";

const toast = useToast();
const targetDir = ref("");
const strategy = ref("smart");
const recentPaths = ref<string[]>([]);

const strategies = [
  {
    value: "smart",
    label: "Smart",
    icon: "🧠",
    desc: "Detect type and reorganize by Plex standard",
  },
  {
    value: "inplace",
    label: "In Place",
    icon: "📂",
    desc: "Keep folder structure, only rename files",
  },
  {
    value: "rename-only",
    label: "Rename Only",
    icon: "✏️",
    desc: "Rename in place without moving anything",
  },
];

const features = [
  {
    title: "Smart Detection",
    desc: "Extract movie and TV metadata from messy filenames",
    icon: "M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z",
    bg: "bg-indigo-50 dark:bg-indigo-500/10",
    color: "text-indigo-600 dark:text-indigo-400",
  },
  {
    title: "Preview First",
    desc: "Review every change before execution",
    icon: "M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z M15 12a3 3 0 11-6 0 3 3 0 016 0z",
    bg: "bg-emerald-50 dark:bg-emerald-500/10",
    color: "text-emerald-600 dark:text-emerald-400",
  },
  {
    title: "Safe Rollback",
    desc: "Auto-backup before every operation",
    icon: "M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z",
    bg: "bg-amber-50 dark:bg-amber-500/10",
    color: "text-amber-600 dark:text-amber-400",
  },
];

function browseDirectory() {
  toast.add({ severity: "info", summary: "Browse", detail: "Desktop file picker coming soon. Paste a path for now.", life: 3000 });
}

function startScan() {
  if (!targetDir.value.trim()) return;
  toast.add({ severity: "success", summary: "Scanning", detail: targetDir.value, life: 2000 });
}
</script>
