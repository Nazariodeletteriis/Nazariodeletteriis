"""Build the animated ASCII-portrait banner (light/dark SVG). Needs Pillow + numpy.

python scripts/portrait.py --photo foto.jpg --crop 100,40,700,760 -o assets
writes assets/banner-dark.svg and assets/banner-light.svg
"""
import argparse
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

RAMP = " .,:;-=+*#%@"
COLS, CW, LH = 90, 5, 9  # columns, char width, line height (px)
W = 1000
THEMES = {
    "dark":  dict(bg="#0d1117", bar="#161b22", border="#30363d", accent="#34d399",
                  text="#c9d1d9", muted="#8b949e", strong="#f0f6fc", invert=False),
    "light": dict(bg="#ffffff", bar="#f6f8fa", border="#d0d7de", accent="#047857",
                  text="#24292f", muted="#57606a", strong="#0d1117", invert=True),
}


def ascii_rows(photo, crop, invert):
    """Rows of (char, '#rrggbb'): char density from luminance, colour from the photo."""
    img = Image.open(photo).convert("RGB").crop(crop)
    rows = round(COLS * img.height / img.width * CW / LH)
    img = img.resize((COLS * 4, rows * 4), Image.LANCZOS).filter(ImageFilter.UnsharpMask(3, 120, 3))
    img = ImageEnhance.Color(img.resize((COLS, rows), Image.LANCZOS)).enhance(1.35)
    rgb = np.asarray(img)
    lum = np.asarray(ImageOps.autocontrast(img.convert("L"), cutoff=1), dtype=float) / 255
    if invert:
        lum = 1 - lum
    idx = (lum ** 0.8 * (len(RAMP) - 1)).round().astype(int)
    return [[(RAMP[idx[y, x]], "#%02x%02x%02x" % tuple(rgb[y, x])) for x in range(COLS)] for y in range(rows)]


def build(rows, t):
    h = 60 + len(rows) * LH + 30
    rx = 36 + COLS * CW + 50  # text column
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" '
         f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
         '<style>'
         '.r{opacity:0;animation:in .35s ease-out forwards}@keyframes in{to{opacity:1}}'
         '.s{animation:sc 7s ease-in-out 3s infinite}'
         f'@keyframes sc{{0%{{transform:translateY(0)}}45%,100%{{transform:translateY({len(rows) * LH}px)}}}}'
         '.c{animation:b 1.1s steps(1) infinite}@keyframes b{50%{opacity:0}}'
         '@media (prefers-reduced-motion:reduce){.r{opacity:1;animation:none}.s,.c{animation:none}.s{display:none}}'
         '</style>',
         f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="0"/>'
         f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity=".35"/></linearGradient>'
         f'<clipPath id="k"><rect x="36" y="60" width="{COLS * CW}" height="{len(rows) * LH}"/></clipPath></defs>',
         f'<rect x="1" y="1" width="{W - 2}" height="{h - 2}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>',
         f'<path d="M1 13a12 12 0 0 1 12-12h{W - 26}a12 12 0 0 1 12 12v30H1z" fill="{t["bar"]}"/>',
         '<circle cx="26" cy="22" r="6" fill="#ff5f56"/><circle cx="48" cy="22" r="6" fill="#ffbd2e"/><circle cx="70" cy="22" r="6" fill="#27c93f"/>',
         f'<text x="{W // 2}" y="27" text-anchor="middle" font-size="13" fill="{t["muted"]}">nazario@letrion-lab: ~</text>',
         f'<g font-size="8.6" style="white-space:pre" xml:space="preserve">']
    for i, r in enumerate(rows):
        cells = "".join(f'<tspan fill="{c}">{ch}</tspan>' if ch != " " else " " for ch, c in r).rstrip()
        o.append(f'<text class="r" style="animation-delay:{0.4 + i * 0.05:.2f}s" x="36" y="{70 + i * LH}">{cells}</text>')
    o.append('</g>')
    o.append(f'<g clip-path="url(#k)"><rect class="s" x="36" y="{60 - 24}" width="{COLS * CW}" height="24" fill="url(#g)"/></g>')
    mid = 60 + len(rows) * LH // 2
    ty = lambda k: mid - 90 + k
    o += [f'<g font-size="19">',
          f'<text x="{rx}" y="{ty(0)}" fill="{t["accent"]}">~ $ <tspan fill="{t["text"]}">whoami</tspan></text>',
          f'<text x="{rx}" y="{ty(34)}" fill="{t["strong"]}" font-size="26" font-weight="700">Nazario De Letteriis</text>',
          f'<text x="{rx}" y="{ty(62)}" fill="{t["text"]}" font-size="20">Lead Full-Stack Developer</text>',
          f'<text x="{rx}" y="{ty(120)}" fill="{t["accent"]}">~ $ <tspan fill="{t["text"]}">cat stack.txt</tspan></text>',
          f'<text x="{rx}" y="{ty(150)}" fill="{t["muted"]}" font-size="15">php · react · node.js · python</text>',
          f'<text x="{rx}" y="{ty(172)}" fill="{t["muted"]}" font-size="15">wordpress · shopify plus</text>',
          f'<text x="{rx}" y="{ty(228)}" fill="{t["accent"]}">~ $ <tspan fill="{t["text"]}">status --now</tspan></text>',
          f'<text x="{rx}" y="{ty(258)}" fill="{t["strong"]}" font-size="15">open to remote Lead / Senior roles,</text>',
          f'<text x="{rx}" y="{ty(280)}" fill="{t["strong"]}" font-size="15">worldwide<tspan class="c" fill="{t["accent"]}"> ▌</tspan></text>',
          '</g></svg>']
    return "\n".join(o)


p = argparse.ArgumentParser()
p.add_argument("--photo", required=True)
p.add_argument("--crop", required=True, help="left,top,right,bottom in px")
p.add_argument("-o", default="assets")
a = p.parse_args()
crop = tuple(int(x) for x in a.crop.split(","))
for name, t in THEMES.items():
    rows = ascii_rows(a.photo, crop, t["invert"])
    open(f"{a.o}/banner-{name}.svg", "w").write(build(rows, t))
    if name == "dark":
        print("\n".join("".join(ch for ch, _ in r) for r in rows))
