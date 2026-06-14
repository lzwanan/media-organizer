import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("@/views/Home.vue"),
    },
    {
      path: "/scan",
      name: "scan",
      component: () => import("@/views/Scan.vue"),
    },
    {
      path: "/execute/:taskId",
      name: "execute",
      component: () => import("@/views/Execute.vue"),
    },
    {
      path: "/report/:taskId",
      name: "report",
      component: () => import("@/views/Report.vue"),
    },
    {
      path: "/history",
      name: "history",
      component: () => import("@/views/History.vue"),
    },
    {
      path: "/settings",
      name: "settings",
      component: () => import("@/views/Settings.vue"),
    },
  ],
});

export default router;
