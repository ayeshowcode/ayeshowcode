"""Builds assets/card-dark.svg and assets/card-light.svg from live GitHub data.

Standard library only. Run: python scripts/build_card.py
Set GITHUB_TOKEN to avoid the anonymous API rate limit (optional).
"""
import datetime as dt
import html
import json
import os
import re
import urllib.request
from pathlib import Path

USER = "ayeshowcode"
NAME = "Ayesh Qureshi"
TAGLINE = "Multi-agent systems and LLM pipelines that actually work."
ABOUT = [
    ("role", "CS undergrad, focused on AI engineering"),
    ("school", "FAST-NUCES Karachi"),
    ("based", "Karachi, Pakistan"),
    ("now", "Gatekeeper, a RAG agent that cannot regress"),
]
# Repo name -> one-line description shown in the projects table.
FEATURED = [
    ("Gatekeeper", "RAG agent that gates its own lessons, no regressions"),
    ("RedHanded", "flags code that breaks your own security policies"),
    ("LoopAI", "end-to-end RAG pipeline on LangGraph and FastAPI"),
    ("AutoStartup", "multi-agent startup builder for founders in Pakistan"),
]
STACK = [
    ("ai", ["LangGraph", "LangChain", "LangSmith", "Claude API", "OpenAI API", "Agentic RAG"]),
    ("backend", ["Python", "FastAPI", "PostgreSQL", "MongoDB", "Redis", "Celery"]),
    ("frontend", ["Next.js", "React", "TypeScript", "Tailwind"]),
    ("infra", ["Docker", "GitHub Actions", "n8n", "MCP"]),
]

THEMES = {
    "dark": dict(bg="#0d1117", border="#30363d", fg="#e6edf3", muted="#8b949e",
                 dim="#484f58", accent="#a78bfa", green="#3fb950", track="#21262d"),
    "light": dict(bg="#ffffff", border="#d0d7de", fg="#1f2328", muted="#656d76",
                  dim="#afb8c1", accent="#7c3aed", green="#1a7f37", track="#eaeef2"),
}
W = 880
FONT = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
CH = 7.83  # width of one 13px monospace character


def get(url, as_json=True):
    req = urllib.request.Request(url, headers={"User-Agent": "profile-card"})
    token = os.environ.get("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode("utf-8")
    return json.loads(body) if as_json else body


def contributions():
    """Daily contribution counts for the last year, oldest first."""
    page = get(f"https://github.com/users/{USER}/contributions", as_json=False)
    dates = {}
    for tag in re.findall(r"<td[^>]*ContributionCalendar-day[^>]*>", page):
        d = re.search(r'data-date="([\d-]+)"', tag)
        i = re.search(r'id="([^"]+)"', tag)
        if d and i:
            dates[i.group(1)] = d.group(1)
    counts = {d: 0 for d in dates.values()}
    for ref, text in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', page):
        m = re.match(r"\s*(\d+) contribution", text)
        if ref in dates and m:
            counts[dates[ref]] = int(m.group(1))
    return sorted(counts.items())


def esc(s):
    return html.escape(str(s), quote=True)


def text(x, y, s, fill, size=13, weight=None, anchor=None, cls=None):
    extra = ""
    if weight:
        extra += f' font-weight="{weight}"'
    if anchor:
        extra += f' text-anchor="{anchor}"'
    if cls:
        extra += f' class="{cls}"'
    return f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-size="{size}"{extra}>{esc(s)}</text>'


def panel(c, x, y, w, h, title):
    tw = len(title) * 7.0 + 14
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="none" stroke="{c["border"]}"/>'
        f'<rect x="{x + 12}" y="{y - 8}" width="{tw:.0f}" height="16" fill="{c["bg"]}"/>'
        + text(x + 19, y + 4, title, c["muted"], 11.5)
    )


