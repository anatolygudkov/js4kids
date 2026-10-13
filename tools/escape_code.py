"""Подготовка уроков: экранирует код в блоках <pre ... data-raw>.

Пишите код в уроке как есть внутри <pre class="code" data-raw> ... </pre>.
Строка с » в начале подсвечивается как новая, с « — как удалённая.
Запуск (один раз на файл): python3 tools/escape_code.py ru/lesson-XX.html
"""
import html, re, sys

PAT = re.compile(r'<pre([^>]*?) data-raw>\n?(.*?)</pre>', re.S)


def ranges(nums):
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(str(nums[i]) if i == j else f"{nums[i]}-{nums[j]}")
        i = j + 1
    return ",".join(out)


def fix(m):
    attrs, body = m.group(1), m.group(2).rstrip()
    new, dele, lines = [], [], []
    for n, line in enumerate(body.split("\n"), 1):
        if line.startswith("»"):
            new.append(n); line = line[1:]
        elif line.startswith("«"):
            dele.append(n); line = line[1:]
        lines.append(line)
    if new:
        attrs += f' data-new="{ranges(new)}"'
    if dele:
        attrs += f' data-del="{ranges(dele)}"'
    return f"<pre{attrs}>" + html.escape("\n".join(lines), quote=False) + "</pre>"


for path in sys.argv[1:]:
    s = open(path, encoding="utf-8").read()
    s2, n = PAT.subn(fix, s)
    if n:
        open(path, "w", encoding="utf-8").write(s2)
    print(path, n)
