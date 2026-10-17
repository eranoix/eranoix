#!/usr/bin/env python3
"""Generates assets/banner.svg from what is actually public on this account.

Every run asks the GitHub API which repositories are public and which languages
and frameworks they use, then redraws the image. The artwork that never changes
(the cubes and the brand symbol) lives in scripts/banner_art/, and every word is
turned into outlines with the fonts in scripts/fonts/, so the image looks the
same on any machine. Needs fontTools.
"""
from __future__ import annotations

import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

OWNER = os.environ.get("PROFILE_OWNER", "eranoix")
NAME = "Arthur Oliveira"
ROLE = "FULL STACK DEVELOPER"
TAGLINE = "I care about what users see, and what they never have to see."
OPEN_TO_WORK = True

HIGHLIGHT = ["TypeScript", "React", "Next.js", "Go", "Kotlin", "Python", "Tailwind CSS"]

FRAMEWORKS = {"next": "Next.js", "react": "React", "tailwindcss": "Tailwind CSS",
              "vite": "Vite", "hono": "Hono", "express": "Express"}
SKIP_DIRS = ("node_modules/", "example/", "examples/", "fixtures/", "testdata/")

SANS = "Segoe UI,Helvetica Neue,Helvetica,Arial,sans-serif"
MONO = "SFMono-Regular,Menlo,Consolas,Liberation Mono,monospace"
NAVY, NAVY2, TEAL, INK, MUTED = "#020617", "#0a1628", "#14b8a6", "#f8fafc", "#94a3b8"

HERE = Path(__file__).resolve().parent
ART = HERE / "banner_art"
FONTS = HERE / "fonts"
SANS_FILES = {"400": "Inter-Regular.ttf", "500": "Inter-Medium.ttf",
              "600": "Inter-SemiBold.ttf", "700": "Inter-Bold.ttf"}
MONO_FILE = "RobotoMono-Medium.ttf"


def api(path: str):
    req = urllib.request.Request(f"https://api.github.com{path}",
                                 headers={"Accept": "application/vnd.github+json",
                                          "User-Agent": f"{OWNER}-banner"})
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def frameworks_in(repo: dict) -> set[str]:
    import base64
    if repo.get("size", 0) == 0:
        return set()
    try:
        tree = api(f"/repos/{OWNER}/{repo['name']}/git/trees/{repo['default_branch']}?recursive=1")
    except urllib.error.HTTPError as e:
        if e.code in (404, 409):
            return set()
        raise
    found: set[str] = set()
    for node in tree.get("tree", []):
        path = node["path"]
        if not path.endswith("package.json") or any(d in f"/{path}" or path.startswith(d) for d in SKIP_DIRS):
            continue
        blob = api(f"/repos/{OWNER}/{repo['name']}/contents/{path}")
        try:
            pkg = json.loads(base64.b64decode(blob["content"]))
        except (KeyError, ValueError):
            continue
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        found |= {name for dep, name in FRAMEWORKS.items() if dep in deps}
    return found


def survey() -> dict:
    repos = [r for r in api(f"/users/{OWNER}/repos?type=owner&per_page=100")
             if not r["fork"] and not r["archived"] and not r["private"]
             and r["name"].lower() != OWNER.lower()]
    if not repos:
        sys.exit("no public repositories returned — refusing to draw an empty banner")
    langs: dict[str, int] = {}
    for r in repos:
        for lang, n in api(f"/repos/{OWNER}/{r['name']}/languages").items():
            langs[lang] = langs.get(lang, 0) + n
    frameworks: set[str] = set()
    for r in repos:
        frameworks |= frameworks_in(r)
    latest = max(repos, key=lambda r: r["pushed_at"])
    when = datetime.strptime(latest["pushed_at"][:10], "%Y-%m-%d").strftime("%b %Y")
    present = set(langs) | frameworks
    top = [x for x in HIGHLIGHT if x in present][:5]
    return {"projects": len(repos), "languages": len(langs), "top": top,
            "all_languages": sorted(langs, key=lambda k: -langs[k]),
            "frameworks": sorted(frameworks),
            "latest": latest["name"], "when": when}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, size, color, t, font=SANS, weight=400, spacing=None):
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{x}" y="{y}" fill="{color}" font-family="{font}" '
            f'font-size="{size}" font-weight="{weight}"{ls}>{esc(t)}</text>')


def art(name: str) -> str:
    return (ART / name).read_text().strip()


_FONTS: dict = {}