def build(theme, user, repos, days):
    c = THEMES[theme]
    out = []
    today = dt.date.today()

    # ---- header
    out.append(text(22, 34, f"{USER}", c["accent"], 13, 700))
    out.append(text(22 + (len(USER) + 1) * CH, 34, "~ github since "
                    + user["created_at"][:4], c["muted"]))
    out.append(text(W - 22, 34, f'{user["public_repos"]} repos · {user["followers"]} followers',
                    c["muted"], 13, anchor="end"))

    # ---- whoami
    x, y, w, h = 20, 58, 500, 190
    out.append(panel(c, x, y, w, h, "whoami"))
    out.append(text(x + 20, y + 52, NAME, c["fg"], 27, 700))
    out.append(f'<rect class="cur" x="{x + 20 + len(NAME) * 16.0 + 6:.0f}" y="{y + 30}" '
               f'width="11" height="24" fill="{c["accent"]}"/>')
    out.append(text(x + 20, y + 78, TAGLINE, c["muted"]))
    for i, (k, v) in enumerate(ABOUT):
        yy = y + 110 + i * 22
        out.append(text(x + 20, yy, k, c["accent"]))
        out.append(text(x + 20 + 8 * CH, yy, v, c["fg"]))

    # ---- activity
    x, y, w, h = 532, 58, 328, 190
    out.append(panel(c, x, y, w, h, "activity"))
    total = sum(n for _, n in days)
    out.append(text(x + 20, y + 46, f"{total:,}", c["accent"], 25, 700))
    out.append(text(x + 20 + len(f"{total:,}") * 15.1 + 8, y + 46,
                    "contributions this year", c["muted"], 12))
    weeks = [sum(n for _, n in days[i:i + 7]) for i in range(len(days) % 7, len(days), 7)][-26:]
    top = max(weeks + [1])
    for i, n in enumerate(weeks):
        bh = max(2, round(72 * (n / top) ** 0.5))
        bx = x + 20 + i * 11.1
        fill = c["accent"] if n else c["track"]
        op = "" if not n else f' opacity="{0.45 + 0.55 * n / top:.2f}"'
        out.append(f'<rect class="bar" style="animation-delay:{i * 0.03:.2f}s" x="{bx:.1f}" '
                   f'y="{y + 142 - bh}" width="8" height="{bh}" rx="1.5" fill="{fill}"{op}/>')
    streak = 0
    for d, n in reversed(days):
        if n:
            streak += 1
        elif d != today.isoformat():
            break
    out.append(text(x + 20, y + 168, "26 wks, sqrt", c["muted"], 11.5))
    out.append(text(x + w - 20, y + 168, f"streak {streak}d · best week {top}",
                    c["muted"], 11.5, anchor="end"))

    # ---- projects
    x, y, w, h = 20, 266, 840, 160
    out.append(panel(c, x, y, w, h, "projects"))
    cols = [("#", 20), ("name", 62), ("what it does", 206), ("lang", 640), ("last push", 740)]
    for label, cx in cols:
        out.append(text(x + cx, y + 30, label, c["muted"], 11.5))
    out.append(f'<line x1="{x + 16}" y1="{y + 40}" x2="{x + w - 16}" y2="{y + 40}" stroke="{c["border"]}"/>')
    by_name = {r["name"]: r for r in repos}
    for i, (name, desc) in enumerate(FEATURED):
        r = by_name.get(name, {})
        yy = y + 64 + i * 26
        out.append(text(x + 20, yy, f"{i + 1:02d}", c["dim"]))
        out.append(text(x + 62, yy, name, c["fg"], 13, 700))
        out.append(text(x + 206, yy, desc, c["muted"]))
        out.append(text(x + 640, yy, r.get("language") or "-", c["fg"]))
        if r.get("homepage"):
            out.append(f'<circle class="pulse" cx="{x + 745}" cy="{yy - 4.5}" r="4" fill="{c["green"]}"/>')
            out.append(text(x + 757, yy, "live demo", c["green"]))
        else:
            pushed = dt.date.fromisoformat(r["pushed_at"][:10]).strftime("%b %Y") if r else "-"
            out.append(text(x + 740, yy, pushed, c["muted"]))

    # ---- stack
    x, y, w, h = 20, 444, 840, 146
    out.append(panel(c, x, y, w, h, "stack"))
    for i, (group, tools) in enumerate(STACK):
        yy = y + 22 + i * 30
        out.append(text(x + 20, yy + 15, group, c["accent"]))
        cx = x + 20 + 11 * CH
        for tool in tools:
            tw = len(tool) * 7.0 + 18
            out.append(f'<rect x="{cx:.0f}" y="{yy}" width="{tw:.0f}" height="22" rx="5" '
                       f'fill="none" stroke="{c["border"]}"/>')
            out.append(text(cx + 9, yy + 15, tool, c["fg"], 11.5))
            cx += tw + 8

    H = 626
    out.append(text(W - 22, H - 14, f"updated {today.isoformat()} from live GitHub data",
                    c["dim"], 11, anchor="end"))

    style = (
        "@keyframes blink{50%{opacity:0}}"
        "@keyframes pulse{50%{opacity:.35}}"
        "@keyframes rise{from{transform:scaleY(0)}to{transform:scaleY(1)}}"
        "@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
        ".cur{animation:blink 1.1s steps(1) infinite}"
        ".pulse{animation:pulse 2s ease-in-out infinite}"
        ".bar{transform-box:fill-box;transform-origin:bottom;animation:rise .7s ease-out both}"
        ".grow{transform-box:fill-box;transform-origin:left;animation:grow .9s ease-out both}"
        "@media (prefers-reduced-motion:reduce){.cur,.pulse,.bar,.grow{animation:none}}"
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="{FONT}" role="img" aria-label="{esc(NAME)}: {esc(TAGLINE)}">'
        f"<style>{style}</style>"
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{c["bg"]}" stroke="{c["border"]}"/>'
        + "".join(out) + "</svg>\n"
    )


def main():
    user = get(f"https://api.github.com/users/{USER}")
    repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100")
    days = contributions()
    assets = Path(__file__).resolve().parent.parent / "assets"
    assets.mkdir(exist_ok=True)
    for theme in THEMES:
        (assets / f"card-{theme}.svg").write_text(build(theme, user, repos, days), encoding="utf-8")
    print(f"built cards: {sum(n for _, n in days)} contributions over {len(days)} days")


if __name__ == "__main__":
    main()
