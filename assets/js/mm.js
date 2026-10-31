/* Molecules & Models — progressive enhancements.
 * Everything here is optional: the site is fully readable without it.
 * State lives in localStorage (wrapped in try/catch): mm-theme, mm-progress, mm-last.
 */
(function () {
  "use strict";
  var root = document.documentElement;
  var COURSE = window.MM_COURSE || { pages: {}, chapters: {}, parts: [], sequence: [] };

  var store = {
    get: function (k, fallback) { try { var v = localStorage.getItem(k); return v === null ? fallback : v; } catch (e) { return fallback; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode etc. */ } },
    del: function (k) { try { localStorage.removeItem(k); } catch (e) {} }
  };
  function el(tag, attrs, html) {
    var e = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    if (html !== undefined) e.innerHTML = html;
    return e;
  }
  var ICON = {
    sun: '<svg viewBox="0 0 16 16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="8" cy="8" r="3"/><path d="M8 1.5v2M8 12.5v2M1.5 8h2M12.5 8h2M3.4 3.4l1.4 1.4M11.2 11.2l1.4 1.4M3.4 12.6l1.4-1.4M11.2 4.8l1.4-1.4"/></svg>',
    moon: '<svg viewBox="0 0 16 16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><path d="M13.5 10.2A6 6 0 0 1 5.8 2.5a6 6 0 1 0 7.7 7.7z"/></svg>',
    auto: '<svg viewBox="0 0 16 16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="6"/><path d="M8 2a6 6 0 0 1 0 12z" fill="currentColor" stroke="none"/></svg>'
  };

  /* ---------------------------------------------------------------- theme (Dark / Light / Auto) */
  var mq = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;
  function wantsDark(pref) { return pref === "dark" || (pref === "auto" && mq && mq.matches); }
  function isDark() { return document.body.classList.contains("quarto-dark"); }
  function applyTheme(pref) {
    root.setAttribute("data-mm-theme-pref", pref);
    var dark = wantsDark(pref);
    root.setAttribute("data-mm-theme", dark ? "dark" : "light");
    if (typeof window.quartoToggleColorScheme === "function" && isDark() !== dark) {
      window.quartoToggleColorScheme();
    }
    document.querySelectorAll("[data-mm-theme-btn]").forEach(function (b) {
      b.setAttribute("aria-checked", String(b.getAttribute("data-mm-theme-btn") === pref));
    });
  }
  function themeControl() {
    var pref = store.get("mm-theme", "dark");
    var wrap = el("div", { class: "mm-theme-ctl" });
    var seg = el("div", { class: "mm-seg", role: "radiogroup", "aria-label": "Colour theme" });
    [["dark", "Dark", ICON.moon], ["light", "Light", ICON.sun], ["auto", "Auto", ICON.auto]].forEach(function (o) {
      var b = el("button", { type: "button", role: "radio", "data-mm-theme-btn": o[0], "aria-checked": String(o[0] === pref), title: o[1] + " theme", "aria-label": o[1] + " theme" }, o[2]);
      b.addEventListener("click", function () { store.set("mm-theme", o[0]); applyTheme(o[0]); });
      seg.appendChild(b);
    });
    wrap.appendChild(seg);
    applyTheme(pref);
    if (mq && mq.addEventListener) mq.addEventListener("change", function () { if (store.get("mm-theme", "dark") === "auto") applyTheme("auto"); });
    return wrap;
  }

  function mountHeaderControls() {
    var tools = document.querySelector(".navbar .quarto-navbar-tools");
    if (!tools) return;
    tools.insertBefore(themeControl(), tools.firstChild);
  }

  /* ---------------------------------------------------------------- progress */
  function readProgress() { try { var p = JSON.parse(store.get("mm-progress", "[]")); return Array.isArray(p) ? p : []; } catch (e) { return []; } }
  function writeProgress(list) { store.set("mm-progress", JSON.stringify(list)); }
  function isDone(id) { return readProgress().indexOf(id) !== -1; }
  function setDone(id, done) {
    var p = readProgress().filter(function (x) { return x !== id; });
    if (done) p.push(id);
    writeProgress(p);
  }
  function chapterStats(cid) {
    var ch = COURSE.chapters[cid];
    if (!ch) return null;
    var done = ch.trackable.filter(isDone).length;
    return { done: done, total: ch.trackable.length, pct: ch.trackable.length ? Math.round(100 * done / ch.trackable.length) : 0 };
  }
  function paintProgress() {
    document.querySelectorAll("[data-mm-check]").forEach(function (c) { c.classList.toggle("is-done", isDone(c.getAttribute("data-mm-check"))); });
    document.querySelectorAll("[data-mm-pct]").forEach(function (s) {
      var st = chapterStats(s.getAttribute("data-mm-pct"));
      if (!st || !st.total) return;
      s.textContent = st.pct + "%";
      s.setAttribute("aria-label", st.done + " of " + st.total + " completed");
    });
    document.querySelectorAll("[data-mm-bar]").forEach(function (bar) {
      var st = chapterStats(bar.getAttribute("data-mm-bar"));
      if (!st || !st.total) return;
      bar.hidden = st.done === 0;
      bar.firstElementChild.style.width = st.pct + "%";
    });
    document.querySelectorAll("[data-mm-chapter-progress]").forEach(function (box) {
      var st = chapterStats(box.getAttribute("data-mm-chapter-progress"));
      if (!st || !st.total) return;
      box.hidden = false;
      box.querySelector(".mm-progress > span").style.width = st.pct + "%";
      box.querySelector(".mm-pct-text").textContent = st.done + " of " + st.total + " completed (" + st.pct + "%)";
    });
    document.querySelectorAll("[data-mm-complete]").forEach(function (btn) {
      var id = btn.getAttribute("data-mm-complete");
      var done = isDone(id);
      btn.hidden = false;
      btn.setAttribute("aria-pressed", String(done));
      btn.classList.toggle("is-done", done);
      btn.querySelector(".mm-complete-text").textContent = done ? "Completed — click to undo" : "Mark episode complete";
      var hint = btn.parentElement.querySelector("[data-mm-complete-hint]");
      if (hint) hint.hidden = false;
    });
  }
  function wireComplete() {
    document.querySelectorAll("[data-mm-complete]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var id = btn.getAttribute("data-mm-complete");
        setDone(id, !isDone(id));
        paintProgress();
      });
    });
  }
  function resetControl() {
    var menu = document.querySelector("#quarto-sidebar .sidebar-menu-container");
    if (!menu) return;
    var box = el("div", { class: "mm-sidebar-resources mm-sidebar-progress" });
    var p = readProgress().length;
    box.innerHTML = '<div class="mm-res-title">Your progress</div><p class="mm-small" style="padding:0 .5rem;margin:0 0 .35rem">' + p + " page" + (p === 1 ? "" : "s") + ' completed. Stored in this browser only.</p>';
    var btn = el("button", { type: "button", class: "mm-btn mm-btn-sm", style: "margin:0 .5rem" }, "Reset progress");
    btn.addEventListener("click", function () {
      if (window.confirm("Clear all completion marks stored in this browser?")) { writeProgress([]); paintProgress(); box.querySelector("p").textContent = "0 pages completed. Stored in this browser only."; }
    });
    box.appendChild(btn);
    menu.appendChild(box);
  }
  function rememberVisit() {
    var btn = document.querySelector("[data-mm-complete]");
    if (!btn) return;
    var id = btn.getAttribute("data-mm-complete");
    var pg = COURSE.pages[id];
    if (pg) store.set("mm-last", JSON.stringify({ id: id, when: Date.now() }));
  }
  function continueCard() {
    var box = document.querySelector("[data-mm-continue]");
    if (!box) return;
    var target = null, why = "";
    try { var last = JSON.parse(store.get("mm-last", "null")); if (last && COURSE.pages[last.id]) { target = COURSE.pages[last.id]; why = "You were last on"; } } catch (e) {}
    var prog = readProgress();
    if (prog.length) {
      // the first trackable page in course order that is not done yet, after the last completed one
      var lastDoneIdx = -1;
      COURSE.sequence.forEach(function (id, i) { if (prog.indexOf(id) !== -1) lastDoneIdx = i; });
      for (var i = lastDoneIdx + 1; i < COURSE.sequence.length; i++) {
        var pg = COURSE.pages[COURSE.sequence[i]];
        if (pg && (pg.kind === "episode" || pg.kind === "lab") && prog.indexOf(pg.id) === -1) { target = pg; why = "Next up"; break; }
      }
    }
    if (!target) return;
    var ch = COURSE.chapters[target.chapter];
    box.hidden = false;
    box.querySelector("[data-mm-continue-title]").textContent = (target.label ? target.label + " · " : "") + target.title;
    box.querySelector("[data-mm-continue-sub]").textContent = why + (ch ? " in Chapter " + ch.number + ": " + ch.title : "");
    var a = box.querySelector("[data-mm-continue-link]");
    a.href = target.href;
  }

  /* ---------------------------------------------------------------- solutions, quizzes, outputs, print */
  function solutionsToggle() {
    var sols = document.querySelectorAll("details.mm-callout--solution");
    if (!sols.length) return;
    var btn = el("button", { type: "button", class: "mm-btn mm-btn-sm mm-solutions-toggle", "aria-pressed": "false" }, "Expand all solutions");
    btn.addEventListener("click", function () {
      var open = btn.getAttribute("aria-pressed") !== "true";
      sols.forEach(function (d) { d.open = open; });
      btn.setAttribute("aria-pressed", String(open));
      btn.textContent = open ? "Collapse all solutions" : "Expand all solutions";
    });
    var tools = el("div", { class: "mm-page-tools" });
    tools.appendChild(btn);
    var title = document.querySelector(".mm-title");
    if (title) title.insertAdjacentElement("afterend", tools);
  }
  function quizzes() {
    document.querySelectorAll("[data-mm-quiz]").forEach(function (ol) {
      var score = ol.parentElement.querySelector("[data-mm-quiz-score]");
      var tries = 0;
      ol.querySelectorAll("details.mm-quiz-option").forEach(function (d) {
        d.addEventListener("toggle", function () {
          if (!d.open) return;
          tries += 1;
          ol.querySelectorAll("details.mm-quiz-option").forEach(function (o) { if (o !== d) o.open = false; });
          if (score) {
            score.hidden = false;
            score.textContent = d.getAttribute("data-correct") === "true" ? ("Correct" + (tries > 1 ? " on attempt " + tries : " first time") + ".") : "Try another option.";
          }
        });
      });
    });
  }
  function longOutputs() {
    document.querySelectorAll(".cell-output pre").forEach(function (pre) {
      if (pre.scrollHeight <= 440) return;
      var wrap = pre.parentElement;
      wrap.classList.add("mm-output-collapsed");
      var b = el("button", { type: "button", class: "mm-btn mm-btn-sm mm-output-toggle", "aria-expanded": "false" }, "Show full output");
      b.addEventListener("click", function () {
        var collapsed = wrap.classList.toggle("mm-output-collapsed");
        b.textContent = collapsed ? "Show full output" : "Collapse output";
        b.setAttribute("aria-expanded", String(!collapsed));
      });
      wrap.appendChild(b);
    });
  }
  function printing() {
    window.addEventListener("beforeprint", function () { document.querySelectorAll("details").forEach(function (d) { d.open = true; }); });
  }
  function searchShortcut() {
    // Quarto already binds "/" (search.keyboard-shortcut); make sure "/" never types into the page body
    document.addEventListener("keydown", function (e) {
      if (e.key !== "/" || e.ctrlKey || e.metaKey || e.altKey) return;
      var t = e.target;
      if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
      var btn = document.querySelector("#quarto-search .aa-DetachedSearchButton, #quarto-search button");
      if (btn) { e.preventDefault(); btn.click(); }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    mountHeaderControls();
    wireComplete();
    paintProgress();
    resetControl();
    rememberVisit();
    continueCard();
    solutionsToggle();
    quizzes();
    longOutputs();
    printing();
    searchShortcut();
  });
})();
