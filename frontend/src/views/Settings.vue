<template>
  <div class="max-w-2xl mx-auto px-6 py-12">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-8">{{ $t("nav.settings") }}</h1>

    <!-- Naming style -->
    <SectionCard>
      <h2 class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-5">Naming Style</h2>
      <div class="space-y-4">
        <div v-for="t in ['movie','tv','anime']" :key="t" class="flex items-center gap-4">
          <span class="text-sm text-gray-600 dark:text-gray-400 w-16 capitalize">{{ t }}</span>
          <div class="flex gap-1">
            <button v-for="s in ['en','zh','bilingual']" :key="s"
              @click="naming[t] = s"
              class="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
              :class="naming[t] === s ? 'bg-indigo-500 text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-700'"
            >{{ s }}</button>
          </div>
        </div>
      </div>
    </SectionCard>

    <!-- API Keys -->
    <div class="mt-6">
      <SectionCard>
        <h2 class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-5">API Keys</h2>
        <div class="space-y-4">
          <div>
            <label class="text-xs text-gray-500 dark:text-gray-400 mb-1.5 block">TMDB API Key</label>
            <input v-model="config.tmdb_key" type="password" placeholder="Enter TMDB API key"
              class="w-full h-10 px-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/10 transition-all" />
          </div>
          <div>
            <label class="text-xs text-gray-500 dark:text-gray-400 mb-1.5 block">Google Translate API Key</label>
            <input v-model="config.translate_key" type="password" placeholder="Enter Google API key"
              class="w-full h-10 px-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/10 transition-all" />
          </div>
        </div>
      </SectionCard>
    </div>

    <!-- Save -->
    <div class="mt-8 flex gap-3 justify-end">
      <button @click="resetDefaults"
        class="px-5 py-2.5 rounded-xl text-sm text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
        Reset
      </button>
      <button @click="save"
        class="px-6 py-2.5 rounded-xl bg-indigo-500 hover:bg-indigo-600 text-white text-sm font-semibold transition-colors">
        Save
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useToast } from "primevue/usetoast";
import api, { fetchConfig } from "@/api/client";
import SectionCard from "@/components/SectionCard.vue";

const toast = useToast();
const naming = ref<Record<string, string>>({ movie: "en", tv: "en", anime: "en" });
const config = ref({ tmdb_key: "", translate_key: "" });

onMounted(async () => {
  try {
    const res = await fetchConfig();
    const d = res.data as any;
    if (d.naming?.style) naming.value = { ...d.naming.style };
    config.value.tmdb_key = d.tmdb?.api_key || "";
    config.value.translate_key = d.translators?.google?.api_key || "";
  } catch {}
});

async function save() {
  try {
    for (const [k, v] of Object.entries(naming.value)) {
      await api.put(`/config/naming.style.${k}`, { value: v });
    }
    await api.put("/config/tmdb.api_key", { value: config.value.tmdb_key });
    await api.put("/config/translators.google.api_key", { value: config.value.translate_key });
    toast.add({ severity: "success", summary: "Saved", detail: "Settings updated", life: 2000 });
  } catch {
    toast.add({ severity: "error", summary: "Error", detail: "Save failed", life: 3000 });
  }
}

async function resetDefaults() {
  try {
    await api.post("/config/reset");
    const res = await fetchConfig();
    const d = res.data as any;
    naming.value = { ...d.naming?.style };
    config.value.tmdb_key = "";
    config.value.translate_key = "";
    toast.add({ severity: "success", summary: "Reset", detail: "Defaults restored", life: 2000 });
  } catch {}
}
</script>
