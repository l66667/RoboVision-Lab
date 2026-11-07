/* ==========================================================================
   RoboVision Lab · 机器人视觉学习台
   Vanilla JS. No build step, no external dependencies.
   ========================================================================== */

'use strict';

/* --------------------------------------------------------------------------
   1. Icons & tiny helpers
   -------------------------------------------------------------------------- */

const ICONS = {
  play: '<polygon points="6 3 20 12 6 21 6 3"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
  moon: '<path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8Z"/>',
  check: '<path d="m20 6-11 11-5-5"/>',
  left: '<path d="M19 12H5"/><path d="m12 19-7-7 7-7"/>',
  right: '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
  down: '<path d="m6 9 6 6 6-6"/>',
  up: '<path d="m18 15-6-6-6 6"/>',
  book: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z"/>',
  code: '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
  spark: '<path d="m12 3 1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9L12 3Z"/><path d="M19 15l.9 2.1L22 18l-2.1.9L19 21l-.9-2.1L16 18l2.1-.9L19 15Z"/>',
  reset: '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/>',
  download: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
  terminal: '<polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/>',
  image: '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-5-5L5 21"/>',
  gauge: '<path d="M12 14a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z"/><path d="M12 14 4.5 6.5"/><path d="M4 18a9 9 0 1 1 16 0"/>',
  checks: '<path d="m3 7 2 2 4-4"/><path d="m3 17 2 2 4-4"/><path d="M13 6h8M13 12h8M13 18h8"/>',
  alert: '<path d="M10.3 3.6 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.6a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/>',
  x: '<path d="M18 6 6 18M6 6l12 12"/>',
  menu: '<path d="M3 6h18M3 12h18M3 18h18"/>',
  target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
  zap: '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  message: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2Z"/>',
  cpu: '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
  layers: '<path d="m12 2 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5"/><path d="m3 17 9 5 9-5"/>',
  arrowUp: '<path d="M7 17 17 7"/><path d="M7 7h10v10"/>',
  copy: '<rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
  light: '<path d="M9 18h6M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2Z"/>',
  power: '<path d="M18.4 6.6a9 9 0 1 1-12.8 0"/><path d="M12 2v10"/>',
  chart: '<path d="M3 3v18h18"/><path d="m7 14 4-4 3 3 5-6"/>',
  tablet: '<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M12 18h.01"/>',
};

function icon(name, size = 18) {
  return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name] || ''}</svg>`;
}

function brandMark(size = 26) {
  return `<svg width="${size}" height="${size}" viewBox="0 0 64 64" fill="none" aria-hidden="true">
    <path d="M9 32c6.7-11.4 15.4-17.1 23-17.1S48.3 20.6 55 32c-6.7 11.4-15.4 17.1-23 17.1S15.7 43.4 9 32Z" stroke="currentColor" stroke-width="2.6"/>
    <circle cx="32" cy="32" r="8" fill="currentColor"/>
    <circle cx="35.5" cy="28.5" r="2.4" fill="#060a0f" opacity=".85"/>
  </svg>`;
}

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

function escapeHtml(value) {
  return String(value == null ? '' : value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function inline(text) {
  let s = escapeHtml(text || '');
  s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  s = s.replace(/\n/g, '<br>');
  return s;
}

function fmtNum(value) {
  if (typeof value !== 'number' || !isFinite(value)) return String(value);
  if (Number.isInteger(value)) return String(value);
  return String(Math.round(value * 1000) / 1000);
}

function debounce(fn, wait) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), wait);
  };
}

function loadJSON(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch (err) {
    return fallback;
  }
}

function saveJSON(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch (err) { /* quota */ }
}

function downloadText(filename, text, mime = 'text/plain;charset=utf-8') {
  const blob = new Blob([text], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1500);
}

/* --------------------------------------------------------------------------
   2. Syntax highlighting
   -------------------------------------------------------------------------- */

function highlightPython(code) {
  const pattern = /(#[^\n]*)|("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|\b(def|class|return|if|elif|else|for|while|in|not|and|or|import|from|as|with|try|except|finally|raise|pass|break|continue|lambda|yield|global|nonlocal|assert|del|is)\b|\b(True|False|None)\b|(@[A-Za-z_]\w*)|\b(print|len|range|int|float|str|bool|list|dict|set|tuple|type|abs|min|max|sum|round|enumerate|zip|open|isinstance|sorted|any|all)\b|\b(\d+(?:\.\d+)?)\b|\b([A-Za-z_]\w*)\b(?=\s*\()/g;
  let out = '';
  let last = 0;
  let match;
  while ((match = pattern.exec(code)) !== null) {
    out += escapeHtml(code.slice(last, match.index));
    const [token, comment, str, keyword, constant, decorator, builtin, number, fn] = match;
    let cls = '';
    if (comment) cls = 'tok-com';
    else if (str) cls = 'tok-str';
    else if (keyword) cls = 'tok-kw';
    else if (constant) cls = 'tok-bi';
    else if (decorator) cls = 'tok-decorator';
    else if (builtin) cls = 'tok-bi';
    else if (number) cls = 'tok-num';
    else if (fn) cls = 'tok-fn';
    out += cls ? `<span class="${cls}">${escapeHtml(token)}</span>` : escapeHtml(token);
    last = match.index + token.length;
  }
  out += escapeHtml(code.slice(last));
  return out;
}

function highlightHalcon(code) {
  const pattern = /(^\s*\*[^\n]*)|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|\b(read_image|write_image|rgb1_to_gray|decompose3|threshold|connection|select_shape|area_center|orientation_region|vector_to_hom_mat2d|vector_to_hom_mat3d|affine_trans_point_2d|affine_trans_point_3d|calibrate_cameras|calibrate_hand_eye|get_calib_data|gen_cross_contour_xld|dev_display|dev_open_window|tuple_sort|tuple_concat)\b|\b(\d+(?:\.\d+)?)\b|(:=)/gm;
  let out = '';
  let last = 0;
  let match;
  while ((match = pattern.exec(code)) !== null) {
    out += escapeHtml(code.slice(last, match.index));
    const [token, comment, str, fn, number, op] = match;
    let cls = '';
    if (comment) cls = 'tok-com';
    else if (str) cls = 'tok-str';
    else if (fn) cls = 'tok-fn';
    else if (number) cls = 'tok-num';
    else if (op) cls = 'tok-op';
    out += cls ? `<span class="${cls}">${escapeHtml(token)}</span>` : escapeHtml(token);
    last = match.index + token.length;
  }
  out += escapeHtml(code.slice(last));
  return out;
}

/* --------------------------------------------------------------------------
   3. App state
   -------------------------------------------------------------------------- */

const LS = {
  progress: 'rv3.progress',
  drafts: 'rv3.drafts',
  scratch: 'rv3.scratch',
  theme: 'rv3.theme',
};

const state = {
  data: null,
  health: null,
  chapters: [],
  lessons: [],
  byId: {},
  currentId: null,
  progress: loadJSON(LS.progress, {}),
  drafts: loadJSON(LS.drafts, {}),
  scratch: loadJSON(LS.scratch, {}),
  theme: localStorage.getItem(LS.theme) || 'dark',
  params: {},
  mode: 'dev',
  runMode: 'lesson',
  guideView: 'map',
  skillsView: 'map',
  weekIndex: null,
  skillIndex: 6,
  lastRun: null,
  outTab: 'console',
  searchOpen: false,
  searchIndex: 0,
  aiMessages: [],
  aiBusy: false,
  runBusy: false,
};

const saveEditorDebounced = debounce((id, mode, code) => {
  if (mode === 'scratch') {
    state.scratch[id] = code;
    saveJSON(LS.scratch, state.scratch);
  } else {
    state.drafts[id] = code;
    saveJSON(LS.drafts, state.drafts);
  }
}, 350);

function saveEditorImmediate() {
  const ta = $('#code');
  const lesson = currentLesson();
  if (!ta || !lesson) return;
  if (state.mode === 'scratch') {
    state.scratch[lesson.id] = ta.value;
    saveJSON(LS.scratch, state.scratch);
  } else {
    state.drafts[lesson.id] = ta.value;
    saveJSON(LS.drafts, state.drafts);
  }
}

function saveProgress() {
  saveJSON(LS.progress, state.progress);
}

function lessonProgress(id) {
  const p = state.progress[id];
  if (!p || typeof p !== 'object') {
    return { completed: false, checks: {}, tasks: [], quiz: {}, updated: 0 };
  }
  return {
    completed: !!p.completed,
    checks: p.checks || {},
    tasks: Array.isArray(p.tasks) ? p.tasks : [],
    quiz: p.quiz || {},
    updated: p.updated || 0,
  };
}

function updateProgress(id, patch) {
  const p = lessonProgress(id);
  Object.assign(p, patch);
  p.updated = Date.now();
  state.progress[id] = p;
  saveProgress();
  refreshChrome();
}

function completedCount() {
  return state.lessons.filter((l) => lessonProgress(l.id).completed).length;
}

function percentComplete() {
  if (!state.lessons.length) return 0;
  return Math.round((completedCount() / state.lessons.length) * 100);
}

function currentLesson() {
  return state.byId[state.currentId] || null;
}

function getDraft(lesson) {
  const saved = state.drafts[lesson.id];
  return typeof saved === 'string' && saved.length ? saved : lesson.starter;
}

function scratchTemplate(lesson) {
  const task = (lesson.tasks || []).find((t) => t.kind === 'dev') || (lesson.tasks || [])[0];
  const lines = [
    '# ' + '='.repeat(62),
    `#  我的练习 · ${lesson.title}`,
    '# ' + '='.repeat(62),
    `#  任务：${task ? task.title : '用本课知识完成一个小任务'}`,
  ];
  if (task && task.detail) {
    lines.push('#  ' + String(task.detail).replace(/\n/g, ' '));
  }
  lines.push('#');
  if (lesson.mode === 'vision') {
    lines.push('#  可用：image（BGR 输入图）、params（参数）、');
    lines.push('#        capture("名称", 图)、metric("名称", 值)');
  } else {
    lines.push('#  这一课没有输入图，直接写 Python 即可。');
  }
  lines.push('#');
  lines.push('#  这段代码只属于你：不会改课程代码，也不会自动判题。');
  lines.push('#  写完点「运行我的代码」，或按 Ctrl + Enter。');
  lines.push('# ' + '='.repeat(62));
  lines.push('');
  lines.push(`print("开始练习：${lesson.title}")`);
  if (lesson.mode === 'vision') {
    lines.push('print("输入图尺寸:", image.shape)');
  }
  lines.push('');
  lines.push('');
  return lines.join('\n');
}

function getScratch(lesson) {
  const saved = state.scratch[lesson.id];
  return typeof saved === 'string' && saved.length ? saved : scratchTemplate(lesson);
}

function chapterOf(lesson) {
  return state.chapters.find((c) => c.id === lesson.chapterId) || null;
}

/* --------------------------------------------------------------------------
   4. Theme
   -------------------------------------------------------------------------- */

function applyTheme(theme) {
  state.theme = theme === 'light' ? 'light' : 'dark';
  document.documentElement.dataset.theme = state.theme;
  localStorage.setItem(LS.theme, state.theme);
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute('content', state.theme === 'light' ? '#f5f2e9' : '#070b10');
}

function toggleTheme() {
  applyTheme(state.theme === 'dark' ? 'light' : 'dark');
  const btn = $('#themeBtn');
  if (btn) btn.innerHTML = icon(state.theme === 'dark' ? 'sun' : 'moon');
}

/* --------------------------------------------------------------------------
   5. Chrome: topbar, ring, shared footer
   -------------------------------------------------------------------------- */

function progressRing() {
  const pct = percentComplete();
  const c = 2 * Math.PI * 13;
  const offset = c * (1 - pct / 100);
  return `<svg class="ring" viewBox="0 0 30 30" aria-hidden="true">
    <circle class="bg" cx="15" cy="15" r="13"></circle>
    <circle class="fg" id="ringFg" cx="15" cy="15" r="13"
      stroke-dasharray="${c.toFixed(2)}" stroke-dashoffset="${offset.toFixed(2)}"></circle>
  </svg>`;
}

function topbar(active) {
  const pct = percentComplete();
  const links = [
    ['#/', '课程地图', 'map'],
    ['#/guide', '学习路线', 'guide'],
    ['#/skills', '技能地图', 'skills'],
  ];
  return `<header class="topbar">
    <a class="brand" href="#/" aria-label="RoboVision Lab 首页">
      <span class="brand-mark">${brandMark(25)}</span>
      <span class="brand-text"><strong>RoboVision Lab</strong><span>机器人视觉学习台</span></span>
    </a>
    <nav class="topnav" aria-label="主导航">
      ${links.map(([href, label, key]) => `<a class="navlink ${active === key ? 'active' : ''}" href="${href}">${label}</a>`).join('')}
    </nav>
    <div class="top-actions">
      <button class="icon-btn" data-action="open-search" title="搜索课程 (Ctrl+K)" aria-label="搜索课程">${icon('search')}</button>
      <a class="progress-chip" href="#/" title="总进度 ${pct}%">${progressRing()}<b id="pctText">${pct}%</b></a>
      <button class="icon-btn" id="themeBtn" data-action="toggle-theme" title="切换主题" aria-label="切换主题">${icon(state.theme === 'dark' ? 'sun' : 'moon')}</button>
      <button class="icon-btn accent" data-action="toggle-ai" title="AI 助教" aria-label="AI 助教">${icon('spark')}</button>
    </div>
  </header>`;
}

function pageFooter() {
  const health = state.health;
  const env = health ? `Python ${escapeHtml(health.python)} · OpenCV ${escapeHtml(health.cv2)} · NumPy ${escapeHtml(health.numpy)}` : '本地运行';
  return `<footer class="page-footer">
    <span>RoboVision Lab v3.0 · ${env}</span>
    <span class="spacer"></span>
    <button class="btn btn-ghost btn-sm" data-action="lan-info">${icon('tablet', 14)} 平板访问</button>
    <button class="btn btn-ghost btn-sm" data-action="export-progress">${icon('download', 14)} 导出学习进度</button>
    <button class="btn btn-ghost btn-sm" data-action="exit-app">${icon('power', 14)} 退出服务</button>
  </footer>`;
}

