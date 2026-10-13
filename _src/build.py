#!/usr/bin/env python3
"""Builds the DialectForge static site.
 - _src/pages/*.html : content fragments with a small front-matter header -> written to their path
 - WRAP list        : existing pages whose body text is kept verbatim and re-wrapped in the new layout
Run: python3 _src/build.py  (from repo root). Output is plain HTML committed to the repo."""
import os, re, html, copy
from bs4 import BeautifulSoup, Comment
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GTAG = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-SDLC9S27DQ"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-SDLC9S27DQ');</script>"""
MARK = """<svg viewBox="0 0 32 32" aria-hidden="true"><rect x="1" y="1" width="30" height="30" fill="none" stroke="currentColor" stroke-width="2"/><path d="M1 11h6M25 21h6M11 1v6M21 25v6" stroke="currentColor" stroke-width="2"/><text x="16" y="21" text-anchor="middle" font-family="JetBrains Mono,monospace" font-size="12" font-weight="700" fill="#b4441c">df</text></svg>"""
NAV = [("/protocol/","Protocol"),("/#domains","Domains"),("/dfos/","DFoS"),("/download/","Apps"),("/licensing/","Licensing"),("/research","Research"),("/#contact","Contact")]

def header(active):
    items = "".join(f'<a href="{h}"{" aria-current=page" if h==active else ""}>{t}</a>' for h,t in NAV)
    return f"""<a class="skip" href="#content">Skip to content</a>
<header class="mast"><div class="wrap">
<a class="mark" href="/">{MARK}<span>DialectForge <small>LLC · Michigan</small></span></a>
<button class="nav-toggle" aria-expanded="false" aria-controls="nav">Menu</button>
<nav class="nav" id="nav" aria-label="Main">{items}<a class="btn-sm" href="/download/">Downloads</a></nav>
</div></header>"""

FOOTER = """<footer class="foot"><div class="wrap">
<div class="cols">
<div class="about"><a class="mark" href="/" style="color:inherit">"""+MARK+"""<span>DialectForge</span></a>
<p>One protocol, applied everywhere data moves or rests. Built in Michigan by John Martin. Being released as open source under AGPL-3.0.</p></div>
<div><h4>Protocol</h4><ul><li><a href="/protocol/">How it works</a></li><li><a href="/comparison/">Traffic comparison</a></li><li><a href="/research">Research</a></li><li><a href="/licensing/">Licensing</a></li></ul></div>
<div><h4>Domains</h4><ul><li><a href="/dfos/">DFoS</a></li><li><a href="/vpn/">VPN</a></li><li><a href="/mesh/">Mesh</a></li><li><a href="/terminal/">Terminal</a></li><li><a href="/messenger/">Messenger</a></li><li><a href="/automotive/">Automotive</a></li><li><a href="/banking/">Banking</a></li><li><a href="/verify/">Verify</a></li><li><a href="/ai-factory/">AI Factory / Lu</a></li><li><a href="/enterprise/">Enterprise</a></li></ul></div>
<div><h4>Apps</h4><ul><li><a href="/download/">Downloads</a></li><li><a href="/snapguard/support/">SnapGuard</a></li><li><a href="/scansmith/support/">ScanSmith</a></li><li><a href="/soundbits/support/">VoxBitz</a></li><li><a href="/pixelsmith/privacy/">PixelSmith</a></li><li><a href="/download/#quick-export">Quick Export</a></li><li><a href="/workshopblast/support/">Workshop Blast</a></li></ul></div>
<div><h4>Help</h4><ul><li><a href="mailto:info@dialectforge.com">info@dialectforge.com</a></li><li><a href="mailto:help@dialectforge.com">help@dialectforge.com</a></li><li><a href="/help/">Help Center</a></li><li><a href="/support/">VPN support</a></li><li><a href="/privacy/">Privacy</a></li><li><a href="/terms/">Terms</a></li><li><a href="/sitroom">SitRoom</a></li></ul></div>
</div>
<div class="legal"><span>© 2026 DialectForge LLC · Michigan, USA</span><span>Code: AGPL-3.0 (open source coming soon) · Commercial licenses available</span></div>
</div></footer>
<script src="/assets/js/df.js" defer></script>"""

