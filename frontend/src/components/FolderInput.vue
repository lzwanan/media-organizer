<template>
  <div>
    <!-- Label -->
    <label class="block text-[13px] font-semibold text-gray-500 dark:text-gray-400 mb-2.5 tracking-wide uppercase">
      <slot name="label" />
    </label>

    <!-- Input row -->
    <div class="flex gap-3">
      <div class="flex-1 relative">
        <InputText
          :model-value="modelValue"
          @update:model-value="$emit('update:modelValue', $event)"
          :placeholder="placeholder"
          class="w-full h-11 !text-[15px]"
          :pt="{ root: { class: '!rounded-xl' } }"
        />
        <!-- Clear button -->
        <button
          v-if="modelValue"
          @click="$emit('update:modelValue', '')"
          class="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 flex items-center justify-center rounded-full bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400 text-xs hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
        >
          <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <button
        @click="$emit('browse')"
        class="h-11 px-5 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-[13px] font-medium text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-750 hover:border-gray-300 dark:hover:border-gray-600 active:scale-[0.98] transition-all duration-150"
      >
        {{ $t("home.browse") }}
      </button>
    </div>

    <!-- Hint / recent paths -->
    <p v-if="$slots.hint" class="mt-2.5 text-xs text-gray-400 dark:text-gray-500">
      <slot name="hint" />
    </p>
  </div>
</template>

<script setup lang="ts">
import InputText from "primevue/inputtext";

defineProps<{
  modelValue: string;
  placeholder?: string;
}>();

defineEmits<{
  "update:modelValue": [value: string];
  browse: [];
}>();
</script>