def _font(path: Path):
    if path not in _FONTS:
        from fontTools.ttLib import TTFont
        f = TTFont(path)
        _FONTS[path] = (f.getBestCmap(), f.getGlyphSet(), f["hmtx"], f["head"].unitsPerEm)
    return _FONTS[path]


def outline(match: re.Match) -> str:
    """One <text> as glyph outlines: same position, size, colour and tracking."""
    from fontTools.pens.svgPathPen import SVGPathPen
    tag = match.group(0)

    def attr(k, default=None):
        m = re.search(rf'{k}="([^"]+)"', tag)
        return m.group(1) if m else default

    family = attr("font-family", "")
    path = FONTS / (MONO_FILE if "mono" in family.lower() else SANS_FILES.get(attr("font-weight", "400"), SANS_FILES["400"]))
    cmap, glyphs, hmtx, upem = _font(path)
    size, tracking = float(attr("font-size")), float(attr("letter-spacing", "0"))
    x, y, scale = float(attr("x")), float(attr("y")), size / upem
    parts = []
    for ch in html.unescape(re.search(r">([^<]*)</text>", tag).group(1)):
        g = cmap.get(ord(ch))
        if g is None:
            x += size * 0.3
            continue
        pen = SVGPathPen(glyphs)
        glyphs[g].draw(pen)
        if pen.getCommands():
            parts.append(f'<path transform="translate({x:.2f} {y:.2f}) scale({scale:.6f} {-scale:.6f})" d="{pen.getCommands()}"/>')
        x += hmtx[g][0] * scale + tracking
    return f'<g fill="{attr("fill", "#000")}">' + "".join(parts) + "</g>"


def outlined(svg: str) -> str:
    return re.sub(r"<text[^>]*>[^<]*</text>", outline, svg)


LANG_COLOR = {
    "Go": "#00ADD8", "Go Template": "#00ADD8", "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6", "Kotlin": "#A97BFF", "Python": "#3572A5",
    "HTML": "#e34c26", "CSS": "#663399", "Shell": "#89e051", "PowerShell": "#012456",
    "Batchfile": "#C1F12E", "SQL": "#e38c00", "PLpgSQL": "#336790", "C++": "#f34b7d",
    "C": "#555555", "CMake": "#DA3434", "Makefile": "#427819", "Dockerfile": "#384d54",
    "Gradle": "#02303a", "XML": "#0060ac", "Java": "#b07219", "Lua": "#000080",
}
LEFT, RIGHT = 48, 832
_REG = dict(zip(" +-.0123456789", [278, 584, 333, 278] + [556] * 10))
_REG.update(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", [667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833,
                                                722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611]))
_REG.update(zip("abcdefghijklmnopqrstuvwxyz", [556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833,
                                                556, 556, 556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500]))
_BOLD = dict(_REG)
_BOLD.update(zip("ABJKLS", [722, 722, 556, 722, 611, 667]))
_BOLD.update(zip("abcdefghijklmnopqrstuvwxyz", [556, 611, 556, 611, 556, 333, 611, 611, 278, 278, 556, 278, 889,
                                                 611, 611, 611, 611, 389, 556, 333, 611, 556, 778, 556, 556, 500]))


def measure(s: str, size: float, weight: int) -> float:
    table = _BOLD if weight >= 600 else _REG
    return sum(table.get(ch, 600) for ch in s) * size / 1000 * 1.03


def dark(hex_color: str) -> bool:
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b < 70
PRIMARY = 6


def hexagon(cx: float, cy: float, r: float) -> str:
    pts = " ".join(f"{cx + r * c:.1f},{cy + r * s:.1f}" for c, s in
                   ((1, 0), (.5, .866), (-.5, .866), (-1, 0), (-.5, -.866), (.5, -.866)))
    return pts


AREAS = {
    "Web": ["TypeScript", "JavaScript", "HTML", "CSS", "React", "Next.js", "Tailwind CSS", "Vite"],
    "Backend": ["Go", "Go Template", "Python", "Hono", "Express"],
    "Mobile": ["Kotlin", "Gradle", "XML", "Java", "Swift"],
    "Data": ["SQL", "PLpgSQL"],
    "Tooling": ["Shell", "Dockerfile", "Makefile", "PowerShell", "CMake", "Batchfile", "C++", "C"],
}
FRAMEWORK_COLOR = {"Next.js": "#e5e7eb", "React": "#61dafb", "Tailwind CSS": "#38bdf8",
                   "Vite": "#bd34fe", "Hono": "#ff5b11", "Express": "#9ca3af"}
