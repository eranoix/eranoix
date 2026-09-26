#!/usr/bin/env python3
"""Generates assets/banner.svg from what is actually public on this account.

The status line at the bottom of the banner is not typed by hand. Every run
asks the GitHub API which repositories are public, which languages GitHub
counts in them, and which one changed most recently, then redraws the image.
A scheduled workflow runs it daily and commits the result only if it changed,
so a new project or a new language shows up without anyone editing anything.

Standard library only: nothing to install, nothing to break.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime

OWNER = os.environ.get("PROFILE_OWNER", "eranoix")
NAME = "Arthur Oliveira"
ROLE = "FULL-STACK ENGINEER"
TAGLINE = "I care about what users see, and what they never have to see."
OPEN_TO_WORK = True          # flip to False and the green dot disappears

# The order to highlight things in. It is a preference, not a claim: an item
# only appears in the banner if the survey below actually finds it in public
# code. Remove something from every repository and it leaves the banner too.
HIGHLIGHT = ["TypeScript", "React", "Next.js", "Go", "Kotlin", "Python", "Tailwind CSS"]

# Frameworks are not languages — GitHub counts .jsx as JavaScript and a Next.js
# app as TypeScript — so they are read from the dependencies each repository
# declares in its package.json files.
FRAMEWORKS = {"next": "Next.js", "react": "React", "tailwindcss": "Tailwind CSS",
              "vite": "Vite", "hono": "Hono", "express": "Express"}
# Fixtures and sample apps are not the owner's stack: safe-code-publisher ships a
# fictional leaking app under example/, and it must not add Express to the list.
SKIP_DIRS = ("node_modules/", "example/", "examples/", "fixtures/", "testdata/")

SANS = "Segoe UI,Helvetica Neue,Helvetica,Arial,sans-serif"
MONO = "SFMono-Regular,Menlo,Consolas,Liberation Mono,monospace"
NAVY, NAVY2, CYAN, CYAN2, INK, MUTED = "#020617", "#0a1628", "#22d3ee", "#0891b2", "#f8fafc", "#94a3b8"


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
    # A repository created a moment ago has no commits yet, and asking for its
    # tree answers 409. That once took the whole banner down on the same push
    # that created six new repositories; an empty repository simply adds nothing.
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
        # An empty answer is far more likely a broken request than an empty
        # account. Failing keeps yesterday's banner instead of publishing zeros.
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
            # Every language GitHub counts, most code first. The banner lists
            # all of them, so the count on the left and the names below agree.
            "all_languages": sorted(langs, key=lambda k: -langs[k]),
            "frameworks": sorted(frameworks),
            "latest": latest["name"], "when": when}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, size, color, t, font=SANS, weight=400, spacing=None):
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{x}" y="{y}" fill="{color}" font-family="{font}" '
            f'font-size="{size}" font-weight="{weight}"{ls}>{esc(t)}</text>')


HEX = "M32 4 L52 15 L56 32 L52 49 L32 60 L12 49 L8 32 L12 15 Z"


def hex_grid(height: int) -> str:
    r, w, out = 14, 14 * 3 ** 0.5, []
    row = 0
    while row * r * 1.5 < height + r:
        col = -1
        while col * w < 900:
            cx, cy = col * w + (w / 2 if row % 2 else 0), row * r * 1.5
            out.append(f'<path d="M{cx:.1f} {cy-r:.1f} L{cx+w/2:.1f} {cy-r/2:.1f} L{cx+w/2:.1f} {cy+r/2:.1f} '
                       f'L{cx:.1f} {cy+r:.1f} L{cx-w/2:.1f} {cy+r/2:.1f} L{cx-w/2:.1f} {cy-r/2:.1f} Z"/>')
            col += 1
        row += 1
    return "".join(out)


# The colour GitHub gives each language, so a reader who knows the language bar
# recognises them at a glance. A language missing here still appears, in grey.
LANG_COLOR = {
    "Go": "#00ADD8", "Go Template": "#00ADD8", "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6", "Kotlin": "#A97BFF", "Python": "#3572A5",
    "HTML": "#e34c26", "CSS": "#663399", "Shell": "#89e051", "PowerShell": "#012456",
    "Batchfile": "#C1F12E", "SQL": "#e38c00", "PLpgSQL": "#336790", "C++": "#f34b7d",
    "C": "#555555", "CMake": "#DA3434", "Makefile": "#427819", "Dockerfile": "#384d54",
    "Gradle": "#02303a", "XML": "#0060ac", "Java": "#b07219", "Lua": "#000080",
}
LEFT, RIGHT = 48, 832
# Helvetica advance widths (per 1000 units of font size), so every gap between
# names is the same width. An average character width left holes after short
# words and crowded long ones.
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
    return sum(table.get(ch, 600) for ch in s) * size / 1000 * 1.03  # 3% for Segoe/Arial drift


def dark(hex_color: str) -> bool:
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b < 70
PRIMARY = 6   # the languages with the most code are set larger


def hexagon(cx: float, cy: float, r: float) -> str:
    pts = " ".join(f"{cx + r * c:.1f},{cy + r * s:.1f}" for c, s in
                   ((1, 0), (.5, .866), (-.5, .866), (-1, 0), (-.5, -.866), (.5, -.866)))
    return pts


def words(s: dict) -> list[tuple[str, str, int, int, bool]]:
    """(name, colour, size, weight, hollow) in reading order.

    Size carries the one thing the old counters said: where most of the code is.
    The biggest languages come first and larger, the rest follow smaller, and
    frameworks close the list with a hollow marker, since they are not languages.
    """
    out = []
    for i, n in enumerate(s["all_languages"]):
        big = i < PRIMARY
        out.append((n, LANG_COLOR.get(n, MUTED), 17 if big else 14, 700 if big else 400, False))
    order = [f for f in HIGHLIGHT if f in s["frameworks"]] + [f for f in s["frameworks"] if f not in HIGHLIGHT]
    out += [(n, CYAN, 14, 400, True) for n in order]
    return out


def layout(items, top: int, reserve_first: float) -> tuple[list[str], int]:
    """Sets the words like text: left aligned, wrapping between words. Frameworks start a new line."""
    svg, x, line_top, line_h = [], LEFT, top, 0
    right = RIGHT - reserve_first
    prev_hollow = None
    rows = [[]]
    for item in items:
        name, color, size, weight, hollow = item
        w = 16 + measure(name, size, weight)
        new_group = prev_hollow is not None and hollow != prev_hollow
        if rows[-1] and (new_group or x + w > right):
            rows.append([]); x = LEFT; right = RIGHT
        rows[-1].append((item, x))
        x += w + 20
        prev_hollow = hollow
    y = top
    for row in rows:
        h = max(i[2] for i, _ in row) + 12
        base = y + h - 8
        for (name, color, size, weight, hollow), x in row:
            cy = base - size * 0.34
            r = 4.2 if size > 14 else 3.6
            if hollow:
                mark = f'<polygon points="{hexagon(x + 5, cy, r)}" fill="none" stroke="{color}" stroke-width="1.4"/>'
            else:
                ring = ".75" if dark(color) else ".25"
                mark = (f'<polygon points="{hexagon(x + 5, cy, r)}" fill="{color}" '
                        f'stroke="#e2e8f0" stroke-opacity="{ring}" stroke-width=".9"/>')
            ink = INK if size > 14 else "#cbd5e1"
            svg.append(mark + text(x + 16, base, size, ink, name, SANS, weight))
        y += h
    return svg, y


def render(s: dict) -> str:
    STRIP = 182
    strip = []
    reserve = 0
    if OPEN_TO_WORK:
        label = "Open to remote roles"
        lx = RIGHT - measure(label, 13, 500)
        reserve = RIGHT - lx + 36
        strip.append(f'<circle cx="{lx - 12:.1f}" cy="{STRIP + 30}" r="4" fill="#34d399"/>'
                     + text(round(lx, 1), STRIP + 34.5, 13, "#6ee7b7", label, SANS, 500))
    marks, bottom = layout(words(s), STRIP + 14, reserve)
    strip += marks
    H = bottom + 18
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 {H}" width="880" height="{H}" role="img" aria-label="{esc(NAME)}, full-stack engineer">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{NAVY}"/><stop offset="1" stop-color="{NAVY2}"/></linearGradient>
<linearGradient id="mk" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#67e8f9"/><stop offset=".55" stop-color="{CYAN}"/><stop offset="1" stop-color="{CYAN2}"/></linearGradient>
<radialGradient id="fade" cx=".82" cy=".5" r=".6"><stop offset="0" stop-color="white" stop-opacity=".9"/><stop offset="1" stop-color="white" stop-opacity="0"/></radialGradient>
<mask id="gridmask"><rect width="880" height="{STRIP}" fill="url(#fade)"/></mask>
<mask id="cut"><rect width="64" height="64" fill="white"/><rect x="29" y="16" width="6" height="32" rx="3" fill="black"/><path d="M17 20 L27 20 L27 26 L21 30 L15 27 Z" fill="black"/><path d="M47 44 L37 44 L37 38 L43 34 L49 37 Z" fill="black"/></mask>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
</defs>
<rect width="880" height="{H}" rx="10" fill="url(#bg)"/>
<g fill="none" stroke="#164e63" stroke-width="1" mask="url(#gridmask)">{hex_grid(STRIP)}</g>
<circle cx="740" cy="92" r="78" fill="none" stroke="{CYAN}" stroke-opacity=".16"/>
<g transform="translate(680 32) scale(1.875)"><path d="{HEX}" fill="{CYAN}" opacity=".45" filter="url(#glow)"/><path d="{HEX}" fill="url(#mk)" mask="url(#cut)"/></g>
{text(48, 56, 12, CYAN, ROLE, MONO, 500, "2.5")}
{text(46, 102, 42, INK, NAME, SANS, 700, "-0.5")}
<rect x="48" y="120" width="56" height="3" rx="1.5" fill="{CYAN}"/>
{text(48, 152, 15, MUTED, TAGLINE)}
<path d="M0 {STRIP} H880 V{H-10} a10 10 0 0 1 -10 10 H10 a10 10 0 0 1 -10 -10 Z" fill="#030b17"/>
<line x1="0" y1="{STRIP}" x2="880" y2="{STRIP}" stroke="#123040"/>
{"".join(strip)}
</svg>
'''


if __name__ == "__main__":
    s = survey()
    print(json.dumps(s), file=sys.stderr)
    sys.stdout.write(render(s))
