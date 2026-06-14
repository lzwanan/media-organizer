<template>
  <div>
    <label class="block text-[13px] font-semibold text-gray-500 dark:text-gray-400 mb-2.5 tracking-wide uppercase">
      <slot name="label" />
    </label>

    <div class="grid grid-cols-3 gap-3">
      <button
        v-for="opt in options"
        :key="opt.value"
        @click="$emit('update:modelValue', opt.value)"
        class="relative text-left p-4 rounded-xl border transition-all duration-200"
        :class="modelValue === opt.value
          ? 'border-indigo-500 bg-indigo-50/50 dark:bg-indigo-500/10 shadow-sm'
          : 'border-gray-150 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/50 hover:border-gray-250 dark:hover:border-gray-700'"
      >
        <div class="text-xl mb-1.5">{{ opt.icon }}</div>
        <div class="text-[13px] font-semibold text-gray-800 dark:text-gray-200 mb-0.5">
          {{ opt.label }}
        </div>
        <div class="text-[11px] text-gray-400 dark:text-gray-500 leading-snug">
          {{ opt.desc }}
        </div>
        <div
          v-if="modelValue === opt.value"
          class="absolute top-3 right-3 w-4 h-4 rounded-full bg-indigo-500 flex items-center justify-center"
        >
          <svg class="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Option {
  value: string;
  label: string;
  icon: string;
  desc: string;
}

defineProps<{
  modelValue: string;
  options: Option[];
}>();

defineEmits<{
  "update:modelValue": [value: string];
}>();
</script>