COL_W, ROW = 162, 21
HEAD_GAP = 16
HEAD_Y = (60, 60 + HEAD_GAP + round(42 * .72), 60 + HEAD_GAP + round(42 * .72) + HEAD_GAP + round(15 * .72))


def areas(s: dict) -> list[tuple[str, list[str]]]:
    """Every language and framework found, placed in its area, in the area's own order."""
    found = list(s["all_languages"]) + list(s["frameworks"])
    placed = {n for names in AREAS.values() for n in names}
    out = []
    for area, names in AREAS.items():
        members = [n for n in names if n in found]
        if area == "Tooling":
            members += [n for n in found if n not in placed]
        if members:
            out.append((area, members))
    return out


def mark(name: str, framework: bool, cx: float, cy: float) -> str:
    if framework:
        c = FRAMEWORK_COLOR.get(name, TEAL)
        return f'<polygon points="{hexagon(cx, cy, 4.2)}" fill="none" stroke="{c}" stroke-width="1.4"/>'
    c = LANG_COLOR.get(name, MUTED)
    ring = ".75" if dark(c) else ".3"
    return (f'<polygon points="{hexagon(cx, cy, 4.2)}" fill="{c}" stroke="#e2e8f0" '
            f'stroke-opacity="{ring}" stroke-width=".9"/>')


def render(s: dict) -> str:
    STRIP = 182
    top = set(s["all_languages"][:PRIMARY])
    frameworks = set(s["frameworks"])
    strip = []
    if OPEN_TO_WORK:
        label = "Open to remote roles"
        role_end = LEFT + len(ROLE) * (12 * 0.6 + 2.5)
        strip.append(f'<circle cx="{role_end + 20:.1f}" cy="{HEAD_Y[0] - 4.5}" r="4" fill="#34d399"/>'
                     + text(round(role_end + 32, 1), HEAD_Y[0], 12.5, "#6ee7b7", label, SANS, 500))
    cols = areas(s)
    title_y = STRIP + 34
    for i, (area, names) in enumerate(cols):
        x = LEFT + i * COL_W
        strip.append(text(x, title_y, 13, TEAL, area, SANS, 700))
        strip.append(f'<line x1="{x}" y1="{title_y + 10}" x2="{x + COL_W - 26}" y2="{title_y + 10}" stroke="#123040"/>')
        for j, n in enumerate(names):
            y = title_y + 32 + j * ROW
            big = n in top
            strip.append(mark(n, n in frameworks, x + 4, y - 4.5)
                         + text(x + 15, y, 13, INK if big else "#cbd5e1", n, SANS, 600 if big else 400))
    tallest = max((len(names) for _, names in cols), default=0)
    bottom = title_y + 32 + max(0, tallest - 1) * ROW
    H = bottom + 26
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 {H}" width="880" height="{H}" role="img" aria-label="{esc(NAME)}, {ROLE.lower()}">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{NAVY}"/><stop offset="1" stop-color="{NAVY2}"/></linearGradient>
<radialGradient id="fade" cx=".82" cy=".5" r=".6"><stop offset="0" stop-color="white" stop-opacity=".9"/><stop offset="1" stop-color="white" stop-opacity="0"/></radialGradient>
<mask id="gridmask"><rect width="880" height="{STRIP}" fill="url(#fade)"/></mask>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
</defs>
<rect width="880" height="{H}" rx="10" fill="url(#bg)"/>
{art("cubes.svg")}
<circle cx="740" cy="92" r="78" fill="none" stroke="{TEAL}" stroke-opacity=".16"/>
{art("symbol.svg")}
{text(48, HEAD_Y[0], 12, TEAL, ROLE, MONO, 500, "2.5")}
{text(46, HEAD_Y[1], 42, INK, NAME, SANS, 700, "-0.5")}
{text(48, HEAD_Y[2], 15, MUTED, TAGLINE)}
<path d="M0 {STRIP} H880 V{H-10} a10 10 0 0 1 -10 10 H10 a10 10 0 0 1 -10 -10 Z" fill="#030b17"/>
<line x1="0" y1="{STRIP}" x2="880" y2="{STRIP}" stroke="#123040"/>
{"".join(strip)}
</svg>
'''


if __name__ == "__main__":
    s = survey()
    print(json.dumps(s), file=sys.stderr)
    sys.stdout.write(outlined(render(s)))
