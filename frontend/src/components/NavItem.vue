<template>
  <router-link
    :to="to"
    class="px-3 py-1.5 rounded-lg text-[13px] font-medium transition-colors duration-150
           text-gray-500 dark:text-gray-400
           hover:text-gray-900 dark:hover:text-white
           hover:bg-gray-100 dark:hover:bg-gray-800"
    active-class="!bg-gray-100 dark:!bg-gray-800 !text-gray-900 dark:!text-white"
  >
    <slot />
  </router-link>
</template>

<script setup lang="ts">
defineProps<{ to: string }>();
</script>
