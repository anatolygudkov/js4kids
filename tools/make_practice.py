"""Собирает интерактивный задачник {ru,en,es}/practice.html из tools/practice_tasks.py.

Запуск: python3 tools/make_practice.py
"""
import html
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from practice_tasks import SECTIONS  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")

UI = {
    "ru": dict(
        title="Задачник", logo="🐍 JavaScript для детей", nav=("Оглавление", "Задачник", "Шпаргалка", "🌐 Язык"),
        kicker="После курса · {n} задач", h1="Задачник",
        lead="Задачи по всем темам курса — от совсем простых до хитрых. Решай в любом порядке и возвращайся к ним, чтобы потренироваться.",
        how=("<b>Как решать:</b>", [
            "прочитай условие и <b>сначала подумай</b> (или напиши код);",
            "нажми <b>▶ Запустить</b> — результат появится под кодом (а ещё можно <kbd>Ctrl</kbd> + <kbd>Enter</kbd>);",
            "код можно менять прямо здесь, <b>↺ Сбросить</b> вернёт исходный;",
            "открывай <b>подсказку</b>, если застрял, и <b>ответ</b> — только когда решил или очень-очень застрял;",
            "отмечай решённые задачи галочкой — прогресс сохраняется в браузере.",
        ]),
        levels=("Все", "⭐ Простые", "⭐⭐ Средние", "⭐⭐⭐ Сложные"),
        kinds=dict(predict="Что выведет?", fix="Найди ошибку", write="Напиши код", think="Подумай", project="Проект"),
        lessons="Уроки", lesson="Урок",
        run="▶ Запустить", reset="↺ Сбросить", done="Решено", hint="💡 Подсказка", answer="✅ Показать ответ",
        out="Здесь появится результат",
        norun="Эту задачу решай в своём файле в Geany — здесь её не запустить.",
        start="// Напиши код здесь\n",
        prev=("← Урок 16", "Игра в интернете"), next=("Всегда под рукой →", "Шпаргалка"),
        adult=("👨‍👩‍👧 Для взрослых", "Код задач выполняется прямо на странице, в изолированной «песочнице», и ничего не может сломать. Задачи с пометкой «Проект» — для своего файла <code>snake.html</code>."),
    ),
    "en": dict(
        title="Practice Problems", logo="🐍 JavaScript for Kids", nav=("Contents", "Practice", "Cheat sheet", "🌐 Language"),
        kicker="After the course · {n} problems", h1="Practice problems",
        lead="Problems on every topic of the course, from really easy to tricky. Solve them in any order and come back to practise.",
        how=("<b>How to solve them:</b>", [
            "read the problem and <b>think first</b> (or write the code);",
            "press <b>▶ Run</b> — the result appears under the code (<kbd>Ctrl</kbd> + <kbd>Enter</kbd> works too);",
            "you can change the code right here; <b>↺ Reset</b> brings back the original;",
            "open the <b>hint</b> if you're stuck, and the <b>answer</b> only once you've solved it or are really, really stuck;",
            "tick the problems you've solved — your progress is saved in the browser.",
        ]),
        levels=("All", "⭐ Easy", "⭐⭐ Medium", "⭐⭐⭐ Hard"),
        kinds=dict(predict="What's printed?", fix="Find the bug", write="Write code", think="Think", project="Project"),
        lessons="Lessons", lesson="Lesson",
        run="▶ Run", reset="↺ Reset", done="Solved", hint="💡 Hint", answer="✅ Show answer",
        out="The result will appear here",
        norun="Solve this one in your own file in Geany — it can't run here.",
        start="// Write your code here\n",
        prev=("← Lesson 16", "The game on the internet"), next=("Always at hand →", "Cheat sheet"),
        adult=("👨‍👩‍👧 For grown-ups", "The code runs right on the page, in an isolated \"sandbox\", and can't break anything. Problems marked \"Project\" are for your own <code>snake.html</code> file."),
    ),
    "es": dict(
        title="Ejercicios", logo="🐍 JavaScript desde cero", nav=("Índice", "Ejercicios", "Chuleta", "🌐 Idioma"),
        kicker="Después del curso · {n} ejercicios", h1="Ejercicios",
        lead="Ejercicios de todos los temas del curso, desde muy fáciles hasta retorcidos. Resuélvelos en el orden que quieras y vuelve a ellos para practicar.",
        how=("<b>Cómo resolverlos:</b>", [
            "lee el enunciado y <b>piensa primero</b> (o escribe el código);",
            "pulsa <b>▶ Ejecutar</b>: el resultado aparece debajo del código (también vale <kbd>Ctrl</kbd> + <kbd>Intro</kbd>);",
            "puedes cambiar el código aquí mismo; <b>↺ Restablecer</b> vuelve al original;",
            "abre la <b>pista</b> si te atascas, y la <b>respuesta</b> solo cuando lo hayas resuelto o estés muy, muy atascado;",
            "marca los ejercicios resueltos: tu progreso se guarda en el navegador.",
        ]),
        levels=("Todos", "⭐ Fáciles", "⭐⭐ Medios", "⭐⭐⭐ Difíciles"),
        kinds=dict(predict="¿Qué muestra?", fix="Encuentra el error", write="Escribe código", think="Piensa", project="Proyecto"),
        lessons="Lecciones", lesson="Lección",
        run="▶ Ejecutar", reset="↺ Restablecer", done="Resuelto", hint="💡 Pista", answer="✅ Ver la respuesta",
        out="Aquí aparecerá el resultado",
        norun="Este ejercicio resuélvelo en tu propio archivo en Geany: aquí no se puede ejecutar.",
        start="// Escribe tu código aquí\n",
        prev=("← Lección 16", "El juego en internet"), next=("Siempre a mano →", "Chuleta"),
        adult=("👨‍👩‍👧 Para personas adultas", "El código se ejecuta en la propia página, en un «arenero» aislado, y no puede romper nada. Los ejercicios marcados como «Proyecto» son para vuestro propio archivo <code>snake.html</code>."),
    ),
}


