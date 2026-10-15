"""Проверяет задачник: ответы выполняются без ошибок и выводят ожидаемое,
а код задач «Найди ошибку» действительно содержит ошибку.

Нужен Node.js. Запуск: python3 tools/test_practice.py
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from practice_tasks import SECTIONS  # noqa: E402
from make_practice import answer_code_of, code_of, pick  # noqa: E402

RUNNER = r"""
const vm = require("vm");
const jobs = JSON.parse(require("fs").readFileSync(0, "utf8"));
const results = [];
for (const job of jobs) {
  const logs = [];
  const fmt = (a) => a.map((x) => (typeof x === "object" && x !== null ? JSON.stringify(x) : String(x))).join(" ");
  const ctx = new Proxy({}, { get: (t, k) => (k in t ? t[k] : () => {}), set: (t, k, v) => ((t[k] = v), true) });
  let handler = null;
  const timers = new Map();
  let nextId = 1;
  const sandbox = {
    console: { log: (...a) => logs.push(fmt(a)) },
    document: {
      getElementById: () => ({ getContext: () => ctx, width: 400, height: 400 }),
      addEventListener: (e, f) => { handler = f; },
    },
    setInterval: (f) => { const id = nextId++; timers.set(id, f); return id; },
    clearInterval: (id) => timers.delete(id),
    Math, Number, JSON,
  };
  let error = null;
  try {
    vm.runInNewContext(job.code, sandbox, { timeout: 2000 });
    for (let tick = 0; tick < 30 && timers.size; tick++) for (const f of [...timers.values()]) f();
    if (handler) for (const key of ["ArrowUp", "ArrowRight"]) handler({ key, code: "" });
  } catch (e) {
    error = String(e && e.message || e);
  }
  results.push({ out: logs.join("\n"), error });
}
console.log(JSON.stringify(results));
"""


def main():
    jobs, meta = [], []
    for s in SECTIONS:
        for t in s["tasks"]:
            for lang in ("ru", "en", "es"):
                code, acode = code_of(t, lang), answer_code_of(t, lang)
                expect = pick(t.get("expect"), lang)
                if t["kind"] == "predict":
                    jobs.append({"code": code}); meta.append((t["id"], lang, "predict", expect))
                if acode and not (t["kind"] == "project" or t["id"] in ("L2", "L3")):
                    jobs.append({"code": acode}); meta.append((t["id"], lang, "answer", expect))
                if t["kind"] == "fix" and t.get("run", True) and not t.get("visual_bug"):
                    jobs.append({"code": code}); meta.append((t["id"], lang, "broken", expect))
    res = subprocess.run(["node", "-e", RUNNER], input=json.dumps(jobs), capture_output=True, text=True, check=True)
    results = json.loads(res.stdout)
    bad = 0
    for (tid, lang, what, expect), r in zip(meta, results):
        problem = None
        if what in ("predict", "answer"):
            if r["error"]:
                problem = "error: " + r["error"]
            elif expect is not None and r["out"] != expect:
                problem = f"output {r['out']!r} != expected {expect!r}"
        elif what == "broken":
            if not r["error"] and (expect is None or r["out"] == expect):
                problem = "the 'broken' code works fine"
        if problem:
            bad += 1
            print(f"FAIL {tid} [{lang}] {what}: {problem}")
    print(f"checked {len(jobs)} runs, {bad} problems")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