function refreshChrome() {
  const pct = percentComplete();
  const ring = $('#ringFg');
  if (ring) {
    const c = 2 * Math.PI * 13;
    ring.setAttribute('stroke-dashoffset', String(c * (1 - pct / 100)));
  }
  const txt = $('#pctText');
  if (txt) txt.textContent = pct + '%';
  $$('.nav-item[data-lesson]').forEach((a) => {
    const p = lessonProgress(a.dataset.lesson);
    const dot = a.querySelector('.status-dot');
    if (!dot) return;
    dot.classList.toggle('done', p.completed);
    dot.classList.toggle('current', a.dataset.lesson === state.currentId);
  });
  const navBar = $('#navBar');
  if (navBar) {
    const lesson = currentLesson();
    const ch = lesson ? chapterOf(lesson) : null;
    if (ch) {
      const done = ch.lessons.filter((l) => lessonProgress(l.id).completed).length;
      navBar.style.width = Math.round((done / ch.lessons.length) * 100) + '%';
    }
  }
  const navPct = $('#navPct');
  if (navPct) navPct.textContent = pct + '%';
  const completeBtn = $('#completeBtn');
  if (completeBtn && state.currentId) {
    const done = lessonProgress(state.currentId).completed;
    completeBtn.classList.toggle('done', done);
    completeBtn.innerHTML = done ? `${icon('check', 16)} 已完成` : `${icon('check', 16)} 标记完成`;
  }
}

/* --------------------------------------------------------------------------
   6. Map page
   -------------------------------------------------------------------------- */

function lessonGlobalIndex(lesson) {
  return state.lessons.indexOf(lesson) + 1;
}

function firstIncomplete() {
  return state.lessons.find((l) => !lessonProgress(l.id).completed) || state.lessons[state.lessons.length - 1];
}

function renderMap() {
  if (!state.lessons.length) return;
  const next = firstIncomplete();
  const nextIndex = lessonGlobalIndex(next);
  const pct = percentComplete();
  const done = completedCount();
  const app = $('#app');
  app.innerHTML = `${topbar('map')}
    <main class="page">
      <section class="hero">
        <div class="hero-copy">
          <span class="eyebrow">Python × OpenCV × Robotics</span>
          <h1>从第一行 Python，<br>到<span class="grad">会看世界的机器人</span></h1>
          <p class="lede">为机器人工程专业准备的 100 天 OpenCV + ROS2 工程入门：32 节课程，从图像处理到节点、接口、package.xml/CMake 和 colcon，每节课都能切到「自己写」空白区。</p>
          <div class="hero-actions">
            <a class="btn btn-primary btn-lg" href="#/lesson/${next.id}">${pct >= 100 ? '复习最后一课' : '继续第 ' + nextIndex + ' 课'} ${icon('right', 18)}</a>
            <a class="btn btn-lg" href="#/guide">看 100 天路线</a>
          </div>
          <div class="hero-note">
            <span>${icon('check', 14)} 零基础可学</span>
            <span>${icon('cpu', 14)} 真实可运行</span>
            <span>${icon('code', 14)} 自己写代码</span>
            <span>${icon('target', 14)} 自动判题</span>
            <span>${icon('layers', 14)} 本地离线</span>
          </div>
          <div class="hero-stats">
            <div class="stat"><b>${state.lessons.length}</b><span>Lessons</span></div>
            <div class="stat"><b>${state.chapters.length}</b><span>Chapters</span></div>
            <div class="stat"><b>${done}</b><span>Completed</span></div>
            <div class="stat"><b>${pct}%</b><span>Progress</span></div>
          </div>
        </div>
        <div class="hero-visual" aria-hidden="true">
          <span class="frame-corner tl"></span><span class="frame-corner tr"></span>
          <span class="frame-corner bl"></span><span class="frame-corner br"></span>
          <span class="scan"></span>
          <div class="hero-chip c1"><i></i> HSV MASK · 4 blobs</div>
          <div class="hero-chip c2"><i></i> HOMOGRAPHY · 3×3</div>
          <div class="hero-chip c3"><i></i> PID · e = 18.4 px</div>
          <div class="hero-chip c4"><i></i> CRC16 · 0x4B37</div>
          <div class="hero-eye">
            <svg viewBox="0 0 64 64" fill="none">
              <path d="M6 32c7-12 16-18 26-18s19 6 26 18c-7 12-16 18-26 18S13 44 6 32Z" stroke="currentColor" stroke-width="1.6" opacity=".8"/>
              <path d="M12 32c5.8-8.5 12.5-12.8 20-12.8S46.2 23.5 52 32c-5.8 8.5-12.5 12.8-20 12.8S17.8 40.5 12 32Z" stroke="currentColor" stroke-width="1" opacity=".35"/>
              <circle cx="32" cy="32" r="10" stroke="currentColor" stroke-width="1.6"/>
              <g class="pupil"><circle cx="32" cy="32" r="5.5" fill="currentColor"/><circle cx="34" cy="30" r="1.8" fill="#060a0f"/></g>
              <path d="M32 4v5M32 55v5M4 32h5M55 32h5" stroke="currentColor" stroke-width="1.2" opacity=".5"/>
            </svg>
          </div>
          <div class="hero-hud"><span>CAM 01 · 1280×800</span><span><b>TRACKING</b> · 30 FPS</span></div>
        </div>
      </section>

      <section class="section">
        <div class="section-head">
          <div>
            <span class="eyebrow">Course map</span>
            <h2>十个章节，一条完整的工程链路</h2>
            <p>从语法到像素，从 OpenCV 到 ROS2 节点、接口、CMake 和 colcon。建议按顺序学，每节课都先跑一遍，再改一个参数。</p>
          </div>
          <div style="display:flex;gap:8px;align-items:center">
            <span class="badge green">${done}/${state.lessons.length} 完成</span>
            <button class="btn btn-sm" data-action="export-progress">${icon('download', 14)} 导出进度</button>
          </div>
        </div>
        <div class="chapter-grid">
          ${state.chapters.map((ch) => chapterCard(ch)).join('')}
        </div>
        <div class="next-card">
          <div>
            <div class="kicker">${pct >= 100 ? 'Review' : 'Next up'}</div>
            <h3>${pct >= 100 ? '全部完成，回到任意一课复习' : `第 ${nextIndex} 课 · ${escapeHtml(next.title)}`}</h3>
            <p>${escapeHtml(next.subtitle)} · 约 ${next.minutes} 分钟</p>
          </div>
          <a class="btn btn-primary" href="#/lesson/${next.id}">${pct >= 100 ? '打开课程' : '开始学习'} ${icon('right', 16)}</a>
        </div>
      </section>

      <section class="section">
        <div class="section-head">
          <div>
            <span class="eyebrow">How it works</span>
            <h2>不是看视频，是动手改代码</h2>
            <p>每节课都有「逐段讲解 + 可运行代码 + 自动检查 + 小测」。你看的每一段代码，都在右侧编辑器里。</p>
          </div>
        </div>
        <div class="stack-grid">
          <div class="stack-item now"><div class="sk">01 / READ</div><h4>先读逐段讲解</h4><p>每段代码配一段「为什么」，不是 API 词典，而是工程判断。</p></div>
          <div class="stack-item"><div class="sk">02 / RUN</div><h4>原样跑一遍</h4><p>点运行，看控制台、图像和指标；先确认基线，再谈修改。</p></div>
          <div class="stack-item now"><div class="sk">03 / WRITE</div><h4>切到「自己写」</h4><p>空白练习区，不覆盖课程代码、不自动判题；从零写一遍，才是真的会。</p></div>
          <div class="stack-item"><div class="sk">04 / TUNE</div><h4>只改一个参数</h4><p>用滑杆或代码改一个变量，观察结果怎么变，并写下原因。</p></div>
          <div class="stack-item"><div class="sk">05 / CHECK</div><h4>让检查变绿</h4><p>自动检查会验证关键结果；全部通过，本课自动标记完成。</p></div>
          <div class="stack-item"><div class="sk">06 / QUIZ</div><h4>用自己的话解释</h4><p>小测不是背 API，而是判断「什么场景该用什么方法」。</p></div>
          <div class="stack-item"><div class="sk">07 / BUILD</div><h4>做进作品集</h4><p>结课项目输出检测报告、节拍和指标，直接写进简历。</p></div>
        </div>
      </section>
      ${pageFooter()}
    </main>`;
}

function chapterCard(ch) {
  const total = ch.lessons.length;
  const done = ch.lessons.filter((l) => lessonProgress(l.id).completed).length;
  const pct = total ? Math.round((done / total) * 100) : 0;
  return `<article class="chapter-card" style="--ch-color:${ch.color}">
    <div class="chapter-head">
      <div class="chapter-num">${escapeHtml(ch.number)}</div>
      <div class="chapter-title">
        <h3>${escapeHtml(ch.title)}</h3>
        <p>${escapeHtml(ch.subtitle)}</p>
      </div>
      <div class="chapter-meta"><b>${done}/${total}</b><span>LESSONS</span></div>
    </div>
    <div class="chapter-progress"><div class="bar"><i style="width:${pct}%"></i></div></div>
    <div class="lesson-list">
      ${ch.lessons.map((l) => {
        const p = lessonProgress(l.id);
        return `<a class="lesson-row" href="#/lesson/${l.id}">
          <span class="idx">${String(lessonGlobalIndex(l)).padStart(2, '0')}</span>
          <span class="status-dot ${p.completed ? 'done' : ''}"></span>
          <span class="name">${escapeHtml(l.title)}</span>
          <span class="mins">${l.minutes}m</span>
        </a>`;
      }).join('')}
    </div>
  </article>`;
}

/* --------------------------------------------------------------------------
   7. Guide page
   -------------------------------------------------------------------------- */

function lessonLink(id, label) {
  const l = state.byId[id];
  if (!l) return escapeHtml(label || id);
  return `<a href="#/lesson/${l.id}">${escapeHtml(label || l.title)}</a>`;
}

const WEEK_POINTS = [
  [100, 100], [360, 100], [620, 100], [880, 100],
  [100, 290], [360, 290], [620, 290], [880, 290],
  [100, 480], [360, 480], [620, 480], [880, 480],
];
const WEEK_PATH = 'M 100 100 L 880 100 L 880 190 L 100 190 L 100 290 L 880 290 L 880 380 L 100 380 L 100 480 L 880 480';

function currentWeekIndex(weeks) {
  const index = weeks.findIndex((w) => w.ids.some((id) => !lessonProgress(id).completed));
  return index < 0 ? weeks.length - 1 : index;
}

function weekStats(week) {
  const total = week.ids.length;
  const done = week.ids.filter((id) => lessonProgress(id).completed).length;
  return { total, done, pct: total ? Math.round((done / total) * 100) : 0 };
}

function weekColor(week) {
  const lesson = state.byId[week.ids[0]];
  const ch = lesson ? chapterOf(lesson) : null;
  return ch ? ch.color : 'var(--accent)';
}

function weekDetailHTML(index) {
  const weeks = state.weekData || [];
  const week = weeks[index];
  if (!week) return '';
  const stats = weekStats(week);
  const nextId = week.ids.find((id) => !lessonProgress(id).completed) || week.ids[0];
  const allDone = stats.done === stats.total;
  return `<div class="week-detail-card" style="--wc:${weekColor(week)}">
    <div class="wd-main">
      <div class="wd-kicker">${escapeHtml(week.week)} · ${stats.done}/${stats.total} 完成</div>
      <h3>${escapeHtml(week.theme)}</h3>
      <div class="bar"><i style="width:${stats.pct}%"></i></div>
      <div class="wd-links">${week.ids.map((id) => `<a class="wd-link" href="#/lesson/${id}">${escapeHtml((state.byId[id] || {}).title || id)}</a>`).join('')}</div>
    </div>
    <div class="wd-side">
      <div class="wd-output-label">本周产出</div>
      <p>${inline(week.output)}</p>
      <a class="btn btn-sm btn-primary" href="#/lesson/${nextId}">${allDone ? '复习本周' : '开始本周'} ${icon('right', 14)}</a>
    </div>
  </div>`;
}

function weekMapHTML(weeks) {
  state.weekData = weeks;
  const current = currentWeekIndex(weeks);
  if (typeof state.weekIndex !== 'number') state.weekIndex = current;
  const path = WEEK_PATH;
  const nodes = weeks.map((week, i) => {
    const stats = weekStats(week);
    const complete = stats.done === stats.total;
    const classes = ['week-node'];
    if (complete) classes.push('done');
    if (i === current) classes.push('current');
    if (i === state.weekIndex) classes.push('selected');
    const [x, y] = WEEK_POINTS[i];
    return `<div class="${classes.join(' ')}" style="left:${x / 10}%;top:${y / 5.8}%;--wc:${weekColor(week)};--p:${stats.pct}%;--delay:${i * 0.05}s">
      <button class="week-dot" data-action="select-week" data-week="${i}" aria-label="${escapeHtml(week.week + ' ' + week.theme)}">
        <span class="week-inner"><b>${String(i + 1).padStart(2, '0')}</b><small>${stats.done}/${stats.total}</small></span>
        ${complete ? `<span class="week-check">${icon('check', 10)}</span>` : ''}
      </button>
      <span class="week-node-label">${escapeHtml(week.theme)}</span>
    </div>`;
  }).join('');
  return `<div class="week-map-wrap">
    <div class="week-map" role="group" aria-label="12 周学习路线图">
      <svg class="week-path" viewBox="0 0 1000 580" preserveAspectRatio="none" aria-hidden="true">
        <path class="track" d="${path}"></path>
        <path class="flow" d="${path}"></path>
        <circle class="traveler" r="4.5">
          <animateMotion dur="11s" repeatCount="indefinite" path="${path}"></animateMotion>
        </circle>
      </svg>
      <span class="map-tag start">START</span>
      <span class="map-tag finish">FINISH</span>
      ${nodes}
    </div>
    <div class="viz-legend"><span><i class="lg-dot dev"></i>圆环：本周完成度</span><span><i class="lg-dot tune"></i>脉冲：当前周</span><span><i class="lg-dot size"></i>虚线与光点：学习顺序</span></div>
    <div id="weekDetail">${weekDetailHTML(state.weekIndex)}</div>
    <div class="week-mobile-list">
      ${weeks.map((week, i) => {
        const stats = weekStats(week);
        const complete = stats.done === stats.total;
        return `<article class="week-mobile-card ${complete ? 'done' : ''}" style="--wc:${weekColor(week)}">
          <div class="wmc-head"><span>${escapeHtml(week.week)}</span><b>${stats.done}/${stats.total}</b></div>
          <h4>${escapeHtml(week.theme)}</h4>
          <div class="wd-links">${week.ids.map((id) => `<a href="#/lesson/${id}">${escapeHtml((state.byId[id] || {}).title || id)}</a>`).join('')}</div>
          <p>${inline(week.output)}</p>
        </article>`;
      }).join('')}
    </div>
  </div>`;
}

