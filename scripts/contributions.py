#!/usr/bin/env python3
"""Render assets/contributions.svg: your contribution graph, fading in left to right.

Usage:
  GITHUB_TOKEN=... python scripts/contributions.py            # real data (GitHub GraphQL API)
  python scripts/contributions.py --sample                    # offline preview with fake data

Standard library only. Run by .github/workflows/contributions.yml every day.
"""
import datetime as dt
import json
import os
import random
import sys
import urllib.request

USER = os.environ.get("PROFILE_USER", "JerryX2007")
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "contributions.svg")

LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date weekday contributionCount contributionLevel } }
      }
    }
  }
}"""


def fetch_real():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set (use --sample for an offline preview).")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        sys.exit(f"GraphQL error: {payload['errors']}")
    cal = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [
        [
            {
                "date": dt.date.fromisoformat(d["date"]),
                "weekday": d["weekday"],
                "count": d["contributionCount"],
                "level": LEVELS.get(d["contributionLevel"], 0),
            }
            for d in w["contributionDays"]
        ]
        for w in cal["weeks"]
    ]
    return cal["totalContributions"], weeks


def fake_data():
    rnd = random.Random(2007)
    today = dt.date.today()
    start = today - dt.timedelta(days=(today.weekday() + 1) % 7 + 52 * 7)
    weeks, total = [], 0
    for w in range(53):
        days = []
        for d in range(7):
            date = start + dt.timedelta(days=w * 7 + d)
            if date > today:
                break
            r = rnd.random() * (0.55 if d in (0, 6) else 1)
            level = 0 if r < 0.25 else 1 if r < 0.45 else 2 if r < 0.65 else 3 if r < 0.82 else 4
            count = 0 if level == 0 else level * 2 + rnd.randint(0, 3)
            total += count
            days.append({"date": date, "weekday": d, "count": count, "level": level})
        weeks.append(days)
    return total, weeks


def ordinal(n):
    return f"{n}{'th' if 11 <= n % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def render(total, weeks, sample=False):
    cell, gap = 15, 4
    step = cell + gap
    left, top = 72, 104
    width = left + len(weeks) * step + 32
    height = top + 7 * step + 58
    out = []
    a = out.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
      f'role="img" aria-label="{total} contributions in the last year">')
    a("<style>"
      "text{font-family:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}"
      ".m{fill:#9198a1;font-size:11px}"
      ".c{opacity:0;animation:in .55s cubic-bezier(.2,.8,.2,1) forwards;transform-box:fill-box;transform-origin:center}"
      "@keyframes in{from{opacity:0;transform:translateX(-8px) scale(.6)}to{opacity:1;transform:none}}"
      "@media (prefers-reduced-motion:reduce){.c{animation:none;opacity:1}}"
      "</style>")
    a(f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="12" fill="#010409" stroke="#30363d"/>')
    a('<text x="32" y="44" font-size="17" font-weight="700" fill="#e6edf3">'
      '<tspan fill="#3fb950">$</tspan> git log --since="1 year ago"</text>')
    caption = "sample data · run the workflow for real numbers" if sample else f"{total:,} contributions in the last year"
    a(f'<text x="32" y="68" font-size="13" fill="#9198a1">{caption}</text>')

    last_month = None
    for i, week in enumerate(weeks):
        if not week:
            continue
        first = week[0]["date"]
        if first.month != last_month and first.day <= 7 and i < len(weeks) - 2:
            a(f'<text class="m" x="{left + i * step}" y="{top - 10}">{MONTHS[first.month - 1]}</text>')
        last_month = first.month
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        a(f'<text class="m" x="32" y="{top + row * step + 11}">{label}</text>')

    for i, week in enumerate(weeks):
        for d in week:
            x, y = left + i * step, top + d["weekday"] * step
            delay = i * 26 + d["weekday"] * 9
            n = d["count"]
            tip = f'{"No" if n == 0 else n} contribution{"" if n == 1 else "s"} on {MONTHS[d["date"].month - 1]} {ordinal(d["date"].day)}'
            stroke = ' stroke="#21262d"' if d["level"] == 0 else ""
            a(f'<rect class="c" style="animation-delay:{delay}ms" x="{x}" y="{y}" width="{cell}" height="{cell}" '
              f'rx="3" fill="{COLORS[d["level"]]}"{stroke}><title>{tip}</title></rect>')

    ly = height - 30
    lx = width - 32 - 5 * 17 - 70
    a(f'<text class="m" x="{lx - 38}" y="{ly + 11}">less</text>')
    for k, color in enumerate(COLORS):
        stroke = ' stroke="#21262d"' if k == 0 else ""
        a(f'<rect x="{lx + k * 17}" y="{ly}" width="13" height="13" rx="3" fill="{color}"{stroke}/>')
    a(f'<text class="m" x="{lx + 5 * 17 + 6}" y="{ly + 11}">more</text>')
    a("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    sample = "--sample" in sys.argv
    total, weeks = fake_data() if sample else fetch_real()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(total, weeks, sample))
    print(f"wrote {os.path.normpath(OUT)} ({total} contributions)")
