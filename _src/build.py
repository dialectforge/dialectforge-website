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
NAV = [("/protocol/","Protocol"),("/#domains","Domains"),("/dfos/","DFoS"),("/download/","Apps"),("/licensing/","Licensing"),("/lu/","Lu"),("/cattledog/","Cattledog"),("/research","Research"),("/#contact","Contact")]

def header(active):
    items = "".join(f'<a href="{h}"{" aria-current=page" if h==active else ""}>{t}</a>' for h,t in NAV)
    return f"""<a class="skip" href="#content">Skip to content</a>
<header class="mast"><div class="wrap">
<a class="mark" href="/">{MARK}<span>DialectForge</span></a>
<button class="nav-toggle" aria-expanded="false" aria-controls="nav">Menu</button>
<nav class="nav" id="nav" aria-label="Main">{items}</nav>
</div></header>"""

FOOTER = """<footer class="foot"><div class="wrap">
<div class="cols">
<div class="about"><a class="mark" href="/" style="color:inherit">"""+MARK+"""<span>DialectForge</span></a>
<p>One protocol, applied everywhere data moves or rests. Built in Michigan by John Martin. Being released as open source under AGPL-3.0.</p></div>
<div><h4>Protocol</h4><ul><li><a href="/protocol/">How it works</a></li><li><a href="/comparison/">Traffic comparison</a></li><li><a href="/research">Research</a></li><li><a href="/licensing/">Licensing</a></li><li><a href="/agents/">AI agent prompts</a></li><li><a href="/build-with-ai/">Build with your AI</a></li><li><a href="/llms.txt">llms.txt</a></li></ul></div>
<div><h4>Domains</h4><ul><li><a href="/dfos/">DFoS</a></li><li><a href="/vpn/">VPN</a></li><li><a href="/mesh/">Mesh</a></li><li><a href="/terminal/">Terminal</a></li><li><a href="/messenger/">Messenger</a></li><li><a href="/automotive/">Automotive</a></li><li><a href="/banking/">Banking</a></li><li><a href="/verify/">Verify</a></li><li><a href="/lu/">Lu</a></li><li><a href="/cattledog/">Cattledog</a></li><li><a href="/enterprise/">Enterprise</a></li></ul></div>
<div><h4>Apps</h4><ul><li><a href="/download/">All apps</a></li><li><a href="/snapguard/support/">SnapGuard</a></li><li><a href="/scansmith/support/">ScanSmith</a></li><li><a href="/soundbits/support/">VoxBitz</a></li><li><a href="/pixelsmith/privacy/">PixelSmith</a></li><li><a href="/download/#quick-export">Quick Export</a></li><li><a href="/workshopblast/support/">Workshop Blast</a></li><li><a href="https://liveflyer.app">LiveFlyer (web) ↗</a></li></ul></div>
<div><h4>Help</h4><ul><li><a href="mailto:info@dialectforge.com">info@dialectforge.com</a></li><li><a href="mailto:help@dialectforge.com">help@dialectforge.com</a></li><li><a href="/help/">Help Center</a></li><li><a href="/support/">VPN support</a></li><li><a href="/privacy/">Privacy</a></li><li><a href="/terms/">Terms</a></li></ul></div>
</div>
<div class="legal"><span>© 2026 DialectForge LLC, a Delaware limited liability company</span><span>Open source now: <a href="https://github.com/dialectforge/lu">Lu</a> (AGPL-3.0) and <a href="https://github.com/dialectforge/cattledog">Cattledog</a> (Apache-2.0) · DF-VPN in progress · Commercial licenses available</span></div>
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

AGENT_REPOS = [  # (repo, project name, page)
 ("dfos-tools-oss","DFoS tools","/dfos/"),("dialectforge-vpn-oss","VPN","/vpn/"),("dialectforge-mesh","Mesh / Tunnel","/mesh/"),
 ("dialectforge-terminal","Terminal / SSH","/terminal/"),("dialectforge-messenger","Messenger","/messenger/"),
 ("dialectforge-verify-core","Verify","/verify/"),("lu","Lu","/lu/"),("cattledog","Cattledog","/cattledog/")]

def agent_prompt(repo, name):
    if repo == "cattledog":
        return """I want to try Cattledog, DialectForge's honesty and scars layer for LLMs, in my project. Read in order:
1. https://dialectforge.com/llms.txt
2. AGENTS.md and README.md in https://github.com/dialectforge/cattledog
3. https://dialectforge.com/cattledog/
4. Its LICENSE (Apache-2.0)
Then ask me about my project (which model, which tools it can call, what a wrong answer would cost) and propose a small integration plan for me to approve.
Be careful with claims: Cattledog is a proof of concept, its results are the author's own runs, and nothing in it has been independently reviewed. Don't promise it stops prompt injection or hallucinations."""
    if repo == "lu":
        return """I want to explore Lu, DialectForge's knowledge-graph AI. Read in order:
