"""One-time synchronization with the owner's updated public homepage.

Uses saved current desktop/mobile captures; preserves the complete static blog
gallery rather than reintroducing Wix's virtualized placeholders. Not a build step.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote
import json
import urllib.request
import sys

from html_tree import Tree, Node
from restore_fidelity import ROOT, serialize, style_files, downloads

reference = ROOT/'migration/reference'
prefix = 'voyage' if '--voyage' in sys.argv else 'home'
slug = 'voyage-interieur' if prefix == 'voyage' else 'home'
target = ROOT/'content/pages'/f'{slug}.njk'
front, old_body = target.read_text().split('\n---\n', 1)
data = dict((key,json.loads(value)) for key,value in (line.split(': ',1) for line in front.splitlines() if ': ' in line))
desktop = Tree((reference/f'{prefix}-current-desktop.html').read_text()).root
mobile = Tree((reference/f'{prefix}-current-mobile.html').read_text()).root
rendered = Tree((reference/f'{prefix}-current-rendered.html').read_text()).root
find = lambda root, identifier: root.find(lambda n:n.attrs.get('id')==identifier)

def replace(old,new):
    old.parent.children[old.parent.children.index(old)] = new
    new.parent = old.parent

container = find(desktop,'SITE_CONTAINER')
replace(find(container,'PAGES_CONTAINER'), find(rendered,'PAGES_CONTAINER'))
mobile_container = find(mobile,'SITE_CONTAINER')
if prefix == 'home':
    replace(find(container,'comp-m4sgx9rv'), find(Tree(old_body).root,'comp-m4sgx9rv'))
    old_mobile = Tree((ROOT/'templates/original/home.mobile.html').read_text()).root
    replace(find(mobile_container,'comp-m4sgx9rv'), find(old_mobile,'comp-m4sgx9rv'))

data['originalDesktopStyles'] = style_files(desktop,'desktop')
data['originalMobileStyles'] = style_files(mobile,'mobile')
data['title'] = desktop.find(lambda n:n.tag=='title').text()
description = desktop.find(lambda n:n.tag=='meta' and n.attrs.get('name')=='description')
data['description'] = description.attrs.get('content','') if description else ''
data['originalMeta'] = [{'property':n.attrs['property'],'content':n.attrs.get('content','')} for n in desktop.walk() if n.tag=='meta' and n.attrs.get('property','').startswith(('og:','twitter:'))]
data['structuredData'] = [json.loads(n.text()) for n in desktop.walk() if n.tag=='script' and n.attrs.get('type')=='application/ld+json']

lossless = json.loads((reference/'lossless-assets.json').read_text())
aliases = json.loads((reference/'asset-aliases.json').read_text())
def final_path(path):
    seen=set()
    while path not in seen and (path in lossless or path in aliases):
        seen.add(path)
        path=aliases.get(path,lossless.get(path,path))
    return path

def localize(markup):
    root = Tree(markup).root
    # The shared serializer preserves/localizes srcset and replaces LQIP images.
    result = serialize(root)
    for old in {**lossless,**aliases}:result=result.replace(old,final_path(old))
    return result

desktop_markup=localize(serialize(container,shared=True))
mobile_markup=localize(serialize(mobile_container))
target.write_text('---\n'+'\n'.join(key+': '+json.dumps(value,ensure_ascii=False) for key,value in data.items())+'\n---\n'+desktop_markup)
(ROOT/'templates/original'/f'{slug}.mobile.html').write_text(mobile_markup)

def fetch(item):
    path,url=item
    path=final_path(path)
    file=ROOT/'public'/path.lstrip('/')
    if not file.exists():
        request=urllib.request.Request(quote(url,safe=':/%?,=&~+'),headers={'User-Agent':'Mozilla/5.0'})
        file.write_bytes(urllib.request.urlopen(request,timeout=90).read())
    return {'path':path,'source':url,'bytes':file.stat().st_size}
assets=list(ThreadPoolExecutor(max_workers=6).map(fetch,downloads.items()))
manifest=json.loads((reference/'asset-manifest.json').read_text())
(reference/'asset-manifest.json').write_text(json.dumps(list({a['path']:a for a in manifest+assets}.values()),ensure_ascii=False,indent=2))
captures=json.loads((reference/'manifest.json').read_text())
for entry in captures:
    if entry['file']==f'{slug}.html':
        entry['previousFile']=entry['file']
        entry['file']=f'{prefix}-current-rendered.html'
        entry['bytes']=(reference/entry['file']).stat().st_size
(reference/'manifest.json').write_text(json.dumps(captures,ensure_ascii=False,indent=2))
print(f'Synchronized current {slug} page in both layouts.')
