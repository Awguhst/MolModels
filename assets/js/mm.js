/* Molecules & Models — progressive enhancements.
 * Everything here is optional: the site is fully readable without it.
 * The only state kept is the theme preference (localStorage key mm-theme) and, for this browser tab only,
 * whether the roadmap intro has played (sessionStorage key mm-intro-seen); both wrapped in try/catch.
 * Nothing about what you have read is recorded, here or anywhere else.
 */
(function () {
  "use strict";
  var root = document.documentElement;

  var store = {
    get: function (k, fallback) { try { var v = localStorage.getItem(k); return v === null ? fallback : v; } catch (e) { return fallback; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode etc. */ } }
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
      // switch without transitions so the whole page changes colour at once
      root.classList.add("mm-theme-switching");
      window.quartoToggleColorScheme();
      requestAnimationFrame(function () { requestAnimationFrame(function () { root.classList.remove("mm-theme-switching"); }); });
    }
    document.querySelectorAll("[data-mm-theme-btn]").forEach(function (b) {
      var checked = b.getAttribute("data-mm-theme-btn") === pref;
      b.setAttribute("aria-checked", String(checked));
      b.tabIndex = checked ? 0 : -1;
    });
  }
  function themeControl() {
    var pref = store.get("mm-theme", "dark");
    var wrap = el("div", { class: "mm-theme-ctl" });
    var seg = el("div", { class: "mm-seg", role: "radiogroup", "aria-label": "Colour theme" });
    [["dark", "Dark", ICON.moon], ["light", "Light", ICON.sun], ["auto", "Auto", ICON.auto]].forEach(function (o) {
      var b = el("button", { type: "button", role: "radio", tabindex: o[0] === pref ? "0" : "-1", "data-mm-theme-btn": o[0], "aria-checked": String(o[0] === pref), title: o[1] + " theme", "aria-label": o[1] + " theme" }, o[2]);
      b.addEventListener("click", function () { store.set("mm-theme", o[0]); applyTheme(o[0]); });
      seg.appendChild(b);
    });
    seg.addEventListener("keydown", function (e) {
      var buttons = Array.from(seg.querySelectorAll("[data-mm-theme-btn]"));
      var index = buttons.indexOf(e.target);
      if (index === -1) return;
      if (e.key === "ArrowRight" || e.key === "ArrowDown") index = (index + 1) % buttons.length;
      else if (e.key === "ArrowLeft" || e.key === "ArrowUp") index = (index + buttons.length - 1) % buttons.length;
      else if (e.key === "Home") index = 0;
      else if (e.key === "End") index = buttons.length - 1;
      else return;
      e.preventDefault();
      var next = buttons[index].getAttribute("data-mm-theme-btn");
      store.set("mm-theme", next);
      applyTheme(next);
      buttons[index].focus();
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
    // On narrow screens the header has no room for the switch: a second copy lives at the foot of the
    // collapsed menu (CSS shows one or the other). Both copies share the same stored preference.
    var menu = document.querySelector("#navbarCollapse");
    if (menu) {
      var inMenu = themeControl();
      inMenu.classList.add("mm-theme-ctl--menu");
      inMenu.insertBefore(el("span", { class: "mm-theme-ctl-label" }, "Theme"), inMenu.firstChild);
      menu.appendChild(inMenu);
    }
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
  /* ---------------------------------------------------------------- code and output windows */
  var PANEL_ICON = {
    code: '<svg viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="m6 5-5 5 5 5m8-10 5 5-5 5m-3-12-2 14"/></svg>',
    copy: '<svg class="mm-copy-icon" viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 4V3a1 1 0 0 0-1-1H3a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h1"/></svg>',
    check: '<svg class="mm-copy-check" viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="m4 10 4 4 8-8"/></svg>',
    output: '<svg viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="m3 5 5 5-5 5m8 0h6"/></svg>',
    chevron: '<svg class="mm-output-chevron" viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="m5 7 5 5 5-5"/></svg>'
  };
  function codeLanguage(pre, code) {
    var labels = { python: "Python", py: "Python", bash: "Shell", sh: "Shell", shell: "Shell", zsh: "Shell", powershell: "PowerShell", ps1: "PowerShell", yaml: "YAML", yml: "YAML", json: "JSON", javascript: "JavaScript", js: "JavaScript", typescript: "TypeScript", ts: "TypeScript", r: "R", sql: "SQL", html: "HTML", css: "CSS", scss: "SCSS", markdown: "Markdown", md: "Markdown", tex: "LaTeX", latex: "LaTeX", bibtex: "BibTeX", toml: "TOML", ini: "INI", dockerfile: "Dockerfile", text: "Text", default: "Text" };
    var classes = Array.from(pre.classList).concat(Array.from(code.classList));
    for (var i = 0; i < classes.length; i += 1) {
      var key = classes[i].replace(/^language-/, "").toLowerCase();
      if (labels[key]) return labels[key];
    }
    return "Code";
  }
  function sourceText(code) {
    var clone = code.cloneNode(true);
    // Quarto's annotation controls are UI, not source. Empty line anchors and syntax spans
    // must not change indentation, blank lines, or trailing newlines in the copied program.
    Array.from(clone.children).forEach(function (child) {
      if (Array.from(child.classList).some(function (name) { return name.indexOf("code-annotation-") === 0; })) child.remove();
    });
    clone.querySelectorAll("a[aria-hidden='true'], .code-annotation-anchor, .code-annotation-container").forEach(function (node) { node.remove(); });
    return clone.textContent;
  }
  function legacyCopy(text) {
    var focused = document.activeElement;
    var selection = window.getSelection();
    var ranges = [];
    if (selection) for (var i = 0; i < selection.rangeCount; i += 1) ranges.push(selection.getRangeAt(i).cloneRange());
    var inputSelection = null;
    try { if (focused && typeof focused.selectionStart === "number") inputSelection = [focused.selectionStart, focused.selectionEnd, focused.selectionDirection]; } catch (e) { /* non-text input */ }
    var area = el("textarea", { readonly: "", "aria-hidden": "true", tabindex: "-1" });
    area.value = text;
    area.style.cssText = "position:fixed;top:0;left:-9999px;width:1px;height:1px;opacity:0;font-size:16px";
    document.body.appendChild(area);
    var copied = false;
    try {
      area.select();
      copied = document.execCommand("copy");
    } finally {
      area.remove();
      if (focused && focused.isConnected) focused.focus({ preventScroll: true });
      if (selection) {
        selection.removeAllRanges();
        ranges.forEach(function (range) { selection.addRange(range); });
      }
      if (inputSelection) focused.setSelectionRange(inputSelection[0], inputSelection[1], inputSelection[2]);
    }
    if (!copied) throw new Error("Clipboard copy was not available");
  }
  async function copySource(text) {
    if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
      try { await navigator.clipboard.writeText(text); return; } catch (e) { /* try the local selection fallback */ }
    }
    legacyCopy(text);
  }
  function codeWindows() {
    var windows = document.querySelectorAll("div.sourceCode");
    if (!windows.length) return;
    var status = el("div", { class: "mm-visually-hidden mm-copy-status", role: "status", "aria-live": "polite", "aria-atomic": "true" });
    document.body.appendChild(status);
    windows.forEach(function (panel) {
      if (panel.classList.contains("mm-code-window")) return;
      var pre = panel.querySelector("pre");
      var code = pre && pre.querySelector("code");
      if (!code) return;
      var language = codeLanguage(pre, code);
      var text = sourceText(code);
      var lineCount = text.replace(/\r\n/g, "\n").replace(/\n$/, "").split("\n").length;
      var toolbar = el("div", { class: "mm-code-toolbar" });
      var label = el("span", { class: "mm-code-language" }, PANEL_ICON.code);
      label.appendChild(document.createTextNode(language));
      var meta = el("span", { class: "mm-code-meta", "aria-hidden": "true" });
      meta.textContent = lineCount + (lineCount === 1 ? " line" : " lines");
      var button = el("button", { type: "button", class: "mm-copy-button", "data-state": "idle", "aria-label": "Copy " + language + " code" }, PANEL_ICON.copy + PANEL_ICON.check);
      var buttonLabel = el("span", { class: "mm-copy-label" });
      buttonLabel.textContent = "Copy";
      button.appendChild(buttonLabel);
      toolbar.appendChild(label);
      toolbar.appendChild(meta);
      toolbar.appendChild(button);
      panel.insertBefore(toolbar, pre);
      panel.classList.add("mm-code-window");
      pre.setAttribute("tabindex", "0");
      pre.setAttribute("aria-label", language + " code");
      pre.style.outlineOffset = "-4px";
      var scaffold = panel.closest(".code-copy-outer-scaffold");
      if (scaffold) scaffold.classList.add("mm-code-scaffold");
      // The replacement never matches ClipboardJS's delegated .code-copy-button selector.
      // Install it before removing the native control, preserving a working no-JS baseline.
      (scaffold || panel).querySelectorAll(".code-copy-button").forEach(function (nativeButton) {
        if (window.bootstrap && window.bootstrap.Tooltip) {
          var tooltip = window.bootstrap.Tooltip.getInstance(nativeButton);
          if (tooltip) tooltip.dispose();
        }
        nativeButton.remove();
      });
      var busy = false;
      var resetTimer;
      button.addEventListener("click", async function () {
        if (busy) return;
        busy = true;
        clearTimeout(resetTimer);
        button.setAttribute("data-state", "copying");
        button.setAttribute("aria-label", "Copying " + language + " code");
        button.setAttribute("aria-busy", "true");
        buttonLabel.textContent = "Copying…";
        status.textContent = "";
        try {
          await copySource(sourceText(code));
          button.setAttribute("data-state", "copied");
          button.setAttribute("aria-label", "Copied " + language + " code");
          buttonLabel.textContent = "Copied";
          status.textContent = language + " code copied to clipboard.";
        } catch (e) {
          button.setAttribute("data-state", "error");
          button.setAttribute("aria-label", "Retry copy of " + language + " code");
          buttonLabel.textContent = "Retry copy";
          status.textContent = "Could not copy. Select the code and copy it manually.";
        } finally {
          busy = false;
          button.removeAttribute("aria-busy");
          resetTimer = setTimeout(function () {
            button.setAttribute("data-state", "idle");
            button.setAttribute("aria-label", "Copy " + language + " code");
            buttonLabel.textContent = "Copy";
          }, 2400);
        }
      });
    });
  }
  function outputWindows() {
    var reduced = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;
    document.querySelectorAll(".cell > .cell-output").forEach(function (output, index) {
      if (output.classList.contains("mm-output-window")) return;
      var labelText = output.classList.contains("cell-output-stderr") ? "Warning" : output.classList.contains("cell-output-error") ? "Error" : "Output";
      var kind = output.querySelector("figure, img, svg") ? "Figure" : output.querySelector("table") ? "Table" : "Text";
      var toolbar = el("div", { class: "mm-output-toolbar" });
      var label = el("span", { class: "mm-output-label" }, PANEL_ICON.output);
      label.appendChild(document.createTextNode(labelText));
      var kindLabel = el("span", { class: "mm-output-kind" });
      kindLabel.textContent = kind;
      toolbar.appendChild(label);
      toolbar.appendChild(kindLabel);
      output.insertBefore(toolbar, output.firstChild);
      output.classList.add("mm-output-window");
      var pre = Array.from(output.children).find(function (node) { return node.tagName === "PRE"; });
      if (!pre || kind !== "Text") return;
      pre.setAttribute("tabindex", "0");
      pre.setAttribute("aria-label", labelText + " text");
      pre.style.outlineOffset = "-4px";
      var lines = pre.textContent.replace(/\r\n/g, "\n").replace(/\n$/, "").split("\n").length;
      var isLong = lines > 14 || pre.scrollHeight > 260;
      var content = el("div", { class: "mm-output-content", id: "mm-output-content-" + index });
      output.insertBefore(content, pre);
      content.appendChild(pre);
      if (!isLong) return;
      kindLabel.textContent = lines + " lines";
      output.classList.add("mm-output-collapsed");
      var footer = el("div", { class: "mm-output-footer" });
      var button = el("button", { type: "button", class: "mm-output-toggle", "aria-expanded": "false", "aria-controls": content.id });
      var buttonLabel = el("span", { class: "mm-output-toggle-label" });
      buttonLabel.textContent = "Show full output";
      button.appendChild(buttonLabel);
      button.insertAdjacentHTML("beforeend", PANEL_ICON.chevron);
      footer.appendChild(button);
      output.appendChild(footer);
      var animation = null;
      function stopAnimation() {
        if (animation) { animation.cancel(); animation = null; }
        content.style.removeProperty("overflow");
      }
      button.addEventListener("click", function () {
        var from = content.getBoundingClientRect().height;
        var oldButtonTop = button.getBoundingClientRect().top;
        stopAnimation();
        var collapsed = output.classList.toggle("mm-output-collapsed");
        button.setAttribute("aria-expanded", String(!collapsed));
        buttonLabel.textContent = collapsed ? "Show full output" : "Collapse output";
        var to = content.getBoundingClientRect().height;
        function finish() {
          animation = null;
          content.style.removeProperty("overflow");
          // Keep the collapse control in view even when thousands of output lines disappear.
          var position = button.getBoundingClientRect();
          var header = document.getElementById("quarto-header");
          var top = header ? header.getBoundingClientRect().bottom + 16 : 16;
          if (collapsed && (position.top < top || position.bottom > window.innerHeight)) {
            var target = Math.max(top, Math.min(oldButtonTop, window.innerHeight - 80));
            window.scrollBy({ top: position.top - target, behavior: "instant" });
          }
        }
        if (content.animate && !(reduced && reduced.matches) && from !== to) {
          content.style.overflow = "hidden";
          animation = content.animate([{ height: from + "px", maxHeight: "none" }, { height: to + "px", maxHeight: "none" }], { duration: 240, easing: "cubic-bezier(.2,.7,.2,1)" });
          animation.onfinish = finish;
        } else finish();
      });
      if (reduced && reduced.addEventListener) reduced.addEventListener("change", function (e) { if (e.matches) stopAnimation(); });
      window.addEventListener("beforeprint", stopAnimation);
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

  function rememberIntro() {
    // the roadmap's draw-in plays on the first visit to the home page in a session only
    if (document.querySelector(".mm-metro")) { try { sessionStorage.setItem("mm-intro-seen", "1"); } catch (e) {} }
  }

  /* ---------------------------------------------------------------- optional motion and reading position */
  function revealSections() {
    var sections = Array.from(document.querySelectorAll("[data-mm-reveal]"));
    if (!sections.length || !window.IntersectionObserver || !Element.prototype.animate) return;
    var reduced = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;
    var animations = new Map();
    var revealed = new WeakSet();
    var observer = new IntersectionObserver(function (entries) {
      var stagger = 0;
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var section = entry.target;
        observer.unobserve(section);
        if (revealed.has(section)) return;
        revealed.add(section);
        if ((reduced && reduced.matches) || section.contains(document.activeElement)) return;
        var animation = section.animate([
          { opacity: 0, transform: "translateY(16px)" },
          { opacity: 1, transform: "translateY(0)" }
        ], { duration: 650, delay: Math.min(stagger * 55, 160), easing: "cubic-bezier(.2,.7,.2,1)", fill: "backwards" });
        stagger += 1;
        animations.set(section, animation);
        animation.onfinish = function () { animations.delete(section); };
      });
    }, { threshold: 0.08 });

    function show(section) {
      revealed.add(section);
      observer.unobserve(section);
      var animation = animations.get(section);
      if (animation) { animation.cancel(); animations.delete(section); }
    }
    // Content is visible by default. Keyboard focus and reduced-motion preferences always win.
    document.addEventListener("focusin", function (e) {
      sections.forEach(function (section) { if (section.contains(e.target)) show(section); });
    });
    if (reduced && reduced.addEventListener) reduced.addEventListener("change", function (e) {
      if (e.matches) { observer.disconnect(); sections.forEach(show); }
    });
    if (!reduced || !reduced.matches) sections.forEach(function (section) { observer.observe(section); });
  }

  function readingProgress() {
    var main = document.querySelector("main.content");
    if (!main || document.querySelector(".mm-home")) return;
    var bar = el("div", { class: "mm-reading-progress", "aria-hidden": "true" });
    bar.style.transform = "scaleX(0)";
    document.body.appendChild(bar);
    var pending = false;
    function update() {
      pending = false;
      var bounds = main.getBoundingClientRect();
      var distance = bounds.height - window.innerHeight;
      var progress = distance > 0 ? -bounds.top / distance : (bounds.bottom <= window.innerHeight ? 1 : 0);
      bar.style.transform = "scaleX(" + Math.max(0, Math.min(1, progress)) + ")";
    }
    function schedule() {
      if (pending) return;
      pending = true;
      requestAnimationFrame(update);
    }
    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", schedule);
    window.addEventListener("load", schedule);
    if (window.ResizeObserver) new ResizeObserver(schedule).observe(main);
    schedule();
  }

  document.addEventListener("DOMContentLoaded", function () {
    rememberIntro();
    mountHeaderControls();
    solutionsToggle();
    quizzes();
    codeWindows();
    outputWindows();
    printing();
    searchShortcut();
    revealSections();
    readingProgress();
  });
})();