1. https://dialectforge.com/llms.txt
2. AGENTS.md and docs/LU_EXPLAINED.md in https://github.com/dialectforge/lu
3. https://dialectforge.com/lu/
Then help me build and test it (cargo build, cargo test) and plan a small experiment with me before writing code.
Lu is research code: its scorecards are the author's own, and the trained brain isn't included. License: AGPL-3.0, or a commercial license from DialectForge LLC (info@dialectforge.com)."""
    return f"""I want to integrate the DialectForge protocol ({name}) into my project. Before writing any code, read these in order:
1. AGENTS.md in https://github.com/dialectforge/{repo}
2. https://dialectforge.com/protocol/
3. LICENSE, COMMERCIAL-LICENSE.md and CONTRIBUTING.md in that repository
Then ask me about my project (language, where data moves, what I want to protect) and propose a small integration plan for me to approve.
Treat every security property as a design goal: this code has not been independently audited. Tell me about the license obligations (AGPL-3.0, or a commercial license from DialectForge LLC) before copying any of its code into my project."""

def agent_block(repo, rail=True):
    name = next(n for r,n,_ in AGENT_REPOS if r == repo)
    if repo in ("lu", "cattledog"):
        lic = "Apache-2.0" if repo == "cattledog" else "AGPL-3.0 + commercial"
        note = f'<p class="measure small">Repository: <a href="https://github.com/dialectforge/{repo}">github.com/dialectforge/{repo}</a> (public, {lic}). <a href="/build-with-ai/">More prompts</a>.</p>'
    else:
        note = None
    pre = f'<div class="prompt"><button class="copy" type="button" data-copy>Copy</button><pre class="code" id="prompt-{repo}">{html.escape(agent_prompt(repo, name))}</pre></div>'
    note = note or f'<p class="measure small">Repository: <code>dialectforge/{repo}</code>. It is private while it is being cleaned up and will be public soon; the prompt works as-is once it is. <a href="/agents/">All agent prompts</a>.</p>'
    if not rail: return pre + note
    return f"""<section class="sheet sec" id="ai-agent"><div class="wrap grid">
<div class="rail"><b>§ AI</b> Agent</div>
<div class="main">
<h2>Start with an AI agent</h2>
<p class="measure">Paste this into your AI coding agent. It points the agent at the repository's <code>AGENTS.md</code> (what's there, what works, which files to read first), the protocol notes and the license, then has it plan the integration with you.</p>
{pre}
{note}
</div>
<p class="note">It's like handing a new helper the drawings and the spec sheet before they pick up a saw.</p>
</div></section>"""

def build_pages():
    d = os.path.join(ROOT, "_src", "pages")
    for fn in sorted(os.listdir(d)):
        src = open(os.path.join(d, fn), encoding="utf-8").read()
        meta, body = src.split("\n---\n", 1)
        body = re.sub(r"\{\{agent:([\w-]+)\}\}", lambda m: agent_block(m.group(1)), body)
        body = re.sub(r"\{\{agents_index\}\}", lambda m: "".join(f'<div class="agent-item" id="{r}"><h3><a href="{pg}">{n}</a> <span class="tag plan">{"Public · Apache-2.0" if r=="cattledog" else ("Public · AGPL-3.0" if r=="lu" else "Source coming soon")}</span></h3>' + agent_block(r, False) + '</div>' for r,n,pg in AGENT_REPOS), body)
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
    if path == "research":
        desc = desc.split(". ")[0] + ". A research paper describing dialect-native LLM training."
        for b in inner.find_all(class_="paper-badge"): b.decompose()
        for h in inner.find_all("h2"):
            if "Declaration" in h.get_text():
                sec = h.find_parent("section")
                if sec is not None and sec is not inner and len(sec.find_all("h2")) == 1:
                    sec.decompose()
                else:
                    nxt = h.find_next_sibling()
                    while nxt is not None and nxt.name != "h2":
                        cur, nxt = nxt, nxt.find_next_sibling(); cur.decompose()
                    h.decompose()
    content = "".join(str(c) for c in inner.contents)
    if path == "research":
        content = '<div class="callout"><h4>Also in research</h4><p><a href="/research/lu-cattledog-jev/">Lu + Cattledog + Jev + LLM agents: an idea for more autonomous AI</a> (proposal, October 14, 2026). Not built or tested. See also <a href="/lu/">Lu</a> and <a href="/cattledog/">Cattledog</a>, now open source.</p></div>' + '<div class="callout"><h4>Editor\'s note</h4><p>This paper is reproduced as it was first published on February 12, 2026. Its statements describe design intent and research goals, not demonstrated results. Strong wording in it, such as “immunity” or attacks being “impossible”, describes what the approach aims for. None of it has been tested or independently verified. For current wording see <a href="/protocol/">the protocol</a> and <a href="/ai-factory/">AI Factory</a>.</p></div>' + content
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

# ---- AI-friendly copies: plain Markdown of key pages, and /llms.txt ----
MD_PAGES = ["lu", "cattledog", "research/lu-cattledog-jev", "research", "build-with-ai"]
SITE = "https://dialectforge.com"

def html_to_md(node):
    out = []
    def inline(el):
        parts = []
        for c in el.children:
            if isinstance(c, str):
                parts.append(re.sub(r"\s+", " ", c))
            elif c.name == "a":
                href = c.get("href", "")
                if href.startswith("/"): href = SITE + href
                parts.append(f"[{inline(c).strip()}]({href})")
            elif c.name in ("strong", "b"): parts.append(f"**{inline(c).strip()}**")
            elif c.name in ("em", "i"): parts.append(f"*{inline(c).strip()}*")
            elif c.name == "code": parts.append(f"`{c.get_text()}`")
            elif c.name == "br": parts.append("\n")
            elif c.name in ("button", "svg", "script", "style"): pass
            else: parts.append(inline(c))
        return "".join(parts)
    def block(el):
        for c in el.children:
            if isinstance(c, str):
                if c.strip(): out.append(c.strip() + "\n")
                continue
            n = c.name
            if n in ("h1", "h2", "h3", "h4"):
                out.append("#" * int(n[1]) + " " + inline(c).strip() + "\n")
            elif n == "p":
                t = inline(c).strip()
                if t: out.append(t + "\n")
            elif n in ("ul", "ol"):
                for k, li in enumerate(c.find_all("li", recursive=False), 1):
                    h = li.find(["h3", "h4"])
                    if h:
                        rest = " ".join(inline(x).strip() for x in li.find_all("p", recursive=False))
                        out.append(f"{k}. **{inline(h).strip()}.** {rest}")
                    else:
                        out.append(("%d. " % k if n == "ol" else "- ") + inline(li).strip())
                out.append("")
            elif n == "pre":
                out.append("```\n" + c.get_text().rstrip() + "\n```\n")
            elif n == "svg":
                d = c.find("desc")
                if d: out.append("> Diagram: " + d.get_text(" ", strip=True) + "\n")
            elif n == "figure":
                block(c)
            elif n == "figcaption":
                out.append("*" + c.get_text(" ", strip=True) + "*\n")
            elif n == "table":
                for tr in c.find_all("tr"):
                    out.append("| " + " | ".join(td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"])) + " |")
                out.append("")
            elif n in ("button", "script", "style", "nav"):
                pass
            elif n in ("div", "section", "article", "main", "span", "header"):
                if "note" in (c.get("class") or []) or "rail" in (c.get("class") or []) or "crumbs" in (c.get("class") or []): continue
                block(c)
            else:
                t = inline(c).strip()
                if t: out.append(t + "\n")
    block(node)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"

def build_md():
    for p in MD_PAGES:
        s = BeautifulSoup(open(os.path.join(ROOT, p, "index.html"), encoding="utf-8").read(), "html.parser")
        main = s.find("main")
        md = f"<!-- Markdown copy of {SITE}/{p}/ for AI assistants and plain readers. Generated by _src/build.py. -->\n\n" + html_to_md(main)
        open(os.path.join(ROOT, p, "index.md"), "w", encoding="utf-8").write(md)
        print("md", p)

LLMS = """# DialectForge

