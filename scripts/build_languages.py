"""Profil için dil halkası (assets/languages.svg) üretir.

Veri: GitHub API'deki repo dil istatistikleri (bayt). Gizli repolar da sayılır
(token'ın `repo` izni olmalı). Hazır kod tabanları ve arayüz/işaretleme dilleri
dışarıda bırakılır; repo içindeki .gitattributes ayarları GitHub tarafında zaten
uygulanmış olarak gelir.

Çalıştırma:  GH_TOKEN=... python scripts/build_languages.py
"""
import json
import math
import os
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "languages.svg"

# Benim yazmadığım hazır kod tabanı + profil reposunun kendisi.
SKIPPED_REPOS = {"nopCommerce-v4.80-Internship-Project", "Femrei"}
IGNORED = {
    "HTML", "CSS", "SCSS", "TypeScript", "JavaScript", "Astro", "Vue", "Dart", "C++", "C", "CMake",
    "Swift", "Kotlin", "Objective-C", "Batchfile", "Shell", "PowerShell", "Dockerfile", "Procfile",
    "Scheme", "TeX", "PHP", "Makefile",
}
ALIASES = {"PLpgSQL": "SQL", "TSQL": "SQL", "Jupyter Notebook": "Notebook"}
TOP = 5

THEMES = {
    "light": {"t": "#1f2328", "m": "#656d76", "r": "#d0d7de", "bg": "#ffffff",
              "c0": "#b45309", "c1": "#d97706", "c2": "#92400e", "c3": "#f59e0b", "c4": "#78350f", "c5": "#8c959f"},
    "dark":  {"t": "#e6edf3", "m": "#7d8590", "r": "#30363d", "bg": "#0d1117",
              "c0": "#f0a23b", "c1": "#c47a1f", "c2": "#f8c77e", "c3": "#e9973a", "c4": "#7a4d16", "c5": "#6e7681"},
}


def api(path, token):
    req = urllib.request.Request(f"https://api.github.com{path}", headers={
        "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
        "User-Agent": "femrei-profile",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def collect(token):
    totals = {}
    page = 1
    while True:
        repos = api(f"/user/repos?affiliation=owner&per_page=100&page={page}", token)
        if not repos:
            break
        for repo in repos:
            if repo["fork"] or repo["name"] in SKIPPED_REPOS:
                continue
            for lang, size in api(f"/repos/{repo['full_name']}/languages", token).items():
                if lang in IGNORED:
                    continue
                name = ALIASES.get(lang, lang)
                totals[name] = totals.get(name, 0) + size
        page += 1
    return totals


def fmt(p):
    return "&lt;0.1%" if p < 0.1 else f"{p:.1f}%"


def render(totals):
    total = sum(totals.values())
    ranked = sorted(totals.items(), key=lambda kv: -kv[1])
    rows = ranked[:TOP]
    rest = sum(v for _, v in ranked[TOP:])
    if rest:
        rows.append(("diğer", rest))

    css_vars = lambda t: "; ".join(f"--{k}: {v}" for k, v in THEMES[t].items())
    W, H = 880, 230
    cx, cy, r, sw = 130, 118, 70, 22
    circ = 2 * math.pi * r
    # Çok küçük dilimler de görünsün: en az 1.2 derece.
    min_len = circ * 1.2 / 360
    lens = [max(v / total * circ, min_len) for _, v in rows]
    scale = circ / sum(lens)
    lens = [l * scale for l in lens]

    arcs, legend, offset = [], [], 0.0
    for i, ((name, value), length) in enumerate(zip(rows, lens)):
        color = f"var(--c{min(i, 5) if name != 'diğer' else 5})"
        gap = 2 if len(rows) > 1 else 0
        arcs.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" style="stroke:{color}" stroke-width="{sw}" '
            f'stroke-dasharray="{max(length - gap, 0.5):.2f} {circ:.2f}" stroke-dashoffset="{-offset:.2f}" '
            f'transform="rotate(-90 {cx} {cy})" class="arc" />'
        )
        offset += length
        pct = value / total * 100
        y = 58 + i * 28
        bar = max(pct / 100 * 300, 2)
        legend.append(
            f'<g class="row" style="animation-delay:{0.3 + i * 0.1:.1f}s">'
            f'<rect x="270" y="{y - 9}" width="10" height="10" style="fill:{color}"/>'
            f'<text x="290" y="{y}" font-size="13" style="fill:var(--t)">{name}</text>'
            f'<rect x="420" y="{y - 7}" width="300" height="6" style="fill:var(--r)"/>'
            f'<rect x="420" y="{y - 7}" width="{bar:.1f}" height="6" style="fill:{color}" class="bar"/>'
            f'<text x="{W - 40}" y="{y}" font-size="12" text-anchor="end" style="fill:var(--m)">{fmt(pct)}</text></g>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="En çok kullandığım diller">
<style>
  :root {{ {css_vars("light")}; }}
  @media (prefers-color-scheme: dark) {{ :root {{ {css_vars("dark")}; }} }}
  text {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; }}
  .arc {{ opacity: 0; animation: fade .6s .1s forwards; }}
  .row {{ opacity: 0; animation: fade .4s forwards; }}
  .bar {{ transform-box: fill-box; transform-origin: left; animation: grow .9s .4s cubic-bezier(.2,.8,.2,1) both; }}
  @keyframes fade {{ to {{ opacity: 1; }} }}
  @keyframes grow {{ from {{ transform: scaleX(0); }} }}
  @media (prefers-reduced-motion: reduce) {{ .arc, .row {{ animation: none; opacity: 1; }} .bar {{ animation: none; }} }}
</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" style="fill:var(--bg);stroke:var(--r)"/>
<text x="40" y="28" font-size="11" style="fill:var(--m)">diller · kendi repolarımdaki koda göre</text>
{''.join(arcs)}
<text x="{cx}" y="{cy - 2}" font-size="12" text-anchor="middle" style="fill:var(--m)">kod</text>
<text x="{cx}" y="{cy + 16}" font-size="14" font-weight="700" text-anchor="middle" style="fill:var(--t)">{len(totals)} dil</text>
{''.join(legend)}
</svg>
"""


def main():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GH_TOKEN gerekli")
    totals = collect(token)
    OUT.write_text(render(totals), encoding="utf-8")
    total = sum(totals.values())
    for name, v in sorted(totals.items(), key=lambda kv: -kv[1]):
        print(f"{name:20s} {v / total * 100:6.2f}%")


if __name__ == "__main__":
    main()
