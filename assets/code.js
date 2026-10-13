// Простая подсветка кода для учебника (HTML + JavaScript).
// Работает без интернета. Каждый <pre class="code"> разбивается на строки,
// строки из data-new подсвечиваются зелёным (новый код), из data-del — красным (удалить).
(function () {
  var KEYWORDS = {
    "let": 1, "const": 1, "var": 1, "function": 1, "return": 1,
    "if": 1, "else": 1, "for": 1, "while": 1, "true": 1, "false": 1,
    "new": 1, "null": 1, "undefined": 1
  };

  var TOKEN = /(\/\/.*$|<!--.*?-->)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|`(?:[^`\\]|\\.)*`)|(<\/?[a-zA-Z!][^>]*>)|(\b\d+(?:\.\d+)?\b)|([A-Za-z_$][\w$]*)(\s*\()?/g;

  function esc(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function span(cls, text) {
    return '<span class="tk-' + cls + '">' + esc(text) + "</span>";
  }

  function tag(text) {
    var m = /^(<\/?)([\w!]+)([\s\S]*?)(\/?>)$/.exec(text);
    if (!m) return span("tag", text);
    var rest = m[3].replace(/("[^"]*"|'[^']*')|([\w-]+)|([^"'\w-]+)/g, function (all, str, word, other) {
      if (str) return span("str", str);
      if (word) return span("attr", word);
      return esc(other);
    });
    return span("tag", m[1] + m[2]) + rest + span("tag", m[4]);
  }

  function highlightLine(line) {
    var out = "";
    var last = 0;
    var m;
    TOKEN.lastIndex = 0;
    while ((m = TOKEN.exec(line))) {
      if (m[0] === "") { TOKEN.lastIndex++; continue; }
      out += esc(line.slice(last, m.index));
      if (m[1]) out += span("com", m[1]);
      else if (m[2]) out += span("str", m[2]);
      else if (m[3]) out += tag(m[3]);
      else if (m[4]) out += span("num", m[4]);
      else if (m[5]) {
        if (KEYWORDS[m[5]]) out += span("kw", m[5]);
        else if (m[6]) out += span("fn", m[5]);
        else out += esc(m[5]);
        if (m[6]) out += esc(m[6]);
      }
      last = TOKEN.lastIndex;
    }
    return out + esc(line.slice(last));
  }

  function parseRanges(s) {
    var set = {};
    if (!s) return set;
    s.split(",").forEach(function (part) {
      var ab = part.split("-");
      var a = parseInt(ab[0], 10);
      var b = ab.length > 1 ? parseInt(ab[1], 10) : a;
      for (var i = a; i <= b; i++) set[i] = true;
    });
    return set;
  }

  var blocks = document.querySelectorAll("pre.code");
  for (var k = 0; k < blocks.length; k++) {
    var pre = blocks[k];
    var text = pre.textContent.replace(/\s+$/, "");
    var isNew = parseRanges(pre.getAttribute("data-new"));
    var isDel = parseRanges(pre.getAttribute("data-del"));
    var lines = text.split("\n");
    var html = "";
    for (var i = 0; i < lines.length; i++) {
      var cls = "line";
      if (isNew[i + 1]) cls += " new";
      if (isDel[i + 1]) cls += " del";
      html += '<span class="' + cls + '">' + highlightLine(lines[i]) + "</span>";
    }
    pre.innerHTML = html;

    var file = pre.getAttribute("data-file");
    var wrap = document.createElement("div");
    wrap.className = "code-wrap";
    pre.parentNode.insertBefore(wrap, pre);
    if (file) {
      var label = document.createElement("div");
      label.className = "code-file";
      label.textContent = "📄 " + file;
      wrap.appendChild(label);
      pre.classList.add("has-file");
    }
    wrap.appendChild(pre);
  }
})();
