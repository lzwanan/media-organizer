<template>
  <div class="home">
    <!-- Hero -->
    <section
      v-motion
      :initial="{ opacity: 0, y: -30 }"
      :enter="{ opacity: 1, y: 0, transition: { duration: 500 } }"
      class="hero"
    >
      <div class="hero-icon">
        <svg viewBox="0 0 64 64" fill="none">
          <path d="M18 16h16l6 8-6 8H18l-6-8 6-8z" fill="white" opacity="0.9"/>
          <path d="M36 16h14l4 8-4 8H36l-4-8 4-8z" fill="white" opacity="0.6"/>
          <rect x="20" y="38" width="24" height="4" rx="2" fill="white" opacity="0.5"/>
        </svg>
      </div>
      <h1 class="hero-title">Media Organizer</h1>
      <p class="hero-subtitle">智能识别混乱的媒体文件名，一键整理为 Plex / Emby / Jellyfin 标准格式</p>
    </section>

    <!-- Action Card -->
    <section
      v-motion
      :initial="{ opacity: 0, y: 20 }"
      :enter="{ opacity: 1, y: 0, transition: { duration: 500, delay: 150 } }"
      class="action-card"
    >
      <div class="card-glass">
        <!-- Directory input -->
        <div class="field">
          <label class="field-label">
            <svg class="field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
            </svg>
            目标目录
          </label>
          <div class="dir-row">
            <div class="dir-input-wrap">
              <input
                v-model="targetDir"
                placeholder="输入或粘贴目录路径…"
                class="dir-input"
              />
              <button v-if="targetDir" class="dir-clear" @click="targetDir = ''">✕</button>
            </div>
            <button class="browse-btn" @click="browseDirectory">浏览…</button>
          </div>
        </div>

        <!-- Strategy selector -->
        <div class="field">
          <label class="field-label">
            <svg class="field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/>
            </svg>
            整理策略
          </label>
          <div class="strategy-row">
            <button
              v-for="opt in strategies"
              :key="opt.value"
              @click="strategy = opt.value"
              class="strategy-btn"
              :class="{ active: strategy === opt.value }"
            >
              <span class="strategy-icon">{{ opt.icon }}</span>
              <span class="strategy-label">{{ opt.label }}</span>
              <span class="strategy-desc">{{ opt.desc }}</span>
              <span v-if="strategy === opt.value" class="strategy-check">✓</span>
            </button>
          </div>
        </div>

        <!-- Start button -->
        <button
          @click="startScan"
          :disabled="!targetDir.trim()"
          class="start-btn"
          :class="{ ready: targetDir.trim() }"
        >
          <svg v-if="targetDir.trim()" class="start-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          {{ targetDir.trim() ? '开始扫描' : '输入目录路径开始' }}
        </button>
      </div>
    </section>

    <!-- Feature row -->
    <section
      v-motion
      :initial="{ opacity: 0 }"
      :enter="{ opacity: 1, transition: { duration: 500, delay: 400 } }"
      class="features"
    >
      <div class="feature-item">
        <span class="feature-dot green">✓</span>
        <div>
          <div class="feature-title">智能识别</div>
          <div class="feature-sub">自动从文件名提取电影/剧集元数据</div>
        </div>
      </div>
      <div class="feature-item">
        <span class="feature-dot blue">👁</span>
        <div>
          <div class="feature-title">预览对比</div>
          <div class="feature-sub">执行前逐项预览变更，支持手动编辑</div>
        </div>
      </div>
      <div class="feature-item">
        <span class="feature-dot amber">🔒</span>
        <div>
          <div class="feature-title">安全回滚</div>
          <div class="feature-sub">自动备份，支持一键恢复到整理前</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useToast } from "primevue/usetoast";

const toast = useToast();

const targetDir = ref("");
const strategy = ref<"smart" | "inplace" | "rename-only">("smart");

const strategies = [
  { value: "smart" as const, label: "智能识别", icon: "🧠", desc: "自动判断目录与文件类型，按 Plex 标准重组" },
  { value: "inplace" as const, label: "原地整理", icon: "📂", desc: "保持现有目录结构，仅重命名不规范文件" },
  { value: "rename-only" as const, label: "仅重命名", icon: "✏️", desc: "不移动任何文件位置，只在原地修改名称" },
];

function browseDirectory() {
  toast.add({ severity: "info", summary: "提示", detail: "桌面版将打开系统目录选择器。当前请手动输入或粘贴路径。", life: 3000 });
}

function startScan() {
  if (!targetDir.value.trim()) return;
  toast.add({ severity: "success", summary: "开始扫描", detail: `正在扫描 ${targetDir.value}…`, life: 2000 });
}
</script>

