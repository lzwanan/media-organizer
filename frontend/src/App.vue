<template>
  <Toast position="top-right" />
  <AppLayout>
    <router-view v-slot="{ Component }">
      <transition name="page" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </AppLayout>
</template>

<script setup lang="ts">
import Toast from "primevue/toast";
import AppLayout from "@/components/AppLayout.vue";
</script>
