#!/usr/bin/env python3
"""Crawl every .html file in the repo, resolve each internal href/src against the local server, report failures.
Also checks #fragment targets exist and that every pre-redesign URL (from git main) still returns 200."""
import os, sys, subprocess, urllib.request, urllib.parse, re
from bs4 import BeautifulSoup
ROOT='/workspace/website'; BASE='http://127.0.0.1:8765'
def status(url):
    try:
        r=urllib.request.urlopen(url,timeout=10); return r.status, r.geturl(), r.read()
    except urllib.error.HTTPError as e: return e.code, url, b''
    except Exception as e: return str(e), url, b''
files=[os.path.relpath(os.path.join(d,f),ROOT) for d,_,fs in os.walk(ROOT) if '/.git' not in d and '/_src' not in d for f in fs if f.endswith('.html')]
cache={}; bad=[]; n=0
for f in sorted(files):
    page='/'+f[:-len('index.html')] if f.endswith('index.html') else '/'+f
    s=BeautifulSoup(open(os.path.join(ROOT,f),encoding='utf-8'),'html.parser')
    for t in s.find_all(['a','link','script','img','source','video']):
        for attr in ('href','src','poster'):
            v=t.get(attr)
            if not v or v.startswith(('mailto:','tel:','javascript:','data:')): continue
            u=urllib.parse.urljoin('https://dialectforge.com'+page, v)
            pu=urllib.parse.urlparse(u)
            if pu.netloc not in('dialectforge.com','www.dialectforge.com'): continue
            n+=1
            path=pu.path or '/'
            if path not in cache: cache[path]=status(BASE+urllib.parse.quote(path))
            code,final,body=cache[path]
            if code!=200: bad.append((f,v,code)); continue
            if pu.fragment and pu.fragment!='' and b'text/html' or True:
                if pu.fragment and not re.search(rb'id=["\']%s["\']'%re.escape(pu.fragment.encode()),body):
                    bad.append((f,v,'missing #'+pu.fragment))
print(f'{len(files)} pages, {n} internal links checked, {len(bad)} problems')
for b in bad: print('  BAD',*b)
old=subprocess.run(['git','-C',ROOT,'ls-tree','-r','--name-only','main'],capture_output=True,text=True).stdout.split()
oldfail=[]
for p in old:
    if p.startswith('.') or '/.' in p: continue
    url='/'+p
    c,_,_=status(BASE+urllib.parse.quote(url))
    if c!=200: oldfail.append((url,c))
    if p.endswith('index.html'):
        d='/'+p[:-10]
        for v in {d, d.rstrip('/') or '/'}:
            c,_,_=status(BASE+urllib.parse.quote(v))
            if c!=200: oldfail.append((v,c))
print(f'{len(old)} files on main re-checked as URLs, {len(oldfail)} failures')
for o in oldfail: print('  OLD',*o)
sys.exit(1 if bad or oldfail else 0)