function weekListHTML(weeks) {
  return `<div style="overflow-x:auto">
    <table class="week-table">
      <thead><tr><th>周</th><th>主题</th><th>课程</th><th class="hide-sm">本周产出</th></tr></thead>
      <tbody>
        ${weeks.map((week) => {
          const stats = weekStats(week);
          return `<tr>
            <td class="wk">${escapeHtml(week.week)}</td>
            <td><strong>${escapeHtml(week.theme)}</strong><div class="mini-pct">${stats.done}/${stats.total}</div></td>
            <td>${week.ids.map((id) => lessonLink(id)).join('<br>')}</td>
            <td class="hide-sm">${inline(week.output)}</td>
          </tr>`;
        }).join('')}
      </tbody>
    </table>
  </div>`;
}

function selectWeek(index) {
  state.weekIndex = index;
  $$('.week-node').forEach((node) => {
    node.classList.toggle('selected', Number(node.dataset.week) === index);
  });
  const detail = $('#weekDetail');
  if (detail) {
    detail.innerHTML = weekDetailHTML(index);
    detail.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

function skillDetailHTML(index) {
  const skills = state.skillData || [];
  const skill = skills[index];
  if (!skill) return '';
  return `<div class="skill-detail-card" style="--sc:${skill.color}">
    <div class="skill-detail-head">
      <span class="sd-index">${String(index + 1).padStart(2, '0')}</span>
      <div><div class="sd-kicker">SKILL / ${skill.ids.length} 节课</div><h3>${escapeHtml(skill.name)}</h3></div>
    </div>
    <div class="skill-detail-grid">
      <div><div class="sd-label">${icon('code', 13)} 开发型用法</div><p>${inline(skill.dev)}</p></div>
      <div><div class="sd-label">${icon('gauge', 13)} 调控型用法</div><p>${inline(skill.tune)}</p></div>
      <div><div class="sd-label">${icon('layers', 13)} 作品集证据</div><p>${inline(skill.evidence)}</p></div>
    </div>
    <div class="sd-links">${skill.ids.map((id) => `<a class="wd-link" href="#/lesson/${id}">${escapeHtml((state.byId[id] || {}).title || id)}</a>`).join('')}</div>
  </div>`;
}

function skillMapHTML(skills) {
  state.skillData = skills;
  return `<div class="skill-map-wrap">
    <div class="skill-map" role="group" aria-label="技能二维地图：横轴开发，纵轴调控">
      <span class="quad q-tl">偏调控</span>
      <span class="quad q-tr">双修</span>
      <span class="quad q-bl">基础</span>
      <span class="quad q-br">偏开发</span>
      <span class="axis-label x">开发 / 实现 →</span>
      <span class="axis-label y">调控 / 现场 →</span>
      ${skills.map((skill, i) => `<div class="skill-node ${i === state.skillIndex ? 'selected' : ''}" style="left:${skill.x}%;top:${skill.y}%;--s:${skill.size}px;--c:${skill.color};--delay:${i * 0.12}s">
        <button class="skill-bubble" data-action="select-skill" data-skill="${i}" aria-label="${escapeHtml(skill.name)}" title="${escapeHtml(skill.name)}">
          <small>${String(i + 1).padStart(2, '0')}</small>
          <b>${escapeHtml(skill.short)}</b>
        </button>
      </div>`).join('')}
    </div>
    <div class="skill-legend"><span><i class="lg-dot dev"></i>越靠右：开发/实现越多</span><span><i class="lg-dot tune"></i>越靠上：调控/现场越多</span><span><i class="lg-dot size"></i>气泡越大：课程覆盖越多</span></div>
    <div id="skillDetail">${skillDetailHTML(state.skillIndex)}</div>
    <div class="skill-mobile-list">
      ${skills.map((skill, i) => `<article class="skill-mobile-card" style="--sc:${skill.color}">
        <div class="smc-head"><span>${String(i + 1).padStart(2, '0')}</span><h4>${escapeHtml(skill.name)}</h4></div>
        <div class="smc-links">${skill.ids.map((id) => `<a href="#/lesson/${id}">${escapeHtml((state.byId[id] || {}).title || id)}</a>`).join('<span class="sep">·</span>')}</div>
        <p><b>开发</b>${inline(skill.dev)}</p>
        <p><b>调控</b>${inline(skill.tune)}</p>
        <p><b>证据</b>${inline(skill.evidence)}</p>
      </article>`).join('')}
    </div>
  </div>`;
}

function skillTableHTML(skills) {
  return `<div style="overflow-x:auto">
    <table class="skill-table">
      <thead><tr><th>技能</th><th>对应课程</th><th>开发型用法</th><th>调控型用法</th><th>作品集证据</th></tr></thead>
      <tbody>
        ${skills.map((s) => `<tr>
          <td>${escapeHtml(s.name)}</td>
          <td class="mono" style="font-size:10.5px;color:var(--muted)">${s.ids.map((id) => `<a href="#/lesson/${id}">${id}</a>`).join(' · ')}</td>
          <td>${inline(s.dev)}</td>
          <td>${inline(s.tune)}</td>
          <td>${inline(s.evidence)}</td>
        </tr>`).join('')}
      </tbody>
    </table>
  </div>`;
}

function selectSkill(index) {
  state.skillIndex = index;
  $$('.skill-node').forEach((node, i) => node.classList.toggle('selected', i === index));
  const detail = $('#skillDetail');
  if (detail) {
    detail.innerHTML = skillDetailHTML(index);
    detail.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

function renderGuide() {
  const health = state.health;
  const weeks = [
    { week: '第 1 周', theme: 'Python 入门', ids: ['py-first-run', 'py-types'], output: '每天 1 课，重点是把报错读懂；写一个 3 行的温度换算脚本。' },
    { week: '第 2 周', theme: '列表、函数与类', ids: ['py-list-dict', 'py-functions', 'py-class-json'], output: '写一个能读 JSON 日志、统计电量最低时刻的小脚本。' },
    { week: '第 3 周', theme: 'NumPy 与图像', ids: ['np-array', 'cv-image-array', 'cv-color-hsv'], output: '用 NumPy 生成渐变图，再做 BGR/HSV 分割；用自己的照片试一次。' },
    { week: '第 4 周', theme: '阈值/轮廓/透视', ids: ['cv-threshold-edge', 'cv-contour-shape', 'cv-perspective'], output: '做一次零件计数；把斜拍的工位图拉正。' },
    { week: '第 5 周', theme: '特征/循迹/分拣', ids: ['cv-template-orb', 'robot-line', 'robot-color-sort'], output: '比较模板/ORB；调循迹 PID；输出物块毫米坐标。' },
    { week: '第 6 周', theme: '对接/光流/标定', ids: ['robot-aruco', 'robot-flow', 'robot-calib'], output: 'ArUco 估距、两帧估速、6 张棋盘格标定。' },
    { week: '第 7 周', theme: '通信/评估/结课', ids: ['ctrl-serial', 'ctrl-state', 'eng-debug', 'capstone-cell'], output: 'CRC/状态机；P/R 评估；分拣站报告。' },
    { week: '第 8 周', theme: 'ROS2 基础', ids: ['ros2-pubsub', 'ros2-msg-srv', 'ros2-remap-namespace'], output: '写发布/订阅节点；自定义 Detection.msg/Detect.srv；用 namespace 隔离两台机器人。' },
    { week: '第 9 周', theme: 'ROS2 进阶', ids: ['ros2-launch-timer', 'ros2-sync-executor', 'ros2-params-logging'], output: '写 launch；用 message_filters 同步相机/雷达；参数和日志可调。' },
    { week: '第 10 周', theme: 'ROS2 工程', ids: ['ros2-package-cmake', 'ros2-rosidl', 'ros2-colcon-workspace'], output: '写 package.xml/CMakeLists；接口包；colcon 多包工作空间。' },
    { week: '第 11 周', theme: 'ROS2 视觉集成', ids: ['ros2-vision-node'], output: '把 OpenCV 检测包成 ROS2 节点，发布 Detection，参数化 min_area。' },
    { week: '第 12 周', theme: '复盘 + 选修复刻', ids: ['github-rotation'], output: '录 2 分钟演示；整理 10 个项目问答；有余力再复刻 GitHub 项目。' },
  ];
  if (typeof state.weekIndex !== 'number' || state.weekIndex < 0 || state.weekIndex >= weeks.length) {
    state.weekIndex = currentWeekIndex(weeks);
  }

  const roles = [
    {
      tag: 'Development track',
      title: '开发型：把算法做成产品',
      desc: '负责视觉模块、SDK/API、协议、部署与测试。需要能把一个 demo 变成可回归、可配置、可维护的模块。',
      items: ['Python / C++、OpenCV、NumPy', 'ROS2 topic/service、串口/CAN', '单元测试、性能剖析、Git', '把模型/算法部署到边缘设备'],
      color: 'var(--blue)',
    },
    {
      tag: 'Commissioning track',
      title: '调控型：让现场稳定跑起来',
      desc: '负责标定、光照、参数、节拍和故障排查。需要快速判断「是视觉、通信、执行器还是工艺」的问题。',
      items: ['HSV/阈值/形态学参数整定', '相机标定、手眼标定、坐标核对', 'PID 整定、节拍与误检分析', '看日志、复现问题、写复盘'],
      color: 'var(--amber)',
    },
  ];

  const stack = [
    ['NOW', 'Python + NumPy', '第 1–3 章。数组、函数、类、JSON，是所有工具的基础。', true],
    ['NOW', 'OpenCV', '第 2–3 章。图像处理、几何、特征、标定、光流。', true],
    ['NOW', 'ROS2', '第 6–9 章。pub/sub、msg/srv、launch、executor、参数。', true],
    ['NOW', 'colcon + ament', '第 8 章。package.xml、CMakeLists、rosidl、工作空间。', true],
    ['NOW', 'C++ / CMake', '第 8 章。节点编译、链接 OpenCV、install/export。', true],
    ['NOW', '串口 / 状态机', '第 4 章。把视觉结果变成机器人能执行的指令。', true],
    ['NEXT', 'TF2 / URDF', '坐标变换、机器人模型、手眼/相机外参。', false],
    ['NEXT', 'Nav2 / MoveIt2', '导航、机械臂规划、抓取。', false],
    ['NEXT', 'PyTorch / YOLO', '目标检测、分割、关键点；ONNX/TensorRT 部署。', false],
    ['LATER', 'SLAM / 三维视觉', 'ORB-SLAM、双目、结构光、点云配准。', false],
    ['LATER', 'MLOps / 数据闭环', '数据标注、版本、回归、线上漂移监控。', false],
  ];

  $('#app').innerHTML = `${topbar('guide')}
    <main class="page page-narrow">
      <section class="guide-hero">
        <div class="eyebrow">Learning path · 100 days</div>
        <h1>从大二开始，<br>搭一条 OpenCV + ROS2 的工程路线</h1>
        <p>100 天左右完成：前 7 周保留 OpenCV 视觉主线，后 5 周进入 ROS2 发布订阅、launch/executor、package.xml/CMake、rosidl 和 colcon。每周 10–12 小时，先跑通，再补深。</p>
        <div class="guide-meta">
          <span>32 LESSONS</span><span>10 CHAPTERS</span><span>≈ 40 HOURS</span><span>100 DAYS</span>
          <span>${health ? 'PYTHON ' + escapeHtml(health.python) + ' · OPENCV ' + escapeHtml(health.cv2) : 'LOCAL RUNTIME'}</span>
        </div>
        <div class="deco" aria-hidden="true">${brandMark(250)}</div>
      </section>

      <section class="section">
        <div class="section-head">
          <div><span class="eyebrow">100-day milestones</span><h2>100 天，先走完一遍</h2><p>不是“学完所有”，而是每个月都有一个能讲清楚的交付物。每天 2 小时：40 分钟读/跑，40 分钟自己写，20 分钟记笔记；第 12 周后留 16 天做项目和补漏。</p></div>
        </div>
        <div class="month-grid">
          <div class="month-card"><div class="mk">DAY 01–30</div><h3>Python + OpenCV</h3><ul><li>Python / NumPy / 图像数组</li><li>阈值、轮廓、透视、特征</li><li>循迹/分拣/标定</li></ul><p>交付：零件计数 + 分拣位姿表 + 标定 RMS。</p></div>
          <div class="month-card"><div class="mk">DAY 31–65</div><h3>ROS2 基础 + 进阶</h3><ul><li>pub/sub、msg/srv、remap</li><li>launch/timer、sync、executor</li><li>参数与日志</li></ul><p>交付：两个节点 + 自定义接口 + launch。</p></div>
          <div class="month-card"><div class="mk">DAY 66–100</div><h3>ROS2 工程 + 集成</h3><ul><li>package.xml / CMakeLists</li><li>rosidl 接口、colcon 工作空间</li><li>OpenCV 视觉节点</li></ul><p>交付：可 colcon build 的多包工程 + ROS2 视觉节点。</p></div>
        </div>
      </section>

      <section class="section">
        <div class="section-head">
          <div><span class="eyebrow">Schedule · 2D map</span><h2>100 天 / 12 周主线</h2><p>12 周主课约 84 天，剩余约 16 天做项目、补漏和复盘。点站点看本周课程和产出。</p></div>
          <div class="viz-tools">
            <div class="segmented" role="group" aria-label="路线图视图">
              <button data-action="guide-view" data-view="map" class="${state.guideView !== 'list' ? 'active' : ''}">路线图</button>
              <button data-action="guide-view" data-view="list" class="${state.guideView === 'list' ? 'active' : ''}">列表</button>
            </div>
          </div>
        </div>
        ${state.guideView === 'list' ? weekListHTML(weeks) : weekMapHTML(weeks)}
      </section>

      <section class="section">
        <div class="section-head">
          <div><span class="eyebrow">Read · Modify · Write</span><h2>未来更看重“读懂 + 改对”，不是只会从零写</h2><p>面试官常给你一段现有代码让你找问题、加功能。初级岗位大量时间在读代码、改配置、定位现场问题；但不会写就改不动。建议按 5:3:2 分配。</p></div>
        </div>
        <div class="month-grid">
          <div class="month-card"><div class="mk">READ · 50%</div><h3>先读懂</h3><ul><li>输入/输出、话题/接口</li><li>坐标系、单位、频率</li><li>状态机、异常路径</li></ul><p>产出：一张数据流/状态图，能用自己的话讲清主流程。</p></div>
          <div class="month-card"><div class="mk">MODIFY · 30%</div><h3>再改对</h3><ul><li>改参数/字段/话题</li><li>一次只改一处，保留 diff</li><li>跑回归 + 失败样本</li></ul><p>产出：一个可回滚的 diff + 改前/改后指标。</p></div>
          <div class="month-card"><div class="mk">WRITE · 20%</div><h3>最后写</h3><ul><li>从空白写最小节点/函数</li><li>先接口，再实现</li><li>加测试与 README</li></ul><p>产出：一个能独立运行的最小版本。</p></div>
        </div>
      </section>

      <section class="section">
        <div class="section-head">
          <div><span class="eyebrow">Two tracks</span><h2>开发型，还是调控型？</h2><p>两条路线不是二选一。先都做过，再决定你更享受「设计系统」还是「让系统稳定」。</p></div>
        </div>
        <div class="role-grid">
          ${roles.map((r) => `<div class="role-card" style="border-top:3px solid ${r.color}">
            <div class="role-tag" style="color:${r.color}">${r.tag}</div>
            <h3>${r.title}</h3>
            <p>${r.desc}</p>
            <ul>${r.items.map((i) => `<li>${i}</li>`).join('')}</ul>
          </div>`).join('')}
        </div>
      </section>

      <section class="section">
        <div class="section-head">
          <div><span class="eyebrow">Two specializations</span><h2>两条落地路线</h2><p>先把 OpenCV 视觉做扎实，再用 ROS2 把它工程化；两条线都需要“算法 + 接口 + 现场”的组合能力。</p></div>
        </div>
        <div class="role-grid">
          <div class="role-card" style="border-top:3px solid var(--blue)">
            <div class="role-tag" style="color:var(--blue)">Vision application</div>
            <h3>OpenCV 视觉应用</h3>
            <p>把检测、定位、标定、手眼和机器人接口串成一条可交付的视觉应用。</p>
            <ul><li>Blob/轮廓/特征/模板</li><li>相机标定、像素→毫米</li><li>检测结果结构化</li><li>参数、日志、现场调试</li></ul>
          </div>
          <div class="role-card" style="border-top:3px solid var(--amber)">
            <div class="role-tag" style="color:var(--amber)">ROS2 engineering</div>
            <h3>ROS2 机器人软件</h3>
            <p>把视觉/控制算法包成节点，用 launch、接口和 colcon 组织成多包工程。</p>
            <ul><li>pub/sub、msg/srv、remap</li><li>launch/timer、sync、executor</li><li>package.xml/CMake/rosidl</li><li>colcon + overlay</li></ul>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="section-head">
          <div><span class="eyebrow">Tech stack</span><h2>这门课在技术栈里的位置</h2><p>先把「经典视觉 + Python 工程」打牢，再往 ROS2、深度学习、SLAM 扩展。顺序反了，容易只会调包。</p></div>
        </div>
        <div class="stack-grid">
          ${stack.map(([tag, title, desc, now]) => `<div class="stack-item ${now ? 'now' : ''}">
            <div class="sk">${tag}</div><h4>${title}</h4><p>${desc}</p>
          </div>`).join('')}
        </div>
      </section>

      <section class="section">
        <div class="section-head">
          <div><span class="eyebrow">FAQ</span><h2>开始前，你可能想问</h2></div>
        </div>
        <div class="interview">
          <details open><summary>我数学一般，能学吗？</summary><div class="ans">能。这门课需要的数学主要是：向量、矩阵乘法、点到直线距离、atan2、PID 的直觉。遇到公式先看「它解决什么问题」，再回来补线性代数；不要停在推导上。</div></details>
          <details><summary>需要显卡 / 摄像头吗？</summary><div class="ans">不需要。所有课程都用本地合成图或示例图；有摄像头可以之后自己接 <code>cv2.VideoCapture</code>。没有 GPU 也能学完经典视觉。</div></details>
          <details><summary>为什么不用 YOLO？</summary><div class="ans">YOLO 是重要工具，但它不能替代「像素、坐标、标定、几何、评估」这些基础。真实项目里，模型只占一小段；标定、坐标变换、节拍、异常处理才是大头。学完本课再上 YOLO，你知道该把检测框接到哪里。</div></details>
          <details><summary>代码跑不出来怎么办？</summary><div class="ans">先看控制台最后一行报错和行号；再点「定位到第 N 行」。常见原因：变量名拼错、缩进不一致、滑杆参数越界、图片路径不对。先恢复初始代码跑通，再逐段改。</div></details>
          <details><summary>学完能做什么岗位？</summary><div class="ans">可以投视觉算法助理、机器人软件/应用工程师、视觉调试/FAE、自动化集成等初级岗位。作品集比证书重要：把循迹、分拣、缺陷检测三个项目做完整，能讲清指标和失败案例。</div></details>
          <details><summary>能在平板 / 手机上用吗？</summary><div class="ans">可以。平板通过同一 Wi-Fi 访问电脑上的服务：双击 <code>start_tablet.bat</code>，再在平板浏览器打开页面左下角「平板访问」里显示的地址。Python/OpenCV 仍在电脑上运行，平板负责显示、写代码和点运行；建议配蓝牙键盘，写代码更舒服。局域网模式只建议在可信 Wi-Fi 使用。</div></details>
          <details><summary>ROS2 需要装什么？</summary><div class="ans">推荐 Ubuntu 22.04 + ROS2 Humble（或 24.04 + Jazzy），Windows 可用 WSL2。本软件的 ROS2 课程用纯 Python 模拟发布/订阅、launch、同步、参数和构建逻辑；rclpy/C++ 代码块标注为只读，真实编译要在 ROS2 环境里把代码复制到工作空间。</div></details>
          <details><summary>没有 ROS2 环境能学吗？</summary><div class="ans">能。先把节点、话题、msg/srv、launch、executor、package.xml/CMake 的概念跑通；等装好 ROS2 再练 <code>colcon build</code> 和 <code>ros2 run</code>。不要一开始就装一堆插件，先把一个包编过。</div></details>
        </div>
      </section>
      ${pageFooter()}
    </main>`;
}

/* --------------------------------------------------------------------------
   8. Skills page
   -------------------------------------------------------------------------- */

function renderSkills() {
  const skills = [
    { name: 'Python 编程', short: 'Python', ids: ['py-first-run', 'py-types', 'py-list-dict', 'py-functions', 'py-class-json'], dev: '写脚本、日志解析、配置、API', tune: '读日志、改参数、复现问题', evidence: '一个能读串口日志的 Python 工具', x: 82, y: 32, size: 96, color: 'var(--blue)' },
    { name: 'NumPy / 图像数组', short: 'NumPy', ids: ['np-array', 'cv-image-array'], dev: '实现图像预处理、向量化', tune: '判断分辨率/通道/ROI 问题', evidence: 'ROI 裁剪与通道拆分脚本', x: 64, y: 20, size: 82, color: 'var(--accent)' },
    { name: '颜色与阈值', short: '颜色', ids: ['cv-color-hsv', 'cv-threshold-edge'], dev: '设计分割模块、参数配置化', tune: '调 HSV/阈值/形态学', evidence: '分拣站颜色检测报告', x: 30, y: 78, size: 86, color: 'var(--accent)' },
    { name: '轮廓与几何', short: '轮廓', ids: ['cv-contour-shape', 'cv-perspective'], dev: '尺寸测量、形状筛选、透视校正', tune: '判断粘连/漏检/角点错', evidence: '零件计数与尺寸测量', x: 46, y: 64, size: 86, color: 'var(--accent)' },
    { name: '特征与定位', short: '定位', ids: ['cv-template-orb'], dev: '模板/ORB/单应性定位', tune: '判断纹理不足、误匹配', evidence: 'PCB/零件定位 demo', x: 84, y: 50, size: 82, color: 'var(--accent)' },
    { name: '相机标定', short: '标定', ids: ['robot-calib'], dev: '标定工具、参数版本管理', tune: '复标、检查 RMS/畸变', evidence: '标定报告（K/dist/RMS）', x: 42, y: 90, size: 80, color: 'var(--amber)' },
    { name: '视觉伺服', short: '伺服', ids: ['robot-line', 'robot-aruco', 'robot-flow'], dev: '误差→控制指令、滤波', tune: '整定 PID、对接成功率', evidence: '循迹/对接视频与曲线', x: 78, y: 84, size: 94, color: 'var(--amber)' },
    { name: '通信协议', short: '串口', ids: ['ctrl-serial'], dev: '帧格式、CRC、解析库', tune: '抓包、判断丢包/CRC/波特率', evidence: '串口协议文档 + 抓包记录', x: 92, y: 64, size: 82, color: 'var(--violet)' },
    { name: '状态机 / 异常', short: '状态机', ids: ['ctrl-state'], dev: '状态设计、超时、恢复', tune: '看日志定位卡点', evidence: '分拣站状态图与日志', x: 62, y: 88, size: 84, color: 'var(--violet)' },
    { name: '评估与测试', short: '评估', ids: ['eng-debug'], dev: '数据集、P/R、回归测试', tune: '误检/漏检分析、阈值取舍', evidence: '缺陷检测评估表', x: 92, y: 40, size: 82, color: 'var(--violet)' },
    { name: '系统集成', short: '集成', ids: ['capstone-cell'], dev: '接口、节拍、交付', tune: '现场标定、布局、验收', evidence: '2 页项目报告 + 演示', x: 66, y: 70, size: 80, color: 'var(--rose)' },
    { name: 'ROS2 通信', short: 'ROS2', ids: ['ros2-pubsub', 'ros2-msg-srv', 'ros2-remap-namespace'], dev: '节点、话题、msg/srv、namespace', tune: 'QoS、remap、多机隔离', evidence: '两个可通信节点 + 自定义接口', x: 22, y: 54, size: 94, color: 'var(--blue)' },
    { name: 'ROS2 进阶', short: '进阶', ids: ['ros2-launch-timer', 'ros2-sync-executor', 'ros2-params-logging'], dev: 'launch、timer、executor、参数', tune: '同步、回调组、日志排查', evidence: 'launch + 同步 + 参数 YAML', x: 50, y: 38, size: 88, color: 'var(--violet)' },
    { name: 'ROS2 工程', short: '工程', ids: ['ros2-package-cmake', 'ros2-rosidl', 'ros2-colcon-workspace', 'ros2-vision-node'], dev: 'ament_cmake、rosidl、colcon、视觉节点', tune: '依赖/链接/overlay 排错', evidence: '可 colcon build 的多包工程', x: 93, y: 80, size: 96, color: 'var(--rose)' },
  ];
  state.skillData = skills;
  if (typeof state.skillIndex !== 'number' || state.skillIndex < 0 || state.skillIndex >= skills.length) {
    state.skillIndex = 6;
  }
  const questions = [
    ['HSV 里 H 为什么是 0–180？红色怎么处理？', 'OpenCV 把 0–360° 压到 0–180，节省一个字节。红色横跨 0° 和 360°，所以用 [0,10] 和 [170,180] 两段掩膜再按位或。'],
    ['Otsu 的假设是什么？什么时候失效？', '假设灰度直方图是双峰的，前景/背景各一峰；找类间方差最大的切点。单峰、渐变光照、大面积阴影时失效，改用自适应阈值或分区。'],
    ['Canny 的四步？高低阈值怎么调？', '高斯平滑 → Sobel 梯度 → 非极大值抑制 → 双阈值连接。低阈值负责接上弱边缘，高阈值保证强边缘；通常从 1:2 到 1:3 开始，按漏检/误检调。'],
    ['单应矩阵需要几对点？和仿射有什么区别？', '4 对点，8 个自由度。仿射 6 个自由度，保证平行线仍平行；单应处理透视，平行线可以相交于消失点。'],
    ['模板匹配什么时候会失败？', '旋转、缩放、遮挡、光照变化、重复纹理。分数高也不代表对，必须看位置和业务约束；旋转场景用 ORB/深度学习特征。'],
    ['像素怎么变成毫米？', '用四个已知点求单应矩阵，把像素齐次坐标乘 H 再除以 w；或者用标定 + 深度。比例尺只在相机正对平面且距离固定时成立。'],
    ['ArUco 的距离为什么不准？', '内参错、marker_size 单位错、标记太小/太斜/太靠边缘、运动模糊。先检查 K 和单位，再看角点质量。'],
    ['PID 三个参数分别解决什么？', 'P 让误差产生动作；I 消稳态误差但会 windup；D 抑制超调但对噪声敏感。先 P，再加 D，最后很小的 I，每次只改一个。'],
    ['串口为什么会丢帧？', '波特率不匹配、接线/地线、缓冲区溢出、没有帧头/长度、坏 CRC、一次 read 不是一帧。解析器要处理分包、粘包和重新同步。'],
    ['误检率 3% 怎么排查？', '先固定数据集和基线，分开看 precision/recall；再看失败样本（光照、反光、材料、折痕）；最后才调阈值/换算法。不要凭感觉改。'],
  ];
  const portfolio = [
    '循迹小车：一段视频 + 误差/转向曲线，说明 Kp/Ki/Kd 怎么整定。',
    '颜色分拣：一张标注图 + 毫米坐标表 + 抓取顺序，说明标定误差。',
    '缺陷检测：P/R/F1、耗时、失败样本，说明为什么选这个工作点。',
    '结课项目：2 页报告（架构、接口、节拍、指标、风险）+ 2 分钟演示。',
    '一份 README：怎么运行、依赖、目录、已知限制。',
  ];

  $('#app').innerHTML = `${topbar('skills')}
    <main class="page page-narrow">
      <section class="guide-hero">
        <div class="eyebrow">Skill map · Career</div>
        <h1>你会什么，<br>比你会多少 API 更重要</h1>
        <p>下面把课程、岗位用法和作品集证据对齐。面试时，不要只说「学过 OpenCV」，要说「我用单应性把像素映射到工作台，误差 2 mm，节拍 24 秒，失败样本是反光」。</p>
        <div class="guide-meta"><span>14 SKILLS</span><span>2 ROLE PATHS</span><span>10 INTERVIEW QUESTIONS</span></div>
        <div class="deco" aria-hidden="true">${icon('target', 260)}</div>
      </section>

      <section class="section">
        <div class="section-head">
          <div><span class="eyebrow">Matrix · 2D map</span><h2>技能 × 课程 × 岗位</h2><p>横轴偏开发，纵轴偏调控；气泡越大，课程覆盖越多。位置表示学习侧重，不是精确评分；点气泡看证据。</p></div>
          <div class="viz-tools">
            <div class="segmented" role="group" aria-label="技能视图">
              <button data-action="skills-view" data-view="map" class="${state.skillsView !== 'table' ? 'active' : ''}">二维图</button>
              <button data-action="skills-view" data-view="table" class="${state.skillsView === 'table' ? 'active' : ''}">表格</button>
            </div>
          </div>
        </div>
        ${state.skillsView === 'table' ? skillTableHTML(skills) : skillMapHTML(skills)}
      </section>

      <section class="section">
        <div class="section-head"><div><span class="eyebrow">Interview</span><h2>10 个问题，检验是否真的理解</h2><p>先自己回答，再展开对照。答案不要求一字不差，但要能说清「为什么」。</p></div></div>
        <div class="interview">
          ${questions.map(([q, a]) => `<details><summary>${q}</summary><div class="ans">${a}</div></details>`).join('')}
        </div>
      </section>

      <section class="section">
        <div class="section-head"><div><span class="eyebrow">Portfolio</span><h2>作品集清单</h2><p>没有项目，就先从这三个小项目开始；每个都能在一周内做完。</p></div></div>
        <div class="checklist">
          ${portfolio.map((item) => `<div class="item">${item}</div>`).join('')}
        </div>
      </section>

      <section class="section">
        <div class="section-head"><div><span class="eyebrow">Next</span><h2>学完之后，往哪里走</h2></div></div>
        <div class="stack-grid">
          <div class="stack-item now"><div class="sk">01</div><h4>接 ROS2</h4><p>把检测节点发布成 topic，用 TF 管理相机/底盘/工具坐标，写 launch 和参数文件。</p></div>
          <div class="stack-item"><div class="sk">02</div><h4>上深度学习</h4><p>YOLO 做检测/分割，关键点做抓取；学 ONNX/TensorRT 部署和量化。</p></div>
          <div class="stack-item"><div class="sk">03</div><h4>做手眼标定</h4><p>eye-in-hand / eye-to-hand，把像素坐标接到机械臂末端；做抓取闭环。</p></div>
          <div class="stack-item"><div class="sk">04</div><h4>补 C++</h4><p>实时性、内存、线程；把 Python 原型迁到 C++/ROS2 节点。</p></div>
          <div class="stack-item"><div class="sk">05</div><h4>做数据闭环</h4><p>采集、标注、训练、评估、上线、漂移监控；这是量产团队的核心能力。</p></div>
          <div class="stack-item"><div class="sk">06</div><h4>去现场</h4><p>看真实产线的光照、节拍、误检、急停；很多问题不在算法，在工艺和结构。</p></div>
        </div>
      </section>
      ${pageFooter()}
    </main>`;
}

/* --------------------------------------------------------------------------
   9. Lesson page
   -------------------------------------------------------------------------- */

function renderBlocks(blocks) {
  return (blocks || []).map((b) => {
    if (b.t === 'p') return `<p>${inline(b.x)}</p>`;
    if (b.t === 'h') return `<h3>${inline(b.x)}</h3>`;
    if (b.t === 'ul') return `<ul>${(b.x || []).map((i) => `<li>${inline(i)}</li>`).join('')}</ul>`;
    if (b.t === 'ol') return `<ol>${(b.x || []).map((i) => `<li>${inline(i)}</li>`).join('')}</ol>`;
    if (b.t === 'note') {
      const tone = b.tone || 'info';
      return `<div class="callout ${tone}"><div class="ct">${tone === 'warn' ? icon('alert', 14) : tone === 'tip' ? icon('light', 14) : icon('target', 14)} ${inline(b.title || '提示')}</div><p>${inline(b.x)}</p></div>`;
    }
    if (b.t === 'formula') {
      return `<div class="formula">${escapeHtml(b.x)}${b.label ? `<small>${escapeHtml(b.label)}</small>` : ''}</div>`;
    }
    if (b.t === 'code') {
      if (b.lang === 'halcon') {
        return `<div class="concept-code is-halcon"><div class="code-lang">HALCON · HDevelop（只读）</div><pre>${highlightHalcon(b.x)}</pre></div>`;
      }
      if (b.lang && b.lang !== 'python') {
        const labels = { cpp: 'C++', xml: 'XML', cmake: 'CMake', bash: 'Shell', text: '接口定义' };
        return `<div class="concept-code is-code"><div class="code-lang">${labels[b.lang] || b.lang.toUpperCase()}（只读）</div><pre>${escapeHtml(b.x)}</pre></div>`;
      }
      return `<pre>${highlightPython(b.x)}</pre>`;
    }
    if (b.t === 'table') {
      const head = (b.head || []).map((h) => `<th>${inline(h)}</th>`).join('');
      const rows = (b.rows || []).map((row) => `<tr>${row.map((c) => `<td>${inline(c)}</td>`).join('')}</tr>`).join('');
      return `<table><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table>`;
    }
    return '';
  }).join('');
}

function renderWalkthrough(lesson) {
  if (!lesson.walkthrough || !lesson.walkthrough.length) return '';
  return `<section class="walk-section" id="walkthrough">
    <div class="walk-head">
      <div><span class="eyebrow">Code walkthrough</span><h2>代码逐段讲解</h2><p>下面每段代码都在右侧编辑器里，按顺序拼成完整程序。先读，再跑，再改。</p></div>
      <span class="badge">${lesson.walkthrough.length} 段</span>
    </div>
    ${lesson.walkthrough.map((seg, i) => `<article class="walk-card">
      <div class="walk-top"><span class="walk-no">${String(i + 1).padStart(2, '0')}</span><h3>${escapeHtml(seg.title)}</h3></div>
      <div class="code-wrap">
        <button class="copy" data-action="copy-seg" data-seg="${i}" title="复制这段代码">${icon('copy', 12)} 复制</button>
        <pre>${highlightPython(seg.code)}</pre>
      </div>
      <div class="walk-explain">${inline(seg.explain)}</div>
      ${seg.tip ? `<div class="walk-tip">${inline(seg.tip)}</div>` : ''}
    </article>`).join('')}
  </section>`;
}

function renderTasks(lesson) {
  if (!lesson.tasks || !lesson.tasks.length) return '';
  const p = lessonProgress(lesson.id);
  return `<section class="tasks">
    <div class="walk-head"><div><span class="eyebrow">Practice</span><h2>动手任务</h2><p>开发型任务练实现，调控型任务练判断。勾选后进度会保存。</p></div></div>
    <div class="task-list">
      ${lesson.tasks.map((t, i) => {
        const done = p.tasks.includes(i);
        const kind = t.kind === 'dev' ? '开发' : t.kind === 'tune' ? '调控' : '观察';
        return `<label class="task ${done ? 'done' : ''}">
          <input type="checkbox" data-task="${i}" ${done ? 'checked' : ''}>
          <span class="task-check">${icon('check', 12)}</span>
          <span class="task-body">
            <span class="task-title">${escapeHtml(t.title)} <span class="kind ${t.kind}">${kind}</span></span>
            <span class="task-detail">${inline(t.detail)}</span>
          </span>
        </label>`;
      }).join('')}
    </div>
  </section>`;
}

function renderScratchCTA(lesson) {
  const task = (lesson.tasks || []).find((t) => t.kind === 'dev') || (lesson.tasks || [])[0];
  const title = task ? task.title : '用本课知识完成一个小任务';
  return `<section class="scratch-cta">
    <div class="scratch-cta-copy">
      <div class="eyebrow">Your turn</div>
      <h3>轮到你了：自己写一遍</h3>
      <p>${inline(title)}。打开「我的代码」空白区，从零写、随便改；这里没有标准答案，也不会覆盖课程代码。</p>
    </div>
    <button class="btn btn-primary" data-action="open-scratch">${icon('code', 16)} 打开我的代码</button>
  </section>`;
}

function renderQuiz(lesson) {
  if (!lesson.quiz || !lesson.quiz.length) return '';
  const p = lessonProgress(lesson.id);
  const answered = Object.keys(p.quiz || {}).length;
  const correct = lesson.quiz.filter((q, i) => p.quiz[i] === q.answer).length;
  return `<section class="quiz">
    <div class="walk-head"><div><span class="eyebrow">Check yourself</span><h2>小测</h2><p>选一个答案，立刻看解释。答错可以重选，直到能讲清原因。</p></div><span class="badge ${correct === lesson.quiz.length ? 'green' : ''}">${correct}/${lesson.quiz.length}</span></div>
    ${lesson.quiz.map((q, qi) => {
      const chosen = p.quiz[qi];
      const has = chosen !== undefined;
      return `<div class="quiz-card ${has ? 'answered' : ''}" data-qcard="${qi}">
        <div class="quiz-q"><span class="qn">Q${qi + 1}</span><span>${inline(q.q)}</span></div>
        <div class="quiz-options">
          ${q.options.map((opt, oi) => {
            let cls = '';
            if (has && oi === q.answer) cls = 'correct';
            if (has && oi === chosen && oi !== q.answer) cls = 'wrong';
            return `<button class="quiz-opt ${cls}" data-quiz-q="${qi}" data-quiz-o="${oi}">
              <span class="letter">${String.fromCharCode(65 + oi)}</span><span>${inline(opt)}</span>
            </button>`;
          }).join('')}
        </div>
        <div class="quiz-why"><strong style="color:var(--text)">为什么：</strong>${inline(q.why)}</div>
      </div>`;
    }).join('')}
  </section>`;
}

function courseNav(lesson) {
  const ch = chapterOf(lesson);
  const chapterLessons = ch ? ch.lessons : [];
  const done = chapterLessons.filter((l) => lessonProgress(l.id).completed).length;
  const pct = chapterLessons.length ? Math.round((done / chapterLessons.length) * 100) : 0;
  return `<aside class="course-nav" aria-label="课程目录">
    <a class="nav-back" href="#/">${icon('left', 14)} 返回课程地图</a>
    <div>
      <div class="nav-chapter">CHAPTER ${escapeHtml(ch ? ch.number : '')} · ${escapeHtml(ch ? ch.title : '')}</div>
      <div class="nav-title">${escapeHtml(lesson.title)}</div>
    </div>
    <div class="nav-progress"><span>本章</span><div class="bar"><i id="navBar" style="width:${pct}%"></i></div><b id="navPct" class="mono" style="font-size:10px;color:var(--muted)">${pct}%</b></div>
    <div class="nav-list">
      ${chapterLessons.map((l) => {
        const p = lessonProgress(l.id);
        return `<a class="nav-item ${l.id === lesson.id ? 'active' : ''}" data-lesson="${l.id}" href="#/lesson/${l.id}">
          <span class="n">${String(lessonGlobalIndex(l)).padStart(2, '0')}</span>
          <span class="status-dot ${p.completed ? 'done' : ''}"></span>
          <span class="t">${escapeHtml(l.title)}</span>
        </a>`;
      }).join('')}
    </div>
    <div class="nav-foot">${state.lessons.length} 节课 · ${percentComplete()}% 完成<br>Ctrl + Enter 运行代码</div>
  </aside>`;
}

function paramsHTML(lesson) {
  if (!lesson.params || !lesson.params.length) return '';
  return `<div class="lab-params open" id="paramsBox">
    ${lesson.params.map((p) => `<div class="param">
      <label>${escapeHtml(p.label)}${p.unit ? ` <span class="dim">(${escapeHtml(p.unit)})</span>` : ''}</label>
      <output id="pv-${p.key}">${p.value}${p.unit || ''}</output>
      <input type="range" data-param="${p.key}" min="${p.min}" max="${p.max}" step="${p.step}" value="${p.value}" aria-label="${escapeHtml(p.label)}">
      ${p.hint ? `<span class="hint">${inline(p.hint)}</span>` : ''}
    </div>`).join('')}
  </div>`;
}

function labHTML(lesson) {
  const target = lesson.target;
  return `<aside class="lab-panel" id="lab">
    <div class="lab">
      <div class="lab-head">
        <div class="mode-switch" role="group" aria-label="学习模式">
          <button data-mode="dev" class="active" title="课程示例代码">跟学</button>
          <button data-mode="scratch" title="我自己的空白练习区">自己写</button>
          <button data-mode="tune" title="锁定代码，只调参数">调控</button>
        </div>
        <span class="lab-file" id="labFile"><i></i> lesson.py</span>
        <div class="lab-actions">
          <button class="icon-btn" data-action="reset-code" title="恢复初始代码" aria-label="恢复初始代码">${icon('reset', 15)}</button>
          <button class="icon-btn" data-action="download-code" title="下载 .py" aria-label="下载代码">${icon('download', 15)}</button>
        </div>
      </div>
      <div class="scratch-note" id="scratchNote" hidden>
        <span class="badge amber">我的代码</span>
        <span>空白练习区：不会影响课程代码和判题，写错也没关系。</span>
      </div>
      <div class="editor-shell">
        <div class="gutter" id="gutter" aria-hidden="true"></div>
        <div class="editor-area">
          <pre id="highlight" aria-hidden="true"></pre>
          <textarea id="code" spellcheck="false" autocapitalize="off" autocomplete="off" aria-label="Python 代码编辑器"></textarea>
        </div>
      </div>
      <div class="runbar">
        <button class="run-btn" id="runBtn">${icon('play', 15)}<span id="runLabel">运行代码</span></button>
        <span class="run-meta">Ctrl + Enter</span>
        <span class="target-pill" id="targetPill" title="${target ? escapeHtml(target.label) : ''}">${target ? '目标 · ' + escapeHtml(target.label) : '自动检查'}</span>
      </div>
      <div class="output">
        <div class="out-tabs" id="outTabs">${outputTabs(null)}</div>
        <div class="out-body" id="outBody">${emptyOutput()}</div>
        <div class="run-status" id="runStatus"><span class="dot"></span><span>尚未运行</span></div>
      </div>
      ${paramsHTML(lesson)}
    </div>
  </aside>`;
}

function outputTabs(data) {
  const counts = data ? {
    console: (data.stdout || data.stderr || data.error) ? 1 : 0,
    images: (data.outputs || []).length + (data.original_url ? 1 : 0),
    metrics: Object.keys(data.metrics || {}).length,
    checks: (data.checks || []).length,
  } : { console: 0, images: 0, metrics: 0, checks: 0 };
  const tabs = [
    ['console', '控制台', 'terminal'],
    ['images', '图像', 'image'],
    ['metrics', '指标', 'gauge'],
    ['checks', '判题', 'checks'],
  ];
  return tabs.map(([key, label, ic]) => `<button class="out-tab ${state.outTab === key ? 'active' : ''}" data-out-tab="${key}">
    ${icon(ic, 13)} ${label}${counts[key] ? `<span class="count">${counts[key]}</span>` : ''}
  </button>`).join('');
}

function emptyOutput() {
  return `<div class="empty">${icon('terminal', 28)}<b>运行后在这里看结果</b><span>控制台 · 图像 · 指标 · 自动检查</span></div>`;
}

function renderLesson(id) {
  const lesson = state.byId[id];
  if (!lesson) {
    $('#app').innerHTML = `${topbar('map')}<main class="page"><div class="empty" style="min-height:50vh"><b>课程不存在</b><span>回到课程地图重新选择</span><a class="btn btn-sm" href="#/">返回地图</a></div></main>`;
    return;
  }
  state.currentId = id;
  state.lastRun = null;
  state.mode = 'dev';
  state.outTab = 'console';
  state.params = {};
  (lesson.params || []).forEach((p) => { state.params[p.key] = p.value; });

  const ch = chapterOf(lesson);
  const index = lessonGlobalIndex(lesson);
  const p = lessonProgress(lesson.id);
  const diff = Math.max(1, Math.min(5, lesson.difficulty || 1));
  const prev = state.lessons[index - 2];
  const next = state.lessons[index];

  $('#app').innerHTML = `${topbar('map')}
    <div class="lesson-layout">
      ${courseNav(lesson)}
      <main class="lesson-main">
        <div class="mobile-course">
          <select id="mobileLessonSelect" aria-label="选择课程">
            ${state.chapters.map((c) => `<optgroup label="${escapeHtml(c.title)}">${c.lessons.map((l) => `<option value="${l.id}" ${l.id === lesson.id ? 'selected' : ''}>${String(lessonGlobalIndex(l)).padStart(2, '0')} ${escapeHtml(l.title)}</option>`).join('')}</optgroup>`).join('')}
          </select>
        </div>
        <header class="lesson-hero">
          <div class="crumbs"><a href="#/">课程地图</a><span>/</span><span>${escapeHtml(ch ? ch.title : '')}</span><span>/</span><span>${String(index).padStart(2, '0')}</span></div>
          <h1>${escapeHtml(lesson.title)}</h1>
          <p class="lesson-sub">${escapeHtml(lesson.subtitle)}</p>
          <div class="meta-row">
            <span class="badge blue">${lesson.mode === 'vision' ? '视觉实验' : 'Python 实验'}</span>
            <span class="badge">${lesson.minutes} 分钟</span>
            <span class="badge">第 ${index} / ${state.lessons.length} 课</span>
            <span class="difficulty" title="难度 ${diff}/5">${[1, 2, 3, 4, 5].map((n) => `<i class="${n <= diff ? 'on' : ''}"></i>`).join('')}</span>
            ${(lesson.tags || []).map((t) => `<span class="badge">${escapeHtml(t)}</span>`).join('')}
            ${p.completed ? `<span class="badge green">${icon('check', 11)} 已完成</span>` : ''}
            <button class="btn btn-sm" data-action="open-scratch" style="margin-left:auto">${icon('code', 14)} 自己写</button>
          </div>
          <div class="objectives">
            <h4>你将学会</h4>
            <ul>${(lesson.objectives || []).map((o) => `<li>${inline(o)}</li>`).join('')}</ul>
          </div>
        </header>

        <div class="lesson-body">
          <article class="lesson-content">
            <div class="prose">${renderBlocks(lesson.concept)}</div>
            ${renderWalkthrough(lesson)}
            <div class="insight-grid">
              <div class="insight"><div class="tag">Industry</div><h4>现实里怎么用</h4><p>${inline(lesson.industry || '')}</p></div>
              <div class="insight career"><div class="tag">Career</div><h4>开发型 / 调控型</h4><p>${inline(lesson.career || '')}</p></div>
            </div>
            ${renderTasks(lesson)}
            ${renderScratchCTA(lesson)}
            ${renderQuiz(lesson)}
            <div class="lesson-foot">
              <button class="btn complete-btn ${p.completed ? 'done' : ''}" id="completeBtn" data-action="toggle-complete">${p.completed ? icon('check', 16) + ' 已完成' : icon('check', 16) + ' 标记完成'}</button>
              <div class="nav-btns">
                ${prev ? `<a class="btn btn-sm" href="#/lesson/${prev.id}">${icon('left', 14)} 上一课</a>` : ''}
                ${next ? `<a class="btn btn-sm" href="#/lesson/${next.id}">下一课 ${icon('right', 14)}</a>` : ''}
              </div>
            </div>
          </article>
          ${labHTML(lesson)}
        </div>
      </main>
    </div>
    ${pageFooter()}`;

  setupLesson(lesson);
}

function setupLesson(lesson) {
  const ta = $('#code');
  const pre = $('#highlight');
  const gutter = $('#gutter');
  if (!ta || !pre || !gutter) return;

  ta.value = getDraft(lesson);

  function paint() {
    const code = ta.value;
    pre.innerHTML = highlightPython(code) + '\n';
    const lines = code.split('\n').length;
    let html = '';
    for (let i = 1; i <= Math.max(lines, 1); i++) html += `<div>${i}</div>`;
    gutter.innerHTML = html;
    syncScroll();
  }
  function syncScroll() {
    pre.scrollTop = ta.scrollTop;
    pre.scrollLeft = ta.scrollLeft;
    gutter.scrollTop = ta.scrollTop;
  }

  paint();
  ta.addEventListener('input', () => {
    paint();
    saveEditorDebounced(lesson.id, state.mode, ta.value);
  });
  ta.addEventListener('scroll', syncScroll);
  ta.addEventListener('keydown', (event) => {
    if (event.key === 'Tab') {
      event.preventDefault();
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      ta.value = ta.value.slice(0, start) + '    ' + ta.value.slice(end);
      ta.selectionStart = ta.selectionEnd = start + 4;
      paint();
      saveEditorDebounced(lesson.id, state.mode, ta.value);
    }
    if (event.key === 'Enter') {
      const start = ta.selectionStart;
      const before = ta.value.slice(0, start);
      const line = before.split('\n').pop();
      const indent = (line.match(/^\s*/) || [''])[0];
      const extra = line.trim().endsWith(':') ? '    ' : '';
      if (indent || extra) {
        event.preventDefault();
        const insert = '\n' + indent + extra;
        ta.value = ta.value.slice(0, start) + insert + ta.value.slice(ta.selectionEnd);
        ta.selectionStart = ta.selectionEnd = start + insert.length;
        paint();
        saveEditorDebounced(lesson.id, state.mode, ta.value);
      }
    }
  });

  document.querySelectorAll('[data-mode]').forEach((btn) => {
    btn.addEventListener('click', () => setMode(btn.dataset.mode));
  });

  $('#runBtn').addEventListener('click', runCode);
  const select = $('#mobileLessonSelect');
  if (select) select.addEventListener('change', () => { location.hash = '#/lesson/' + select.value; });

  document.querySelectorAll('[data-param]').forEach((range) => {
    const key = range.dataset.param;
    const output = document.getElementById('pv-' + key);
    const p = (lesson.params || []).find((x) => x.key === key);
    range.addEventListener('input', () => {
      state.params[key] = parseFloat(range.value);
      if (output) output.textContent = range.value + (p && p.unit ? p.unit : '');
      updateTargetPill(state.lastRun);
    });
  });

  document.querySelectorAll('[data-task]').forEach((input) => {
    input.addEventListener('change', () => {
      const idx = Number(input.dataset.task);
      const p = lessonProgress(lesson.id);
      const set = new Set(p.tasks);
      if (input.checked) set.add(idx); else set.delete(idx);
      updateProgress(lesson.id, { tasks: Array.from(set).sort((a, b) => a - b) });
      input.closest('.task').classList.toggle('done', input.checked);
    });
  });

  document.querySelectorAll('[data-quiz-q]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const qi = Number(btn.dataset.quizQ);
      const oi = Number(btn.dataset.quizO);
      const p = lessonProgress(lesson.id);
      p.quiz[qi] = oi;
      updateProgress(lesson.id, { quiz: p.quiz });
      renderQuizState(lesson);
    });
  });

  $('#outTabs').addEventListener('click', (event) => {
    const tab = event.target.closest('[data-out-tab]');
    if (!tab) return;
    state.outTab = tab.dataset.outTab;
    renderOutput();
  });

  setMode('dev');
  updateTargetPill(null);
}

function updateRunButton() {
  const btn = $('#runBtn');
  if (!btn || btn.classList.contains('running')) return;
  const labels = { dev: '运行代码', scratch: '运行我的代码', tune: '运行参数' };
  btn.innerHTML = `${icon('play', 15)}<span id="runLabel">${labels[state.mode] || '运行代码'}</span>`;
}

function setMode(mode) {
  const lesson = currentLesson();
  const box = document.querySelector('#lab .lab');
  const ta = $('#code');
  if (!lesson || !box || !ta) return;
  const same = state.mode === mode;

  if (!same) saveEditorImmediate();
  state.mode = mode;

  if (!same) {
    ta.value = mode === 'scratch' ? getScratch(lesson) : getDraft(lesson);
    ta.dispatchEvent(new Event('input'));
  }

  ta.readOnly = mode === 'tune';
  box.classList.toggle('tune', mode === 'tune');
  box.classList.toggle('scratch', mode === 'scratch');
  const file = $('#labFile');
  if (file) file.innerHTML = `<i></i> ${mode === 'scratch' ? 'my_code.py' : 'lesson.py'}`;
  const note = $('#scratchNote');
  if (note) note.hidden = mode !== 'scratch';
  document.querySelectorAll('[data-mode]').forEach((b) => b.classList.toggle('active', b.dataset.mode === mode));
  updateRunButton();

  const pill = $('#targetPill');
  if (pill && mode === 'scratch') {
    pill.className = 'target-pill';
    pill.textContent = '练习模式 · 无判题';
    pill.title = '自由练习没有自动判题，自己对照任务检查';
  } else {
    updateTargetPill(null);
  }

  if (!same) {
    state.lastRun = null;
    state.runMode = mode === 'scratch' ? 'scratch' : 'lesson';
    state.outTab = 'console';
    renderOutput();
    setRunStatus(null, null);
    if (mode === 'tune') {
      const params = $('#paramsBox');
      if (params) params.classList.add('open');
      toast('调控模式：代码已锁定，拖动参数后重新运行', 'info', 2600);
    } else if (mode === 'scratch') {
      toast('已切到「我的代码」：空白练习区，不会影响课程代码', 'info', 2600);
    }
  }
}

function renderQuizState(lesson) {
  const p = lessonProgress(lesson.id);
  const correct = lesson.quiz.filter((q, i) => p.quiz[i] === q.answer).length;
  const badge = document.querySelector('.quiz .badge');
  if (badge) {
    badge.textContent = `${correct}/${lesson.quiz.length}`;
    badge.classList.toggle('green', correct === lesson.quiz.length);
  }
  lesson.quiz.forEach((q, qi) => {
    const card = document.querySelector(`[data-qcard="${qi}"]`);
    if (!card) return;
    const chosen = p.quiz[qi];
    card.classList.toggle('answered', chosen !== undefined);
    card.querySelectorAll('[data-quiz-o]').forEach((btn) => {
      const oi = Number(btn.dataset.quizO);
      btn.classList.toggle('correct', chosen !== undefined && oi === q.answer);
      btn.classList.toggle('wrong', chosen !== undefined && oi === chosen && oi !== q.answer);
    });
  });
}

/* --------------------------------------------------------------------------
   10. Run & outputs
   -------------------------------------------------------------------------- */

async function runCode() {
  const lesson = currentLesson();
  if (!lesson || state.runBusy) return;
  const ta = $('#code');
  const code = ta ? ta.value : '';
  if (!code.trim()) { toast('代码是空的', 'bad'); return; }
  const isScratch = state.mode === 'scratch';

  state.runBusy = true;
  const btn = $('#runBtn');
  if (btn) {
    btn.classList.add('running');
    btn.innerHTML = `<span class="spin"></span><span>运行中…</span>`;
  }
  state.outTab = 'console';
  renderOutput();

  try {
    const response = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code,
        lesson_id: lesson.id,
        params: state.params,
        mode: isScratch ? 'scratch' : 'lesson',
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || '运行失败');
    state.lastRun = data;
    if (isScratch) applyScratchResult(lesson, data);
    else applyRunResult(lesson, data);
  } catch (err) {
    state.lastRun = {
      ok: false,
      error: String(err.message || err),
      stdout: '',
      stderr: '',
      metrics: {},
      outputs: [],
      checks: [],
    };
    state.runMode = isScratch ? 'scratch' : 'lesson';
    state.outTab = 'console';
    renderOutput();
    setRunStatus(false, null);
    toast('运行失败：' + (err.message || err), 'bad', 5000);
  } finally {
    state.runBusy = false;
    if (btn) btn.classList.remove('running');
    updateRunButton();
  }
}