<style scoped>
/* ===== Hero ===== */
.hero {
  text-align: center;
  padding: 2.5rem 0 2rem;
}
.hero-icon {
  width: 72px; height: 72px;
  margin: 0 auto 1.25rem;
  border-radius: 16px;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 8px 32px rgba(99,102,241,.25);
}
.hero-icon svg { width: 36px; height: 36px; }
.hero-title {
  font-size: 2.25rem; font-weight: 800; letter-spacing: -0.02em;
  color: #111827; margin-bottom: 0.5rem;
}
.hero-subtitle {
  font-size: 1rem; color: #6b7280; max-width: 28rem; margin: 0 auto; line-height: 1.6;
}

/* ===== Action Card ===== */
.action-card { max-width: 640px; margin: 0 auto; }
.card-glass {
  background: rgba(255,255,255,.75);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(229,231,235,.6);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0,0,0,.04);
}

/* ===== Field ===== */
.field { margin-bottom: 1.5rem; }
.field:last-of-type { margin-bottom: 2rem; }
.field-label {
  display: inline-flex; align-items: center; gap: 0.375rem;
  font-size: 0.8125rem; font-weight: 600; color: #374151;
  margin-bottom: 0.625rem;
}
.field-icon { width: 14px; height: 14px; }

/* ===== Directory Input ===== */
.dir-row { display: flex; gap: 0.75rem; }
.dir-input-wrap { flex: 1; position: relative; }
.dir-input {
  width: 100%; height: 48px; padding: 0 2.5rem 0 1rem;
  border-radius: 12px; border: 2px solid #e5e7eb;
  background: #f9fafb; font-size: 0.875rem; color: #111827;
  outline: none; transition: all .25s;
}
.dir-input::placeholder { color: #9ca3af; }
.dir-input:focus {
  border-color: #6366f1; background: #fff;
  box-shadow: 0 0 0 4px rgba(99,102,241,.08);
}
.dir-clear {
  position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
  width: 20px; height: 20px; border-radius: 50%;
  background: #d1d5db; color: #fff; font-size: 10px;
  display: flex; align-items: center; justify-content: center;
  border: none; cursor: pointer; transition: background .2s;
}
.dir-clear:hover { background: #9ca3af; }
.browse-btn {
  height: 48px; padding: 0 18px; border-radius: 12px;
  border: 2px solid #e5e7eb; background: #f3f4f6;
  font-size: 0.8125rem; font-weight: 500; color: #4b5563;
  cursor: pointer; transition: all .2s; white-space: nowrap;
}
.browse-btn:hover { background: #e5e7eb; border-color: #d1d5db; }
.browse-btn:active { transform: scale(0.96); }

/* ===== Strategy ===== */
.strategy-row {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem;
}
.strategy-btn {
  position: relative; text-align: left; padding: 1rem;
  border-radius: 12px; border: 2px solid #e5e7eb;
  background: #f9fafb; cursor: pointer;
  transition: all .3s;
}
.strategy-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,.06); }
.strategy-btn.active {
  border-color: #6366f1; background: #eef2ff;
  box-shadow: 0 4px 16px rgba(99,102,241,.12);
}
.strategy-icon { display: block; font-size: 1.5rem; margin-bottom: 0.5rem; }
.strategy-label { display: block; font-size: 0.8125rem; font-weight: 600; color: #374151; margin-bottom: 0.25rem; }
.strategy-btn.active .strategy-label { color: #4338ca; }
.strategy-desc { display: block; font-size: 0.6875rem; color: #9ca3af; line-height: 1.4; }
.strategy-check {
  position: absolute; top: 10px; right: 10px;
  width: 20px; height: 20px; border-radius: 50%;
  background: #6366f1; color: #fff; font-size: 11px;
  display: flex; align-items: center; justify-content: center;
}

/* ===== Start Button ===== */
.start-btn {
  width: 100%; height: 52px; border-radius: 12px;
  font-size: 0.9375rem; font-weight: 700; letter-spacing: 0.02em;
  border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 0.5rem;
  transition: all .3s;
  background: #e5e7eb; color: #9ca3af;
  opacity: 0.55;
}
.start-btn.ready {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff; opacity: 1;
  box-shadow: 0 4px 20px rgba(99,102,241,.3);
  background-size: 200% 100%;
  animation: shimmer 3s ease-in-out infinite;
}
.start-btn.ready:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(99,102,241,.4);
}
.start-btn.ready:active { transform: scale(0.98); }
.start-icon { width: 18px; height: 18px; }

@keyframes shimmer {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

/* ===== Features ===== */
.features {
  max-width: 640px; margin: 2.5rem auto 0;
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem;
}
.feature-item {
  display: flex; align-items: flex-start; gap: 0.625rem; padding: 0.75rem;
}
.feature-dot {
  width: 28px; height: 28px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; flex-shrink: 0;
}
.feature-dot.green { background: #d1fae5; color: #059669; }
.feature-dot.blue { background: #dbeafe; color: #2563eb; }
.feature-dot.amber { background: #fef3c7; color: #d97706; }
.feature-title { font-size: 0.8125rem; font-weight: 600; color: #1f2937; margin-bottom: 0.125rem; }
.feature-sub { font-size: 0.6875rem; color: #9ca3af; line-height: 1.35; }
</style>
