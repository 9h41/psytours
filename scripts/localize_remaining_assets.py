"""One-time localization of residual Wix URLs, including SEO images and videos.

Not part of the offline build. Archived source captures retain provenance URLs.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote
import json
import re
import urllib.request

from restore_fidelity import ROOT, local_asset

reference=ROOT/'migration/reference'
manifest_file=reference/'asset-manifest.json'
manifest=json.loads(manifest_file.read_text())
aliases=json.loads((reference/'asset-aliases.json').read_text())
lossless=json.loads((reference/'lossless-assets.json').read_text())
def final_path(path):
    seen=set()
    while path not in seen and (path in aliases or path in lossless):
        seen.add(path)
        path=aliases.get(path,lossless.get(path,path))
    return path

known={row['source']:final_path(row['path']) for row in manifest}
files=[p for folder in ['content','templates','public','data'] for p in (ROOT/folder).rglob('*') if p.suffix in {'.html','.njk','.css','.js','.json','.xml','.svg'}]
pattern=re.compile(r'https?://(?:[\w-]+\.)*(?:wixstatic\.com|parastorage\.com)/[^\s<>"\x27)\\]+')
mapping={}
for file in files:
    for url in pattern.findall(file.read_text()):
        mapping[url]=known.get(url,final_path(local_asset(url)))

def fetch(item):
    url,path=item
    file=ROOT/'public'/path.lstrip('/')
    if not file.exists():
        request=urllib.request.Request(quote(url,safe=':/%?,=&~+'),headers={'User-Agent':'Mozilla/5.0'})
        file.write_bytes(urllib.request.urlopen(request,timeout=120).read())
    return {'path':path,'source':url,'bytes':file.stat().st_size}

print(f'Localizing {len(mapping)} remaining image/video URLs.',flush=True)
assets=list(ThreadPoolExecutor(max_workers=6).map(fetch,mapping.items()))
for file in files:
    original=file.read_text()
    localized=pattern.sub(lambda match:mapping[match[0]],original)
    if localized!=original:file.write_text(localized)
manifest_file.write_text(json.dumps(list({row['path']:row for row in manifest+assets}.values()),ensure_ascii=False,indent=2))
(reference/'remaining-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2))
print(f'Localized all residual Wix asset URLs ({len(assets)} unique URLs).')