function applyRunResult(lesson, data) {
  state.runMode = 'lesson';
  const checks = data.checks || [];
  const allPassed = checks.length > 0 && checks.every((c) => c.passed);
  const p = lessonProgress(lesson.id);
  const checkMap = { ...p.checks };
  checks.forEach((c) => { checkMap[c.name] = !!c.passed; });
  const completed = p.completed || (data.ok && (checks.length ? allPassed : true));
  updateProgress(lesson.id, { checks: checkMap, completed });

  if (data.ok && checks.length && allPassed) {
    const evaluated = evaluateTarget(lesson, data);
    if (evaluated && !evaluated.hit) {
      toast('检查通过；调控挑战还没达标，试试在「调控」模式里调整参数', 'info', 4200);
    } else {
      toast('运行成功，本课完成！', 'ok', 3000);
    }
  } else if (data.ok) {
    toast(checks.length ? '运行成功，还有检查未通过' : '运行成功', checks.length ? 'info' : 'ok');
  } else {
    toast('代码报错，查看控制台', 'bad', 4200);
  }

  if (!data.ok || data.error) state.outTab = 'console';
  else if ((data.outputs || []).length) state.outTab = 'images';
  else state.outTab = 'console';

  renderOutput();
  setRunStatus(data.ok, data);
  updateTargetPill(data);
  refreshChrome();
}

