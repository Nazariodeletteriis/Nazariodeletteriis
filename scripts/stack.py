"""Build assets/stack.svg: skillicons tiles plus tiles skillicons lacks. Needs network.

python scripts/stack.py
"""
import re, urllib.request

PERLINE, STEP = 10, 300
TILE = '<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" fill="none" viewBox="0 0 256 256"><rect width="256" height="256" fill="#242938" rx="60"/>{}</svg>'
# name -> tile; a plain name is fetched from skillicons, the rest are drawn here
SIMPLE = "https://cdn.jsdelivr.net/npm/simple-icons@13.21.0/icons/shopify.svg"
ICONS = ["php", "js", "ts", "react", "nextjs", "nodejs", "python", "rust", "postgres", "wordpress",
         "laravel", "shopify", "liquid", "hydrogen", "remix", "prisma", "docker", "git", "github"]


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "stack.py"}), timeout=30).read().decode()


def custom(name):
    if name == "shopify":  # official glyph from simple-icons, brand green
        d = re.search(r' d="([^"]+)"', get(SIMPLE)).group(1)
        return TILE.format(f'<path fill="#95BF47" transform="translate(53 53) scale(6.67)" d="{d}"/>')
    if name == "liquid":  # a droplet
        return TILE.format('<path fill="#95BF47" d="M128 50C128 50 70 120 70 154a58 58 0 0 0 116 0C186 120 128 50 128 50z"/>'
                           '<path fill="#fff" fill-opacity=".35" d="M104 150a24 24 0 0 0 20 28 24 24 0 0 1-20-28z"/>')
    if name == "hydrogen":  # the element symbol
        return TILE.format('<text x="128" y="160" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace" '
                           'font-size="104" font-weight="700" fill="#fff">H<tspan font-size="56" dy="22" fill="#95BF47">2</tspan></text>')


def tile(name):
    if name in ("shopify", "liquid", "hydrogen"):
        return custom(name)
    return re.search(r'<g transform="translate\(0, 0\)">\s*(<svg.*</svg>)\s*</g>', get(f"https://skillicons.dev/icons?i={name}"), re.S).group(1).strip()


rows = -(-len(ICONS) // PERLINE)
w, h = PERLINE * 256 + (PERLINE - 1) * 44, rows * 256 + (rows - 1) * 44
out = [f'<svg width="{w * .1875:.2f}" height="{h * .1875:.2f}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg">']
for i, n in enumerate(ICONS):
    out.append(f'<g transform="translate({i % PERLINE * STEP}, {i // PERLINE * STEP})">{tile(n)}</g>')
out.append("</svg>")
open("assets/stack.svg", "w").write("\n".join(out))
