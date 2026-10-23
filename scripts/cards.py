"""Render a GitHub stats card as light/dark SVG. Stdlib only.

python scripts/cards.py --user NAME --out assets
writes assets/card-stats-dark.svg and assets/card-stats-light.svg

$GITHUB_TOKEN unlocks the contribution and streak tiles (GraphQL); without it
the card renders with the first three tiles only.
"""
import argparse, datetime as dt, json, os, urllib.request

THEMES = {
    "dark":  dict(bg="#0d1117", border="#30363d", title="#34d399", value="#f0f6fc", muted="#8b949e"),
    "light": dict(bg="#ffffff", border="#d0d7de", title="#047857", value="#0d1117", muted="#57606a"),
}
QUERY = """query($l:String!){user(login:$l){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date contributionCount}}}}}}"""


def call(url, token, body=None):
    h = {"User-Agent": "cards.py"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    if body:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, json.dumps(body).encode() if body else None, h)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def contributions(user, token):
    """(total, current streak, longest streak), or None when unavailable."""
    if not token:
        return None
    try:
        d = call("https://api.github.com/graphql", token, {"query": QUERY, "variables": {"l": user}})
        cal = d["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    except Exception as e:
        print("contributions unavailable:", e)
        return None
    days = sorted((x["date"], x["contributionCount"]) for w in cal["weeks"] for x in w["contributionDays"])
    longest = run = 0
    for _, c in days:
        run = run + 1 if c else 0
        longest = max(longest, run)
    cur = 0
    for i, (_, c) in enumerate(reversed(days)):
        if c:
            cur += 1
        elif i:  # an empty today does not break yesterday's streak
            break
    return cal["totalContributions"], cur, longest


def render(tiles, name, t):
    cols, tw, th = 3, 150, 72
    rows = -(-len(tiles) // cols)
    w, h = 40 + cols * tw, 70 + rows * th
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
         f'font-family="ui-sans-serif,-apple-system,Segoe UI,Helvetica,Arial,sans-serif">',
         f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="10" fill="{t["bg"]}" stroke="{t["border"]}"/>',
         f'<text x="20" y="34" font-size="16" font-weight="600" fill="{t["title"]}">{name} · GitHub</text>']
    for i, (label, val) in enumerate(tiles):
        x, y = 20 + (i % cols) * tw, 62 + (i // cols) * th
        o.append(f'<text x="{x}" y="{y + 22}" font-size="26" font-weight="700" fill="{t["value"]}">{val:,}</text>')
        o.append(f'<text x="{x}" y="{y + 42}" font-size="12" fill="{t["muted"]}">{label}</text>')
    return "\n".join(o + ["</svg>"])


p = argparse.ArgumentParser()
p.add_argument("--user", required=True)
p.add_argument("--out", default="assets")
a = p.parse_args()
token = os.environ.get("GITHUB_TOKEN")
u = call(f"https://api.github.com/users/{a.user}", token)
repos = call(f"https://api.github.com/users/{a.user}/repos?per_page=100&type=owner", token)
tiles = [("Public repos", u["public_repos"]),
         ("Stars earned", sum(r["stargazers_count"] for r in repos)),
         ("Followers", u["followers"])]
c = contributions(a.user, token)
if c:
    tiles += [("Contributions, last year", c[0]), ("Current streak (days)", c[1]), ("Longest streak (days)", c[2])]
for n, t in THEMES.items():
    open(f"{a.out}/card-stats-{n}.svg", "w").write(render(tiles, u["name"] or a.user, t))