function applyScratchResult(lesson, data) {
  state.runMode = 'scratch';
  if (!data.ok || data.error) state.outTab = 'console';
  else if ((data.outputs || []).length) state.outTab = 'images';
  else state.outTab = 'console';
  renderOutput();
  setRunStatus(data.ok, data);
  updateTargetPill(null);
  if (data.ok) {
    toast('练习运行成功；这里没有自动判题，自己对照任务检查', 'ok', 3600);
  } else {
    toast('练习代码报错，查看控制台', 'bad', 4200);
  }
}

function setRunStatus(ok, data) {
  const el = $('#runStatus');
  if (!el) return;
  if (data === null && ok === null) {
    el.className = 'run-status';
    el.innerHTML = `<span class="dot"></span><span>尚未运行</span>`;
    return;
  }
  if (!data) {
    el.className = 'run-status bad';
    el.innerHTML = `<span class="dot"></span><span>运行失败</span>`;
    return;
  }
  el.className = 'run-status ' + (ok ? 'ok' : 'bad');
  const size = data.width ? `${data.width}×${data.height}` : '';
  const link = data.run_id ? `<a href="/api/export/${data.run_id}" target="_blank" rel="noopener">导出 ZIP</a>` : '';
  el.innerHTML = `<span class="dot"></span><span>${ok ? '运行成功' : '运行失败'} · ${data.duration_ms || 0} ms ${size ? '· ' + size : ''}</span><span class="spacer"></span>${link}`;
}