def pick(value, lang):
    if isinstance(value, dict):
        v = value.get(lang)
        return v
    return value


def code_of(task, lang):
    if "code_i18n" in task:
        return pick(task["code_i18n"], lang)
    return pick(task.get("code"), lang)


def answer_code_of(task, lang):
    v = None
    if "answer_code_i18n" in task:
        v = pick(task["answer_code_i18n"], lang)
    return v if v is not None else pick(task.get("answer_code"), lang)


def esc(s):
    return html.escape(s, quote=False)


def runnable(task):
    return task.get("run", True) and task["kind"] not in ("think", "project")


def render_task(task, lang, ui):
    tid = task["id"]
    stars = "⭐" * task["level"]
    out = [f'  <section class="task" id="t-{tid}" data-level="{task["level"]}">']
    out.append(
        f'    <div class="task-head"><span class="task-num">{tid}</span>'
        f'<span class="task-kind kind-{task["kind"]}">{ui["kinds"][task["kind"]]}</span>'
        f'<span class="task-level" title="{stars}">{stars}</span>'
        f'<label class="task-done"><input type="checkbox" data-task="{tid}"> {ui["done"]}</label></div>'
    )
    out.append(f'    <p>{pick(task["text"], lang)}</p>')
    code = code_of(task, lang)
    if runnable(task):
        if not code:
            code = ui["start"]
        rows = max(3, code.count("\n") + 2)
        out.append(
            f'    <div class="runner" data-id="{tid}" data-canvas="{1 if task.get("canvas") else 0}">'
            f'<textarea spellcheck="false" autocapitalize="off" autocomplete="off" rows="{rows}">{esc(code)}</textarea>'
            f'<div class="runner-bar"><button type="button" class="run">{ui["run"]}</button>'
            f'<button type="button" class="reset">{ui["reset"]}</button></div>'
            f'<div class="runner-view"><pre class="runner-out" data-placeholder="{ui["out"]}"></pre></div></div>'
        )
    else:
        if code:
            out.append(f'    <pre class="code">{esc(code)}</pre>')
        if task["kind"] in ("fix", "write", "project") and task.get("run") is False:
            out.append(f'    <p class="norun">{ui["norun"]}</p>')
    if task.get("hint"):
        out.append(f'    <details class="hint"><summary>{ui["hint"]}</summary><div>{pick(task["hint"], lang)}</div></details>')
    ans = [f'<p>{pick(task["answer"], lang)}</p>'] if task.get("answer") else []
    acode = answer_code_of(task, lang)
    if acode:
        ans.append(f'<pre class="code">{esc(acode)}</pre>')
    out.append(f'    <details class="answer"><summary>{ui["answer"]}</summary><div>{"".join(ans)}</div></details>')
    out.append("  </section>")
    return "\n".join(out)


def render(lang):
    ui = UI[lang]
    total = sum(len(s["tasks"]) for s in SECTIONS)
    nav = ui["nav"]
    parts = [f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{ui["title"]}</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<header class="top">
  <a class="logo" href="index.html">{ui["logo"]}</a>
  <nav><a href="index.html">{nav[0]}</a><a href="practice.html">{nav[1]}</a><a href="cheatsheet.html">{nav[2]}</a><a href="../index.html">{nav[3]}</a></nav>
</header>
<main class="practice">
  <p class="kicker">{ui["kicker"].format(n=total)}</p>
  <h1>{ui["h1"]}</h1>
  <p class="lead">{ui["lead"]}</p>
  <div class="goals">
    {ui["how"][0]}
    <ul>{"".join(f"<li>{x}</li>" for x in ui["how"][1])}</ul>
  </div>
  <div class="box adult"><span class="title">{ui["adult"][0]}</span>{ui["adult"][1]}</div>
  <div class="practice-tools">
    <div class="level-filter">"""]
    for value, text in zip(("all", "1", "2", "3"), ui["levels"]):
        active = ' class="active"' if value == "all" else ""
        parts.append(f'<button type="button" data-level="{value}"{active}>{text}</button>')
    parts.append(f"""</div>
    <div class="progress"><div class="progress-track"><div class="progress-fill"></div></div><span class="progress-label"></span></div>
  </div>
  <nav class="toc">""")
    for s in SECTIONS:
        parts.append(f'<a href="#s-{s["key"]}">{pick(s["title"], lang)}</a>')
    parts.append("</nav>")
    for s in SECTIONS:
        links = ", ".join(f'<a href="lesson-{n:02d}.html">{n}</a>' for n in s["lessons"])
        label = ui["lesson"] if len(s["lessons"]) == 1 else ui["lessons"]
        parts.append(f'\n  <h2 id="s-{s["key"]}">{pick(s["title"], lang)} <small class="sec-lessons">{label} {links}</small></h2>')
        for t in s["tasks"]:
            parts.append(render_task(t, lang, ui))
    parts.append(f"""
  <nav class="pager">
    <a class="prev" href="lesson-16.html"><small>{ui["prev"][0]}</small>{ui["prev"][1]}</a>
    <a class="next" href="cheatsheet.html"><small>{ui["next"][0]}</small>{ui["next"][1]}</a>
  </nav>
</main>
<script src="../assets/code.js"></script>
<script src="../assets/practice.js"></script>
</body>
</html>
""")
    return "\n".join(parts)


if __name__ == "__main__":
    for lang in UI:
        path = os.path.join(ROOT, lang, "practice.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(render(lang))
        print("wrote", path)
