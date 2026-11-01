"""One-time import of the owner's current public Voyage intérieur landing page.

This replaces that page's desktop and mobile sources. Do not run for routine edits.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import re
from urllib.parse import quote
import json
import urllib.request

from html_tree import Tree
from restore_fidelity import ROOT, serialize, style_files, downloads, local_asset

reference=ROOT/'migration/reference'
desktop=Tree((reference/'voyage-live-2026-desktop-source.html').read_text()).root
mobile=Tree((reference/'voyage-live-2026-mobile-source.html').read_text()).root
rendered=Tree((reference/'voyage-live-2026-rendered.html').read_text()).root
find=lambda root,ident:root.find(lambda n:n.attrs.get('id')==ident)
desktop_container=find(desktop,'SITE_CONTAINER')
old=find(desktop_container,'PAGES_CONTAINER')
new=find(rendered,'PAGES_CONTAINER')
if not all((desktop_container,old,new,find(mobile,'SITE_CONTAINER'))):
    raise ValueError('The captured page structure is incomplete')
old.parent.children[old.parent.children.index(old)]=new
new.parent=old.parent

target=ROOT/'content/pages/voyage-interieur.njk'
front,_=target.read_text().split('\n---\n',1)
data=dict(line.split(': ',1) for line in front.splitlines() if ': ' in line)
data={key:json.loads(value) for key,value in data.items()}
# Keep a snapshot: shared style_files() can regenerate previously localized
# styles with remote source-map comments; do not overwrite those shared files.
existing_styles={p:p.read_bytes() for p in (ROOT/'public/assets/original').glob('*.css')}
data['originalDesktopStyles']=style_files(desktop,'desktop')
data['originalMobileStyles']=style_files(mobile,'mobile')
for file,content in existing_styles.items():file.write_bytes(content)
data['title']=desktop.find(lambda n:n.tag=='title').text()
description=desktop.find(lambda n:n.tag=='meta' and n.attrs.get('name')=='description')
data['description']=description.attrs.get('content','') if description else ''
meta=[]
for node in desktop.walk():
    if node.tag=='meta' and node.attrs.get('property','').startswith(('og:','twitter:')):
        value=node.attrs.get('content','')
        if node.attrs['property'] in {'og:image','og:image:url','og:image:secure_url','twitter:image'}:
            value=local_asset(value)
        meta.append({'property':node.attrs['property'],'content':value})
data['originalMeta']=meta
# Keep the existing structured data unless the current capture explicitly supplies any.
jsonld=[json.loads(n.text()) for n in desktop.walk() if n.tag=='script' and n.attrs.get('type')=='application/ld+json']
if jsonld:data['structuredData']=jsonld
desktop_markup=serialize(desktop_container,shared=True)
mobile_markup=serialize(find(mobile,'SITE_CONTAINER'))

aliases=json.loads((reference/'asset-aliases.json').read_text())
lossless=json.loads((reference/'lossless-assets.json').read_text())
def final_path(path):
    seen=set()
    while path not in seen and (path in aliases or path in lossless):
        seen.add(path)
        path=aliases.get(path,lossless.get(path,path))
    return path

def download(item):
    path,url=item
    path=final_path(path)
    file=ROOT/'public'/path.lstrip('/')
    if not file.exists():
        request=urllib.request.Request(quote(url,safe=':/%?,=&~+'),headers={'User-Agent':'Mozilla/5.0'})
        file.write_bytes(urllib.request.urlopen(request,timeout=90).read())
    # Wix can respond to enc_avif with JPEG or WebP bytes. Match the extension.
    head=file.read_bytes()[:16]
    suffix='.jpg' if head.startswith(b'\xff\xd8\xff') else '.png' if head.startswith(b'\x89PNG\r\n\x1a\n') else '.webp' if head.startswith(b'RIFF') and head[8:12]==b'WEBP' else None
    new=file.with_suffix(suffix) if suffix and file.suffix.lower() not in ({'.jpg','.jpeg'} if suffix=='.jpg' else {suffix}) else file
    if new!=file:
        if not new.exists():new.write_bytes(file.read_bytes())
        aliases[path]='/'+str(new.relative_to(ROOT/'public'))
        path=aliases[path]
    return {'path':path,'source':url,'bytes':new.stat().st_size}

with ThreadPoolExecutor(max_workers=6) as pool:
    assets=list(pool.map(download,list(downloads.items())))
def apply_aliases(text):
    for old in {**lossless,**aliases}:text=text.replace(old,final_path(old))
    return text

# Styles may refer to media paths whose extensions were corrected above.
for style in set(data['originalDesktopStyles']+data['originalMobileStyles']):
    file=ROOT/'public'/style.lstrip('/')
    if file not in existing_styles:
        css=re.sub(r'/\*# sourceMappingURL=.*?\*/','',file.read_text())
        file.write_text(apply_aliases(css))
desktop_markup=apply_aliases(desktop_markup)
mobile_markup=apply_aliases(mobile_markup)
data['originalMeta']=json.loads(apply_aliases(json.dumps(data['originalMeta'],ensure_ascii=False)))
target.write_text('---\n'+'\n'.join(key+': '+json.dumps(value,ensure_ascii=False) for key,value in data.items())+'\n---\n'+desktop_markup)
(ROOT/'templates/original/voyage-interieur.mobile.html').write_text(mobile_markup)
(reference/'asset-aliases.json').write_text(json.dumps(aliases,ensure_ascii=False,indent=2)+'\n')
manifest=json.loads((reference/'asset-manifest.json').read_text())
(reference/'asset-manifest.json').write_text(json.dumps(list({a['path']:a for a in manifest+assets}.values()),ensure_ascii=False,indent=2))
captures=json.loads((reference/'manifest.json').read_text())
for entry in captures:
    if entry['url'].rstrip('/').endswith('/voyage-interieur'):
        entry['previousFile']=entry['file']
        entry['file']='voyage-live-2026-rendered.html'
        entry['bytes']=(reference/entry['file']).stat().st_size
(reference/'manifest.json').write_text(json.dumps(captures,ensure_ascii=False,indent=2))
print(f'Imported the current Voyage intérieur page and localized {len(assets)} asset references.')