function renderOutput() {
  const lesson = currentLesson();
  const data = state.lastRun;
  const tabs = $('#outTabs');
  const body = $('#outBody');
  if (!tabs || !body) return;
  tabs.innerHTML = outputTabs(data);
  let html = '';
  if (state.outTab === 'console') html = outputConsole(data);
  else if (state.outTab === 'images') html = outputImages(data);
  else if (state.outTab === 'metrics') html = outputMetrics(data);
  else html = outputChecks(data, lesson);
  body.innerHTML = html;
  tabs.querySelectorAll('[data-out-tab]').forEach((tab) => {
    tab.classList.toggle('active', tab.dataset.outTab === state.outTab);
  });
}

function outputConsole(data) {
  if (!data) return emptyOutput();
  let html = '';
  if (data.stdout) html += `<pre class="console">${escapeHtml(data.stdout)}</pre>`;
  // The runner prints the traceback to stderr and also stores it in error;
  // showing both duplicates a long traceback.
  const stderrText = data.error ? '' : (data.stderr || '');
  if (stderrText) html += `<pre class="console"><span class="err">${escapeHtml(stderrText)}</span></pre>`;
  if (data.error) {
    html += `<pre class="console"><span class="err">${escapeHtml(data.error)}</span></pre>`;
    const m = /File "<lesson>", line (\d+)/.exec(data.error) || /line (\d+)/.exec(data.error);
    if (m) html += `<button class="btn btn-sm" style="margin-top:8px" data-action="goto-line" data-line="${m[1]}">定位到第 ${m[1]} 行</button>`;
  }
  if (!html) html = `<div class="empty">${icon('terminal', 26)}<b>没有文字输出</b><span>这段代码只生成了图像或指标</span></div>`;
  return html;
}

