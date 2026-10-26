"""Generates a Jujutsu Kaisen 'Hollow Purple' animation over your GitHub contribution grid.

Gojo's Blue and Red orbs appear, collide, and fire Hollow Purple across the
grid, erasing every contribution square in its path. The grid then regrows.
Run: python scripts/hollow_purple.py <github-username> <output.svg>
"""
import re
import sys
import urllib.request

USER = sys.argv[1] if len(sys.argv) > 1 else "uri-el"
OUT = sys.argv[2] if len(sys.argv) > 2 else "dist/hollow-purple.svg"

req = urllib.request.Request(
    f"https://github.com/users/{USER}/contributions",
    headers={"User-Agent": "Mozilla/5.0"},
)
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")

cells = {}
for td in re.findall(r"<td[^>]*ContributionCalendar-day[^>]*>", html):
    m = re.search(r'id="contribution-day-component-(\d+)-(\d+)"', td)
    lv = re.search(r'data-level="(\d)"', td)
    if m and lv:
        cells[(int(m.group(2)), int(m.group(1)))] = int(lv.group(1))  # (col,row)

total_m = re.search(r"([\d,]+)\s+contributions?\s+in the last year", html)
total = total_m.group(1) if total_m else "?"

COLS = max(c for c, _ in cells) + 1 if cells else 53
CELL, GAP = 11, 3
STEP = CELL + GAP
W = 1000
GX = (W - COLS * STEP) // 2
GY = 70
H = GY + 7 * STEP + 50
CY = GY + 3.5 * STEP

# Cursed energy shades: empty -> deep void, high -> bright purple
COLORS = ["#1a1030", "#3b1a5c", "#5b2a86", "#8a4fd1", "#c9a6ff"]

DUR = 9  # seconds per loop
SWEEP_START, SWEEP_END = 3.2, 6.4  # when the purple blast crosses the grid
x_start, x_end = 60, GX + COLS * STEP + 40


def pct(t):
    return f"{t / DUR * 100:.2f}%"


