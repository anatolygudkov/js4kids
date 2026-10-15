"""Добавляет к ссылкам на assets/*.css и *.js версию по содержимому файла (?v=abc123),
чтобы браузер не брал из кэша старые стили и скрипты после обновления сайта.

Запуск (после любых правок в assets/): python3 tools/bust_cache.py
"""
import glob
import hashlib
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..")
ASSETS = ("style.css", "code.js", "practice.js", "os.js")


def version(name):
    with open(os.path.join(ROOT, "assets", name), "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()[:8]


def main():
    versions = {name: version(name) for name in ASSETS}
    pages = glob.glob(os.path.join(ROOT, "index.html")) + glob.glob(os.path.join(ROOT, "*", "*.html"))
    changed = 0
    for page in pages:
        with open(page, encoding="utf-8") as f:
            text = f.read()
        new = text
        for name, v in versions.items():
            new = re.sub(r'(assets/' + re.escape(name) + r')(\?v=[0-9a-f]+)?"', r'\1?v=' + v + '"', new)
        if new != text:
            with open(page, "w", encoding="utf-8") as f:
                f.write(new)
            changed += 1
    print(f"{changed} pages updated", versions)


if __name__ == "__main__":
    main()