function outputImages(data) {
  if (!data) return emptyOutput();
  const items = [];
  if (data.original_url) items.push({ url: data.original_url, name: '原图 / 输入' });
  (data.outputs || []).forEach((o) => items.push({ url: o.url, name: o.name || '结果图' }));
  if (!items.length) {
    return `<div class="empty">${icon('image', 26)}<b>没有图像输出</b><span>这一课是纯文本/指标实验</span></div>`;
  }
  return `<div class="img-grid">${items.map((item) => `<figure class="img-card" data-action="lightbox" data-src="${escapeHtml(item.url)}" data-caption="${escapeHtml(item.name)}" title="点击放大">
    <img src="${escapeHtml(item.url)}" alt="${escapeHtml(item.name)}" loading="lazy">
    <figcaption>${escapeHtml(item.name)}</figcaption>
  </figure>`).join('')}</div>`;
}

function outputMetrics(data) {
  if (!data || !data.metrics || !Object.keys(data.metrics).length) {
    return `<div class="empty">${icon('gauge', 26)}<b>没有指标</b><span>在代码里用 metric("名称", 值) 记录实验指标</span></div>`;
  }
  return `<div class="metric-grid">${Object.entries(data.metrics).map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><b>${escapeHtml(fmtNum(value))}</b></div>`).join('')}</div>`;
}

function outputChecks(data, lesson) {
  if (state.mode === 'scratch') {
    return `<div class="empty">${icon('code', 26)}<b>练习模式没有自动判题</b><span>对照左侧任务，自己检查输出、坐标和指标</span></div>`;
  }
  if (!data) {
    return `<div class="empty">${icon('checks', 26)}<b>还没有判题结果</b><span>运行代码后，这里会显示自动检查</span></div>`;
  }
  const checks = data.checks || [];
  if (!checks.length) {
    return `<div class="empty">${icon('checks', 26)}<b>本课没有自动检查</b><span>用运行结果和小测自检</span></div>`;
  }
  return `<div class="checks">${checks.map((c) => `<div class="check ${c.passed ? 'pass' : 'fail'}">
    <span class="ico">${c.passed ? '✓' : '×'}</span>
    <span class="ct"><b>${escapeHtml(c.name)}</b><span>${escapeHtml(c.detail || (c.passed ? '通过' : '未通过'))}</span></span>
  </div>`).join('')}</div>`;
}

function evaluateTarget(lesson, data) {
  if (!lesson || !lesson.target || !data || !data.metrics) return null;
  const target = lesson.target;
  if (!(target.metric in data.metrics)) return null;
  const actual = Number(data.metrics[target.metric]);
  const expected = Number(target.value);
  let hit = false;
  if (target.op === '<=') hit = actual <= expected;
  else if (target.op === '>=') hit = actual >= expected;
  else if (target.op === '<') hit = actual < expected;
  else if (target.op === '>') hit = actual > expected;
  else if (target.op === '==') hit = Math.abs(actual - expected) < 1e-9;
  return { hit, actual, expected, op: target.op };
}

function updateTargetPill(data) {
  const lesson = currentLesson();
  const pill = $('#targetPill');
  if (!lesson || !pill) return;
  if (state.mode === 'scratch') {
    pill.className = 'target-pill';
    pill.textContent = '练习模式 · 无判题';
    pill.title = '自由练习没有自动判题，自己对照任务检查';
    return;
  }
  const target = lesson.target;
  pill.title = target ? target.label : '本课自动检查';
  if (!target) {
    pill.className = 'target-pill';
    pill.textContent = '自动检查';
    return;
  }
  const evaluated = evaluateTarget(lesson, data);
  if (!evaluated) {
    pill.className = 'target-pill';
    pill.textContent = `目标 · ${target.metric} ${target.op} ${fmtNum(target.value)}`;
    return;
  }
  pill.className = 'target-pill ' + (evaluated.hit ? 'hit' : 'miss');
  pill.textContent = evaluated.hit
    ? `挑战达成 · ${fmtNum(evaluated.actual)}`
    : `挑战 · ${fmtNum(evaluated.actual)} ${evaluated.op} ${fmtNum(evaluated.expected)}`;
}

/* --------------------------------------------------------------------------
   11. Clipboard, lightbox, modals, toast
   -------------------------------------------------------------------------- */

async function copyText(text, btn) {
  try {
    await navigator.clipboard.writeText(text);
  } catch (err) {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (e) { /* ignore */ }
    ta.remove();
  }
  if (btn) {
    const old = btn.innerHTML;
    btn.innerHTML = '已复制';
    setTimeout(() => { btn.innerHTML = old; }, 1300);
  }
  toast('已复制到剪贴板', 'ok', 1600);
}

function toast(message, type = 'info', ms = 2800) {
  const root = $('#toast-root');
  if (!root) return;
  const el = document.createElement('div');
  el.className = 'toast ' + type;
  el.innerHTML = `<span class="ico">${type === 'ok' ? '✓' : type === 'bad' ? '×' : 'i'}</span><span>${escapeHtml(message)}</span>`;
  const existing = root.querySelectorAll('.toast');
  if (existing.length >= 2) existing[0].remove();
  root.appendChild(el);
  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(6px)';
    setTimeout(() => el.remove(), 240);
  }, ms);
}

function openLightbox(src, caption) {
  const root = $('#modal-root');
  root.innerHTML = `<div class="lightbox" data-close-lightbox>
    <button class="close" aria-label="关闭">${icon('x', 18)}</button>
    <figure style="margin:0"><img src="${escapeHtml(src)}" alt="${escapeHtml(caption || '')}"><figcaption>${escapeHtml(caption || '')}</figcaption></figure>
  </div>`;
  root.querySelector('.lightbox').addEventListener('click', () => { root.innerHTML = ''; });
}

async function openLanInfo() {
  const root = $('#modal-root');
  root.innerHTML = `<div class="modal-backdrop"><div class="modal lan-modal" role="dialog" aria-modal="true" aria-label="平板访问">
    <div class="lan-loading">${icon('tablet', 26)}<span>正在检查局域网地址…</span></div>
  </div></div>`;
  try {
    const response = await fetch('/api/lan', { cache: 'no-store' });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || '读取失败');
    const live = data.lan && data.lan_url;
    root.innerHTML = `<div class="modal-backdrop"><div class="modal lan-modal" role="dialog" aria-modal="true" aria-label="平板访问">
      <div class="lan-head">
        <span class="lan-icon">${icon('tablet', 24)}</span>
        <div><div class="eyebrow">Tablet mode</div><h3>${live ? '在平板上打开' : '开启平板访问'}</h3></div>
        <button class="icon-btn" data-close-modal aria-label="关闭">${icon('x', 16)}</button>
      </div>
      ${live ? `
        <p class="lan-lede">平板和电脑连同一个 Wi-Fi，用平板浏览器打开下面这个地址。Python 和 OpenCV 仍然在电脑上运行，平板只负责显示和写代码。</p>
        <div class="lan-url"><code>${escapeHtml(data.lan_url)}</code><button class="btn btn-sm btn-primary" data-action="copy-url" data-url="${escapeHtml(data.lan_url)}">复制地址</button></div>
        <ol class="lan-steps">
          <li>确认平板和电脑连的是同一个 Wi-Fi（不要用平板流量）。</li>
          <li>在平板浏览器地址栏输入上面的地址。</li>
          <li>如果打不开：运行 <code>allow_tablet_firewall.bat</code>；如果 Wi-Fi 被 Windows 识别为「公用网络」，默认会拦截，需要允许或改为「专用」。</li>
          <li>用完点页面左下角「退出服务」，或双击 <code>stop.bat</code>。</li>
        </ol>
        <div class="lan-warn">${icon('alert', 14)} ${escapeHtml(data.warning)}</div>
      ` : `
        <p class="lan-lede">当前是「仅本机」模式，平板无法直接连接。双击项目里的 <code>start_tablet.bat</code> 即可切换为局域网模式。</p>
        <ol class="lan-steps">
          <li>在电脑上双击 <code>start_tablet.bat</code>（会先关掉当前服务，再以局域网模式重启）。</li>
          <li>如果 Windows 弹出防火墙提示，勾选「专用网络」并允许。</li>
          <li>回到本页点「平板访问」，复制新地址到平板浏览器打开。</li>
        </ol>
        <div class="lan-warn">${icon('alert', 14)} 局域网模式会让同一 Wi-Fi 下的设备访问本机；只在可信网络使用。</div>
      `}
      <div class="lan-foot"><button class="btn btn-sm" data-close-modal>知道了</button></div>
    </div></div>`;
    root.querySelector('.modal-backdrop').addEventListener('click', (event) => {
      if (event.target === root.querySelector('.modal-backdrop')) closeModal();
    });
  } catch (err) {
    root.innerHTML = `<div class="modal-backdrop"><div class="modal lan-modal"><p class="lan-lede">读取失败：${escapeHtml(err.message || err)}</p><div class="lan-foot"><button class="btn btn-sm" data-close-modal>关闭</button></div></div></div>`;
  }
}

function closeModal() {
  const root = $('#modal-root');
  if (root) root.innerHTML = '';
}

function openConfirm({ title, text, confirmText = '确认', danger = false, onConfirm }) {
  const root = $('#modal-root');
  root.innerHTML = `<div class="modal-backdrop">
    <div class="modal" role="dialog" aria-modal="true" aria-label="${escapeHtml(title)}" style="max-width:480px">
      <div style="padding:22px 22px 8px">
        <h3 style="font-size:18px;margin-bottom:8px">${escapeHtml(title)}</h3>
        <p style="margin:0;color:var(--muted);font-size:12.5px;line-height:1.75">${escapeHtml(text)}</p>
      </div>
      <div style="display:flex;justify-content:flex-end;gap:8px;padding:16px 22px 20px">
        <button class="btn btn-sm" data-close-modal>取消</button>
        <button class="btn btn-sm ${danger ? 'btn-lime' : 'btn-primary'}" id="confirmYes">${escapeHtml(confirmText)}</button>
      </div>
    </div>
  </div>`;
  root.querySelector('[data-close-modal]').addEventListener('click', closeModal);
  root.querySelector('.modal-backdrop').addEventListener('click', (e) => {
    if (e.target === root.querySelector('.modal-backdrop')) closeModal();
  });
  root.querySelector('#confirmYes').addEventListener('click', async () => {
    closeModal();
    if (onConfirm) await onConfirm();
  });
}

/* --------------------------------------------------------------------------
   12. Search
   -------------------------------------------------------------------------- */

function buildSearchIndex() {
  state.searchIndex = 0;
  state.searchData = state.lessons.map((l) => {
    const ch = chapterOf(l);
    return {
      id: l.id,
      title: l.title,
      subtitle: l.subtitle,
      chapter: ch ? ch.title : '',
      number: lessonGlobalIndex(l),
      text: [l.title, l.subtitle, (l.tags || []).join(' '), (l.objectives || []).join(' '), ch ? ch.title : ''].join(' ').toLowerCase(),
    };
  });
}

function openSearch() {
  const root = $('#modal-root');
  state.searchIndex = 0;
  root.innerHTML = `<div class="modal-backdrop">
    <div class="modal" role="dialog" aria-modal="true" aria-label="搜索课程">
      <div class="search-head">${icon('search', 18)}<input id="searchInput" type="search" placeholder="搜索课程、标签、技能…" autocomplete="off" spellcheck="false"><span class="kbd">ESC</span></div>
      <div class="search-results" id="searchResults"></div>
      <div class="search-foot"><span>↑ ↓ 选择</span><span>Enter 打开</span><span>Ctrl + K 随时搜索</span></div>
    </div>
  </div>`;
  const input = $('#searchInput');
  input.focus();
  const render = () => {
    const q = input.value.trim().toLowerCase();
    let results = state.searchData;
    if (q) results = results.filter((r) => r.text.includes(q));
    results = results.slice(0, 9);
    const box = $('#searchResults');
    if (!results.length) {
      state.searchResults = [];
      box.innerHTML = `<div class="search-empty">没有匹配的课程。试试「HSV」「PID」「标定」。</div>`;
      return;
    }
    state.searchResults = results;
    state.searchIndex = Math.min(state.searchIndex, results.length - 1);
    box.innerHTML = results.map((r, i) => `<a class="search-item ${i === state.searchIndex ? 'active' : ''}" href="#/lesson/${r.id}" data-search-item="${i}">
      <span class="sidx">${String(r.number).padStart(2, '0')}</span>
      <span class="st"><b>${escapeHtml(r.title)}</b><span>${escapeHtml(r.chapter)} · ${escapeHtml(r.subtitle)}</span></span>
      <span class="sk">OPEN</span>
    </a>`).join('');
    box.querySelectorAll('[data-search-item]').forEach((a) => {
      a.addEventListener('click', () => { closeModal(); });
    });
  };
  input.addEventListener('input', () => { state.searchIndex = 0; render(); });
  input.addEventListener('keydown', (e) => {
    if (!state.searchResults || !state.searchResults.length) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      state.searchIndex = (state.searchIndex + 1) % state.searchResults.length;
      render();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      state.searchIndex = (state.searchIndex - 1 + state.searchResults.length) % state.searchResults.length;
      render();
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const item = state.searchResults[state.searchIndex];
      if (item) { closeModal(); location.hash = '#/lesson/' + item.id; }
    }
  });
  root.querySelector('.modal-backdrop').addEventListener('click', (e) => {
    if (e.target === root.querySelector('.modal-backdrop')) closeModal();
  });
  render();
}

/* --------------------------------------------------------------------------
   13. AI assistant
   -------------------------------------------------------------------------- */

function toggleAI() {
  const existing = $('#aiPanel');
  if (existing) { existing.remove(); return; }
  const panel = document.createElement('div');
  panel.className = 'ai-panel';
  panel.id = 'aiPanel';
  panel.innerHTML = `<div class="ai-head">
      <span class="brand-mark" style="width:30px;height:30px;border-radius:9px">${brandMark(18)}</span>
      <span class="t"><b>AI 助教</b><span>贴着本课代码回答 · 可选</span></span>
      <button class="icon-btn" data-ai-close aria-label="关闭">${icon('x', 15)}</button>
    </div>
    <div class="ai-msgs" id="aiMsgs"></div>
    <div class="ai-input"><textarea id="aiInput" placeholder="例如：为什么红色要用两段 HSV？" rows="1"></textarea><button class="ai-send" id="aiSend" aria-label="发送">${icon('right', 16)}</button></div>`;
  document.body.appendChild(panel);
  panel.querySelector('[data-ai-close]').addEventListener('click', () => panel.remove());
  panel.querySelector('#aiSend').addEventListener('click', sendAI);
  panel.querySelector('#aiInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendAI(); }
  });
  state.aiMessages = state.aiMessages || [];
  if (!state.aiMessages.length) {
    addAIMessage('bot', '我是本课的 AI 助教。可以问我某段代码为什么这么写、某个参数怎么调，或者让解释报错。我会结合右侧代码回答。');
  } else {
    renderAIMessages();
  }
}

function addAIMessage(role, text) {
  state.aiMessages.push({ role, text });
  renderAIMessages();
}

function renderAIMessages() {
  const box = $('#aiMsgs');
  if (!box) return;
  box.innerHTML = state.aiMessages.map((m) => `<div class="ai-msg ${m.role}">${m.role === 'bot' ? renderAIText(m.text) : escapeHtml(m.text)}</div>`).join('');
  box.scrollTop = box.scrollHeight;
}

function renderAIText(text) {
  let s = escapeHtml(text || '');
  const blocks = [];
  s = s.replace(/```(?:python)?\n([\s\S]*?)```/g, (_, code) => {
    blocks.push(code);
    return `@@CODEBLOCK${blocks.length - 1}@@`;
  });
  s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  s = s.replace(/\n/g, '<br>');
  s = s.replace(/@@CODEBLOCK(\d+)@@/g, (_, index) => {
    return `<pre style="margin:6px 0;padding:8px;border-radius:6px;background:#060a0f;overflow:auto"><code>${blocks[Number(index)]}</code></pre>`;
  });
  return s;
}

async function sendAI() {
  if (state.aiBusy) return;
  const input = $('#aiInput');
  const q = input ? input.value.trim() : '';
  if (!q) return;
  input.value = '';
  addAIMessage('user', q);
  state.aiBusy = true;
  addAIMessage('bot', '思考中…');
  const box = $('#aiMsgs');
  const pending = box ? box.lastElementChild : null;
  try {
    const lesson = currentLesson();
    const code = $('#code') ? $('#code').value : '';
    const response = await fetch('/api/ai', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q, code, lesson_title: lesson ? lesson.title : '' }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'AI 请求失败');
    state.aiMessages.pop();
    addAIMessage('bot', data.answer || '（没有返回内容）');
  } catch (err) {
    state.aiMessages.pop();
    addAIMessage('bot', '调用失败：' + (err.message || err) + '\n\n如果还没配置，请在 data/ai_config.json 填入 key；不配置也不影响课程运行。');
    if (pending) pending.remove();
  } finally {
    state.aiBusy = false;
  }
}

/* --------------------------------------------------------------------------
   14. Progress export / exit
   -------------------------------------------------------------------------- */

function exportProgress() {
  const pct = percentComplete();
  const lines = [];
  lines.push('# RoboVision Lab 学习进度');
  lines.push('');
  lines.push('生成时间：' + new Date().toLocaleString('zh-CN'));
  lines.push('总进度：' + completedCount() + '/' + state.lessons.length + '（' + pct + '%）');
  lines.push('');
  state.chapters.forEach((ch) => {
    const done = ch.lessons.filter((l) => lessonProgress(l.id).completed).length;
    lines.push('## 第 ' + ch.number + ' 章 · ' + ch.title + '（' + done + '/' + ch.lessons.length + '）');
    lines.push('');
    ch.lessons.forEach((l) => {
      const p = lessonProgress(l.id);
      const checks = Object.values(p.checks || {});
      const passed = checks.filter(Boolean).length;
      const quizTotal = (l.quiz || []).length;
      const quizDone = Object.keys(p.quiz || {}).length;
      const quizCorrect = (l.quiz || []).filter((q, i) => p.quiz[i] === q.answer).length;
      lines.push('- [' + (p.completed ? 'x' : ' ') + '] ' + l.title +
        ' · 检查 ' + passed + '/' + (l.tests || []).length +
        (quizTotal ? ' · 小测 ' + quizCorrect + '/' + quizTotal : '') +
        (quizDone < quizTotal ? '（未完成）' : ''));
    });
    lines.push('');
  });
  lines.push('## 下一步');
  const next = firstIncomplete();
  lines.push(next ? '- 继续：' + next.title + '（#/lesson/' + next.id + '）' : '- 全部完成，开始整理作品集。');
  lines.push('');
  downloadText('RoboVision-学习进度.md', lines.join('\n'), 'text/markdown;charset=utf-8');
  toast('学习进度已导出', 'ok');
}

function exitApp() {
  openConfirm({
    title: '退出学习软件？',
    text: '会停止本地 Python 服务。已保存的代码和进度不会丢失；下次双击桌面上的「机器人视觉学习台」快捷方式即可继续。',
    confirmText: '退出',
    danger: true,
    onConfirm: async () => {
      try {
        await fetch('/api/shutdown', { method: 'POST' });
        document.body.innerHTML = `<div style="min-height:100vh;display:grid;place-items:center;background:#060a0f;color:#e7eff8;font-family:system-ui;text-align:center"><div><div style="font-size:34px;margin-bottom:10px">✓</div><h2 style="font-weight:600">学习服务已关闭</h2><p style="color:#8da2b7;font-size:13px">可以关闭这个窗口了。下次双击桌面上的「机器人视觉学习台」快捷方式继续。</p></div></div>`;
      } catch (err) {
        toast('关闭失败：' + err.message, 'bad');
      }
    },
  });
}

/* --------------------------------------------------------------------------
   15. Global events & router
   -------------------------------------------------------------------------- */

function persistCurrentDraft() {
  saveEditorImmediate();
}

document.addEventListener('click', (event) => {
  const actionEl = event.target.closest('[data-action]');
  if (actionEl) {
    const action = actionEl.dataset.action;
    if (action === 'lan-info') { openLanInfo(); return; }
    if (action === 'copy-url') { copyText(actionEl.dataset.url, actionEl); return; }
    if (action === 'select-week') { selectWeek(Number(actionEl.dataset.week)); return; }
    if (action === 'select-skill') { selectSkill(Number(actionEl.dataset.skill)); return; }
    if (action === 'guide-view') {
      const y = window.scrollY;
      state.guideView = actionEl.dataset.view;
      renderGuide();
      window.scrollTo(0, y);
      return;
    }
    if (action === 'skills-view') {
      const y = window.scrollY;
      state.skillsView = actionEl.dataset.view;
      renderSkills();
      window.scrollTo(0, y);
      return;
    }
    if (action === 'toggle-theme') { toggleTheme(); return; }
    if (action === 'open-search') { openSearch(); return; }
    if (action === 'toggle-ai') { toggleAI(); return; }
    if (action === 'export-progress') { exportProgress(); return; }
    if (action === 'exit-app') { exitApp(); return; }
    if (action === 'copy-seg') {
      const lesson = currentLesson();
      const seg = lesson && lesson.walkthrough[Number(actionEl.dataset.seg)];
      if (seg) copyText(seg.code, actionEl);
      return;
    }
    if (action === 'open-scratch') {
      setMode('scratch');
      const lab = $('#lab');
      if (lab) lab.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
    if (action === 'reset-code') {
      const lesson = currentLesson();
      if (!lesson) return;
      const isScratch = state.mode === 'scratch';
      openConfirm({
        title: isScratch ? '清空我的练习？' : '恢复初始代码？',
        text: isScratch
          ? '当前「我的代码」会被清空成一张新的练习纸。课程代码不受影响。'
          : '当前编辑器里的修改会被替换成本课原始代码。这个操作不能撤销。',
        confirmText: isScratch ? '清空' : '恢复',
        onConfirm: () => {
          const ta = $('#code');
          if (!ta) return;
          if (isScratch) {
            ta.value = scratchTemplate(lesson);
            state.scratch[lesson.id] = ta.value;
            saveJSON(LS.scratch, state.scratch);
          } else {
            ta.value = lesson.starter;
            state.drafts[lesson.id] = lesson.starter;
            saveJSON(LS.drafts, state.drafts);
          }
          ta.dispatchEvent(new Event('input'));
          state.lastRun = null;
          state.runMode = isScratch ? 'scratch' : 'lesson';
          state.outTab = 'console';
          renderOutput();
          setRunStatus(null, null);
          toast(isScratch ? '已清空并新建一张练习纸' : '已恢复初始代码', 'ok');
        },
      });
      return;
    }
    if (action === 'download-code') {
      const lesson = currentLesson();
      const ta = $('#code');
      if (lesson && ta) {
        const suffix = state.mode === 'scratch' ? '-我的练习' : '';
        downloadText(lesson.id + suffix + '.py', ta.value, 'text/x-python;charset=utf-8');
      }
      return;
    }
    if (action === 'goto-line') {
      const n = Number(actionEl.dataset.line);
      selectLine(n);
      return;
    }
    if (action === 'lightbox') {
      openLightbox(actionEl.dataset.src, actionEl.dataset.caption);
      return;
    }
    if (action === 'toggle-complete') {
      const lesson = currentLesson();
      if (!lesson) return;
      const p = lessonProgress(lesson.id);
      updateProgress(lesson.id, { completed: !p.completed });
      const btn = $('#completeBtn');
      if (btn) {
        btn.classList.toggle('done', !p.completed);
        btn.innerHTML = !p.completed ? icon('check', 16) + ' 已完成' : icon('check', 16) + ' 标记完成';
      }
      toast(!p.completed ? '本课已标记完成' : '已取消完成标记', !p.completed ? 'ok' : 'info');
      return;
    }
  }

  const closeModalBtn = event.target.closest('[data-close-modal]');
  if (closeModalBtn) { closeModal(); return; }
  const quizBtn = event.target.closest('[data-quiz-q]');
  if (quizBtn) {
    // handled by per-lesson listeners; kept as a safe no-op fallback
  }
});

document.addEventListener('keydown', (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault();
    if (!state.data) return;
    openSearch();
    return;
  }
  if (event.key === 'Escape') {
    closeModal();
    const ai = $('#aiPanel');
    if (ai) ai.remove();
    return;
  }
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    if (state.currentId && $('#runBtn')) {
      event.preventDefault();
      runCode();
    }
  }
});

function selectLine(n) {
  const ta = $('#code');
  if (!ta) return;
  const lines = ta.value.split('\n');
  n = Math.max(1, Math.min(n, lines.length));
  let start = 0;
  for (let i = 0; i < n - 1; i++) start += lines[i].length + 1;
  ta.focus();
  ta.setSelectionRange(start, start + lines[n - 1].length);
  ta.scrollTop = Math.max(0, (n - 1) * 21.45 - 80);
  ta.dispatchEvent(new Event('scroll'));
}

function route() {
  persistCurrentDraft();
  closeModal();
  const hash = location.hash || '#/';
  if (hash.startsWith('#/lesson/')) {
    const id = decodeURIComponent(hash.slice('#/lesson/'.length));
    renderLesson(id);
  } else if (hash === '#/guide') {
    renderGuide();
  } else if (hash === '#/skills') {
    renderSkills();
  } else {
    renderMap();
  }
  window.scrollTo(0, 0);
  const boot = $('#boot');
  if (boot) boot.classList.add('hidden');
}

async function init() {
  applyTheme(state.theme);
  try {
    const [lessonsResponse, healthResponse] = await Promise.all([
      fetch('/api/lessons', { cache: 'no-store' }),
      fetch('/api/health', { cache: 'no-store' }).catch(() => null),
    ]);
    if (!lessonsResponse.ok) throw new Error('无法读取课程数据');
    state.data = await lessonsResponse.json();
    if (healthResponse && healthResponse.ok) {
      state.health = await healthResponse.json().catch(() => null);
    }
    state.chapters = (state.data.chapters || []).map((ch) => ({
      ...ch,
      lessons: ch.lessons.map((l) => ({ ...l, chapterId: ch.id, chapterTitle: ch.title, chapterColor: ch.color })),
    }));
    state.lessons = [];
    state.byId = {};
    state.chapters.forEach((ch) => {
      ch.lessons.forEach((l) => {
        state.lessons.push(l);
        state.byId[l.id] = l;
      });
    });
    buildSearchIndex();
    if (!location.hash) location.hash = '#/';
    route();
    window.addEventListener('hashchange', route);
  } catch (err) {
    const boot = $('#boot');
    if (boot) {
      boot.innerHTML = `<div style="text-align:center;max-width:520px;padding:20px">
        <div style="color:#fb7185;font-size:34px;margin-bottom:8px">!</div>
        <h2 style="font-size:18px;margin-bottom:8px">课程数据加载失败</h2>
        <p style="color:#8da2b7;font-size:12.5px;line-height:1.8">${escapeHtml(err.message || err)}<br>请确认本地服务正在运行，然后刷新页面。</p>
        <button class="btn btn-primary" style="margin-top:14px" onclick="location.reload()">重新加载</button>
      </div>`;
    }
  }
}

init();