> DialectForge is John Martin's one-person software shop (DialectForge LLC): a security protocol and the projects built on it, plus two AI projects, Lu and Cattledog, now open source. Plain, honest status: research code, tested by the author, not independently reviewed.

John builds by directing AI coding assistants. Vibe coders are welcome. Start with the Markdown pages below, then each repository's AGENTS.md.

## AI projects (open source)
- [Lu](https://dialectforge.com/lu/index.md): an AI built on a knowledge graph instead of model weights. Persistent, honest ("I don't know"), scars, curiosity. Rust. AGPL-3.0 + commercial license.
- [Lu repository](https://github.com/dialectforge/lu): start with AGENTS.md and docs/LU_EXPLAINED.md.
- [Cattledog](https://dialectforge.com/cattledog/index.md): wraps any LLM with Lu's honesty and scars. Python + Rust. Apache-2.0, free for anyone, including companies.
- [Cattledog repository](https://github.com/dialectforge/cattledog): start with AGENTS.md and README.md.

## Research
- [Lu + Cattledog + Jev + LLM agents](https://dialectforge.com/research/lu-cattledog-jev/index.md): an unbuilt proposal for a curious, persistent overseer of LLM agents.
- [DialectForge-native language models](https://dialectforge.com/research/index.md): an earlier paper (February 2026) on dialect-only instruction channels.

## Using these with an AI
- [Build with your AI](https://dialectforge.com/build-with-ai/index.md): paste-ready prompts.
- [AI agent prompts for every project](https://dialectforge.com/agents/)

## Protocol and other projects
- [Protocol](https://dialectforge.com/protocol/)
- [AI Factory (history of Lu and Cattledog)](https://dialectforge.com/ai-factory/)
- [Licensing](https://dialectforge.com/licensing/)

## Contact
- info@dialectforge.com
"""

def build_llms():
    open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8").write(LLMS)
    print("llms.txt")

if __name__ == "__main__":
    build_pages(); build_wraps(); build_md(); build_llms()