rects = []
for (c, r), lv in sorted(cells.items()):
    x, y = GX + c * STEP, GY + r * STEP
    cx = x + CELL / 2
    hit = SWEEP_START + (cx - x_start) / (x_end - x_start) * (SWEEP_END - SWEEP_START)
    rects.append(
        f'<rect class="d" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
        f'fill="{COLORS[lv]}" style="animation-delay:{hit - 0.15:.2f}s;'
        f'transform-origin:{cx}px {y + CELL / 2}px"/>'
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <radialGradient id="blue"><stop offset="0" stop-color="#ffffff"/><stop offset=".35" stop-color="#6ec6ff"/><stop offset="1" stop-color="#1e5bff" stop-opacity="0"/></radialGradient>
  <radialGradient id="red"><stop offset="0" stop-color="#ffffff"/><stop offset=".35" stop-color="#ff6b6b"/><stop offset="1" stop-color="#e63946" stop-opacity="0"/></radialGradient>
  <radialGradient id="purple"><stop offset="0" stop-color="#ffffff"/><stop offset=".3" stop-color="#e0c3ff"/><stop offset=".6" stop-color="#9b4dff"/><stop offset="1" stop-color="#5b2a86" stop-opacity="0"/></radialGradient>
  <linearGradient id="trail" x1="0" x2="1"><stop offset="0" stop-color="#9b4dff" stop-opacity="0"/><stop offset="1" stop-color="#c9a6ff" stop-opacity=".55"/></linearGradient>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
  * {{ animation-duration:{DUR}s; animation-iteration-count:infinite; animation-timing-function:linear; }}
  .d {{ animation-name:erase; }}
  @keyframes erase {{
    0% {{ opacity:1; transform:scale(1); filter:brightness(1); }}
    1.5% {{ opacity:1; transform:scale(1.6); filter:brightness(4); }}
    4% {{ opacity:0; transform:scale(0); filter:brightness(1); }}
    {pct(2.5)} {{ opacity:0; transform:scale(0); }}
    {pct(3.1)} {{ opacity:1; transform:scale(1); filter:brightness(1); }}
    100% {{ opacity:1; transform:scale(1); filter:brightness(1); }}
  }}
  .blue {{ animation-name:blue; }}
  @keyframes blue {{
    0% {{ transform:translate(60px,{CY - 28}px) scale(0); opacity:0; }}
    {pct(0.4)} {{ transform:translate(60px,{CY - 28}px) scale(1); opacity:1; }}
    {pct(2.2)} {{ transform:translate(60px,{CY - 28}px) scale(1.1); opacity:1; }}
    {pct(2.9)} {{ transform:translate(60px,{CY}px) scale(.6); opacity:1; }}
    {pct(3.0)}, 100% {{ transform:translate(60px,{CY}px) scale(0); opacity:0; }}
  }}
  .red {{ animation-name:red; }}
  @keyframes red {{
    0%, {pct(0.8)} {{ transform:translate(60px,{CY + 28}px) scale(0); opacity:0; }}
    {pct(1.2)} {{ transform:translate(60px,{CY + 28}px) scale(1); opacity:1; }}
    {pct(2.2)} {{ transform:translate(60px,{CY + 28}px) scale(1.1); opacity:1; }}
    {pct(2.9)} {{ transform:translate(60px,{CY}px) scale(.6); opacity:1; }}
    {pct(3.0)}, 100% {{ transform:translate(60px,{CY}px) scale(0); opacity:0; }}
  }}
  .hp {{ animation-name:hp; }}
  @keyframes hp {{
    0%, {pct(2.9)} {{ transform:translate(60px,{CY}px) scale(0); opacity:0; }}
    {pct(3.2)} {{ transform:translate({x_start}px,{CY}px) scale(1.3); opacity:1; }}
    {pct(SWEEP_END)} {{ transform:translate({x_end}px,{CY}px) scale(1.3); opacity:1; }}
    {pct(SWEEP_END + 0.4)}, 100% {{ transform:translate({x_end + 120}px,{CY}px) scale(2); opacity:0; }}
  }}
  .flash {{ animation-name:flash; }}
  @keyframes flash {{
    0%, {pct(2.9)} {{ opacity:0; }}
    {pct(3.0)} {{ opacity:.85; }}
    {pct(3.5)}, 100% {{ opacity:0; }}
  }}
  .t1 {{ animation-name:t1; }} .t2 {{ animation-name:t2; }} .t3 {{ animation-name:t3; }} .t4 {{ animation-name:t4; }}
  @keyframes t1 {{ 0%,{pct(0.2)} {{opacity:0}} {pct(0.5)},{pct(1.0)} {{opacity:1}} {pct(1.2)},100% {{opacity:0}} }}
  @keyframes t2 {{ 0%,{pct(1.2)} {{opacity:0}} {pct(1.4)},{pct(2.0)} {{opacity:1}} {pct(2.2)},100% {{opacity:0}} }}
  @keyframes t3 {{ 0%,{pct(2.2)} {{opacity:0}} {pct(2.4)},{pct(2.9)} {{opacity:1}} {pct(3.0)},100% {{opacity:0}} }}
  @keyframes t4 {{ 0%,{pct(3.0)} {{opacity:0}} {pct(3.3)},{pct(7.6)} {{opacity:1}} {pct(8.0)},100% {{opacity:0}} }}
  text {{ font-family:'Segoe UI',Helvetica,Arial,sans-serif; }}
</style>
<rect width="{W}" height="{H}" rx="12" fill="#0d0221"/>
<text x="{W/2}" y="38" fill="#b388ff" font-size="20" font-weight="700" text-anchor="middle" class="t1">Cursed Technique Lapse: Blue</text>
<text x="{W/2}" y="38" fill="#ff6b6b" font-size="20" font-weight="700" text-anchor="middle" class="t2">Reversal: Red</text>
<text x="{W/2}" y="38" fill="#ffffff" font-size="20" font-weight="700" text-anchor="middle" class="t3">Combine them...</text>
<text x="{W/2}" y="38" fill="#e0c3ff" font-size="24" font-weight="800" text-anchor="middle" class="t4" filter="url(#glow)">HOLLOW PURPLE</text>
{"".join(rects)}
<g class="hp"><rect x="-260" y="-26" width="260" height="52" rx="26" fill="url(#trail)"/><circle r="42" fill="url(#purple)" filter="url(#glow)"/></g>
<g class="blue"><circle r="26" fill="url(#blue)" filter="url(#glow)"/></g>
<g class="red"><circle r="26" fill="url(#red)" filter="url(#glow)"/></g>
<rect class="flash" width="{W}" height="{H}" rx="12" fill="#e0c3ff" opacity="0"/>
<text x="{GX}" y="{H - 18}" fill="#8a7aa8" font-size="13">{total} contributions in the last year · erased by Gojo Satoru</text>
<text x="{W - GX}" y="{H - 18}" fill="#8a7aa8" font-size="13" text-anchor="end">Throughout Heaven and Earth, I alone commit.</text>
</svg>'''

import os
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"Wrote {OUT} ({len(cells)} days, {total} contributions)")
