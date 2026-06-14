import { createApp } from "vue";
import { createPinia } from "pinia";
import { MotionPlugin } from "@vueuse/motion";
import PrimeVue from "primevue/config";
import Aura from "@primevue/themes/aura";
import ToastService from "primevue/toastservice";
import router from "./router";
import i18n from "./i18n";
import App from "./App.vue";

import "./styles/global.css";

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(i18n);
app.use(MotionPlugin);
app.use(ToastService);
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: ".app-dark",
    },
  },
});

app.mount("#app");
