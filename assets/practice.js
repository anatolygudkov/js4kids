// Задачник: запуск кода в песочнице, сброс, отметки «Решено» и прогресс.
(function () {
  var LANG = (document.documentElement.lang || "en").slice(0, 2);
  var T = {
    ru: { empty: "(программа ничего не вывела)", line: "строка", progress: "Решено: {n} из {t}", running: "Работает…" },
    en: { empty: "(the program printed nothing)", line: "line", progress: "Solved: {n} of {t}", running: "Running…" },
    es: { empty: "(el programa no ha mostrado nada)", line: "línea", progress: "Resueltos: {n} de {t}", running: "Ejecutando…" }
  }[LANG] || null;
  if (!T) T = { empty: "(no output)", line: "line", progress: "{n} / {t}", running: "…" };

  var runners = document.querySelectorAll(".runner");
  var frames = {};

  function preamble(id) {
    return [
      "<!DOCTYPE html><html><head><meta charset='utf-8'></head>",
      "<body style='margin:0;background:#fff'>",
      "<canvas id='game' width='400' height='400' style='display:block;width:200px;height:200px;background:#fff'></canvas>",
      "<script>",
      "var __id = " + JSON.stringify(id) + ";",
      "function __send(t, v) { parent.postMessage({ id: __id, t: t, v: v }, '*'); }",
      "function __fmt(a) { return Array.prototype.map.call(a, function (x) { return (typeof x === 'object' && x !== null) ? JSON.stringify(x) : String(x); }).join(' '); }",
      "console.log = function () { __send('log', __fmt(arguments)); };",
      "window.alert = function (m) { __send('log', '[alert] ' + m); };",
      "window.prompt = function () { return null; };",
      "window.onerror = function (m, s, l) { __send('err', { m: String(m), l: l }); return true; };",
      "<\/script>",
      "<script>"
    ].join("\n") + "\n";
  }

  function run(box) {
    var id = box.getAttribute("data-id");
    var code = box.querySelector("textarea").value;
    var out = box.querySelector(".runner-out");
    var old = frames[id];
    if (old && old.parentNode) old.parentNode.removeChild(old);
    out.textContent = "";
    out.classList.remove("has-error");
    out.setAttribute("data-empty", T.running);
    var head = preamble(id);
    var offset = head.split("\n").length - 1;
    box.setAttribute("data-offset", offset);
    var iframe = document.createElement("iframe");
    iframe.setAttribute("sandbox", "allow-scripts");
    iframe.className = "runner-frame";
    if (box.getAttribute("data-canvas") !== "1") iframe.style.display = "none";
    iframe.srcdoc = head + code.replace(/<\/script/gi, "<\\/script") + "\n<\/script><script>__send('done', 0);<\/script></body></html>";
    box.querySelector(".runner-view").appendChild(iframe);
    frames[id] = iframe;
  }

  window.addEventListener("message", function (e) {
    var d = e.data;
    if (!d || !d.id) return;
    var box = document.querySelector('.runner[data-id="' + d.id + '"]');
    if (!box || !frames[d.id] || e.source !== frames[d.id].contentWindow) return;
    var out = box.querySelector(".runner-out");
    if (d.t === "log") {
      out.textContent += d.v + "\n";
    } else if (d.t === "err") {
      var line = d.v.l ? d.v.l - Number(box.getAttribute("data-offset")) : 0;
      out.textContent += "✖ " + d.v.m + (line > 0 ? "   (" + T.line + " " + line + ")" : "") + "\n";
      out.classList.add("has-error");
    }
    out.setAttribute("data-empty", out.textContent ? "" : T.empty);
  });

  for (var i = 0; i < runners.length; i++) {
    (function (box) {
      var ta = box.querySelector("textarea");
      var original = ta.value;
      box.querySelector(".run").addEventListener("click", function () { run(box); });
      box.querySelector(".reset").addEventListener("click", function () {
        ta.value = original;
        var f = frames[box.getAttribute("data-id")];
        if (f && f.parentNode) f.parentNode.removeChild(f);
        var out = box.querySelector(".runner-out");
        out.textContent = "";
        out.classList.remove("has-error");
        out.removeAttribute("data-empty");
      });
      ta.addEventListener("keydown", function (e) {
        if (e.key === "Tab" && !e.shiftKey) {
          e.preventDefault();
          var s = ta.selectionStart;
          ta.value = ta.value.slice(0, s) + "  " + ta.value.slice(ta.selectionEnd);
          ta.selectionStart = ta.selectionEnd = s + 2;
        }
        if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
          e.preventDefault();
          run(box);
        }
      });
    })(runners[i]);
  }

  // «Решено»: запоминаем в браузере, если это возможно
  var KEY = "js4kids-practice-" + LANG;
  var done = {};
  try { done = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { done = {}; }
  var boxes = document.querySelectorAll("input[data-task]");
  var bar = document.querySelector(".progress-fill");
  var label = document.querySelector(".progress-label");

  function update() {
    var n = 0;
    for (var k = 0; k < boxes.length; k++) {
      var on = boxes[k].checked;
      if (on) n++;
      var task = document.getElementById("t-" + boxes[k].getAttribute("data-task"));
      if (task) task.classList.toggle("is-done", on);
    }
    if (bar) bar.style.width = (boxes.length ? (100 * n) / boxes.length : 0) + "%";
    if (label) label.textContent = T.progress.replace("{n}", n).replace("{t}", boxes.length);
  }

  for (var k = 0; k < boxes.length; k++) {
    boxes[k].checked = !!done[boxes[k].getAttribute("data-task")];
    boxes[k].addEventListener("change", function () {
      done[this.getAttribute("data-task")] = this.checked;
      try { localStorage.setItem(KEY, JSON.stringify(done)); } catch (e) { /* без памяти тоже работает */ }
      update();
    });
  }
  update();

  // Сбросить все отметки
  var resetAll = document.querySelector(".reset-progress");
  if (resetAll) {
    resetAll.addEventListener("click", function () {
      if (!window.confirm(resetAll.getAttribute("data-confirm"))) return;
      done = {};
      for (var k = 0; k < boxes.length; k++) boxes[k].checked = false;
      try { localStorage.removeItem(KEY); } catch (e) { /* ничего страшного */ }
      update();
    });
  }

  // Фильтр по сложности
  var filters = document.querySelectorAll(".level-filter button");
  for (var f = 0; f < filters.length; f++) {
    filters[f].addEventListener("click", function () {
      var level = this.getAttribute("data-level");
      for (var b = 0; b < filters.length; b++) filters[b].classList.toggle("active", filters[b] === this);
      var tasks = document.querySelectorAll(".task");
      for (var t = 0; t < tasks.length; t++) {
        tasks[t].hidden = level !== "all" && tasks[t].getAttribute("data-level") !== level;
      }
    });
  }
})();
