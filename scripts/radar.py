"""Draw a radar chart as light/dark SVG from a JSON file. Stdlib only.

python scripts/radar.py --data assets/skills.json -o assets/radar [--values]
writes assets/radar-dark.svg and assets/radar-light.svg
"""
import argparse, json, math

THEMES = {
    "dark":  dict(grid="#30363d", text="#c9d1d9", accent="#34d399"),
    "light": dict(grid="#d0d7de", text="#24292f", accent="#047857"),
}
W, H, CX, CY, R = 520, 400, 260, 200, 120


def render(axes, t, show_values):
    n = len(axes)

    def pt(i, r):
        a = -math.pi / 2 + 2 * math.pi * i / n
        return CX + r * math.cos(a), CY + r * math.sin(a)

    def poly(rs):
        return " ".join("%.1f,%.1f" % pt(i, r) for i, r in enumerate(rs))

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
           f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="12">']
    for k in range(1, 5):
        out.append(f'<polygon points="{poly([R * k / 4] * n)}" fill="none" stroke="{t["grid"]}"/>')
    for i in range(n):
        x, y = pt(i, R)
        out.append(f'<line x1="{CX}" y1="{CY}" x2="{x:.1f}" y2="{y:.1f}" stroke="{t["grid"]}"/>')
    out.append(f'<polygon points="{poly([R * a["value"] / 100 for a in axes])}" '
               f'fill="{t["accent"]}" fill-opacity=".25" stroke="{t["accent"]}" stroke-width="2"/>')
    for i, a in enumerate(axes):
        x, y = pt(i, R + 16)
        c = math.cos(-math.pi / 2 + 2 * math.pi * i / n)
        anchor = "middle" if abs(c) < .25 else ("start" if c > 0 else "end")
        label = a["label"] + (f' · {a["value"]}' if show_values else "")
        out.append(f'<text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="{anchor}" fill="{t["text"]}">{label}</text>')
    out.append("</svg>")
    return "\n".join(out)


p = argparse.ArgumentParser()
p.add_argument("--data", required=True)
p.add_argument("-o", required=True, help="output prefix")
p.add_argument("--values", action="store_true")
a = p.parse_args()
axes = json.load(open(a.data))["axes"]
for name, theme in THEMES.items():
    open(f"{a.o}-{name}.svg", "w").write(render(axes, theme, a.values))