def page(title, desc, body, active="", extra_head=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{GTAG}
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#f2eee5">
<link rel="preload" href="/assets/fonts/archivo.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/df.css">
{extra_head}</head>
<body>
{header(active)}
<main id="content">
{body}
</main>
{FOOTER}
</body>
</html>
"""

def build_pages():
    d = os.path.join(ROOT, "_src", "pages")
    for fn in sorted(os.listdir(d)):
        src = open(os.path.join(d, fn), encoding="utf-8").read()
        meta, body = src.split("\n---\n", 1)
        body = re.sub(r"\{\{(\w+)\}\}", lambda m: open(os.path.join(ROOT,"_src","partials",m.group(1)+".html"),encoding="utf-8").read(), body)
        m = dict(l.split(":", 1) for l in meta.strip().splitlines())
        m = {k.strip(): v.strip() for k, v in m.items()}
        out = os.path.join(ROOT, m["path"].strip("/"), "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write(page(m["title"], m["desc"], body, m.get("nav", "")))
        print("page", m["path"])

# ---- re-wrap existing documents: wording untouched, only chrome/styling replaced ----
EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F\u2B50\u2B06\u2194-\u21AA]")
APPS = {
 "snapguard": ("SnapGuard","Free · Premium $3.99/mo","https://apps.apple.com/us/app/snapguard/id6759138449",["support","privacy","terms"]),
 "scansmith": ("ScanSmith","$4.99","https://apps.apple.com/us/app/scansmith/id6759459781",["support","privacy","terms"]),
 "soundbits": ("VoxBitz (formerly SoundBits)","$3.99","https://apps.apple.com/us/app/voxbitz/id6759455569",["support","privacy","terms"]),
 "pixelsmith": ("PixelSmith","Free · Pro $9.99","https://apps.apple.com/us/app/pixelsmith/id6758932412",["privacy","terms"]),
 "workshopblast": ("Workshop Blast","Free · Full game $5.99","https://apps.apple.com/us/app/workshop-blast/id6759474289",["support","privacy","terms"]),
}
WRAP = {  # path: (crumb, legal?)  legal pages keep emoji/everything verbatim
 "terms":("Legal",True),"privacy":("Legal",True),"messenger/terms":("Messenger · Legal",True),"messenger/privacy":("Messenger · Legal",True),
 "help":("Help",False),"support":("VPN support",False),"research":("Research",False),
}
for a in APPS:
    for s in APPS[a][3]: WRAP[f"{a}/{s}"] = ("Apps", s != "support")

def wrap(path, crumb, legal):
    fn = os.path.join(ROOT, "_src", "orig", path, "index.html")
    s = BeautifulSoup(open(fn, encoding="utf-8").read(), "html.parser")
    title = s.title.get_text(strip=True) if s.title else "DialectForge"
    md = s.find("meta", attrs={"name": "description"})
    desc = md["content"] if md and md.get("content") else title
    root = s.find("article") or s.body
    for t in root.find_all(["script", "style", "nav", "input"]): t.decompose()
    for t in root.find_all(class_=re.compile("bg-animation")): t.decompose()
    for t in root.find_all(string=lambda x: isinstance(x, Comment)): t.extract()
    if root.name == "body":
        for t in root.find_all("footer", recursive=False): t.decompose()
    for t in root.find_all(True):
        t.attrs.pop("style", None); t.attrs.pop("onclick", None)
    if not legal:
        for t in root.find_all("svg"): t.decompose()
        for t in root.find_all(string=True):
            if EMOJI.search(t): t.replace_with(EMOJI.sub("", t))
    # unwrap single .container wrapper
    inner = root
    kids = [k for k in root.find_all(recursive=False)]
    if len(kids) == 1 and kids[0].name == "div": inner = kids[0]
    h1 = inner.find("h1")
    head_title = h1.get_text(" ", strip=True) if h1 else title
    if h1: h1.decompose()
    content = "".join(str(c) for c in inner.contents)
    if path == "research":
        content = '<div class="callout"><h4>Editor\'s note</h4><p>This paper is reproduced as it was published on February 12, 2026, as a defensive (prior art) publication. Its statements describe design intent and research goals; they have not been independently verified. For current wording see <a href="/protocol/">the protocol</a> and <a href="/ai-factory/">AI Factory</a>.</p></div>' + content
    app = path.split("/")[0]
    apphead = ""
    if app in APPS:
        name, price, url, subs = APPS[app]
        links = " ".join(f'<a href="/{app}/{x}/">{x.capitalize()}</a>' for x in subs)
        apphead = f'<div class="apphead"><span class="tag live">iOS</span><span>{name} · {price}</span><a href="{url}">App Store ↗</a><nav aria-label="{name} pages">{links}</nav></div>'
        crumb = f'<a href="/download/">Apps</a> / {name}'
        head_title = f'{name.split(" (")[0]} · {head_title}'
    body = f"""<div class="doc-head"><div class="wrap"><div class="crumbs"><a href="/">DialectForge</a> / {crumb}</div><h1>{head_title}</h1>{apphead}</div></div>
<div class="wrap"><article class="doc">{content}</article></div>"""
    out = os.path.join(ROOT, path, "index.html")
    open(out, "w", encoding="utf-8").write(page(title, desc, body))
    print("wrap", path)

def build_wraps():
    for p, (c, legal) in WRAP.items(): wrap(p, c, legal)

if __name__ == "__main__":
    build_pages(); build_wraps()
