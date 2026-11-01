"""One-time assembly of the original gallery, including virtualized cards."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
import json
import urllib.request
from html_tree import Tree
from restore_fidelity import serialize, downloads

ROOT=Path(__file__).resolve().parents[1]
file=ROOT/'content/pages/home.njk'
front,body=file.read_text().split('\n---\n',1)
root=Tree(body).root
gallery=root.find(lambda n:n.attrs.get('id')=='pro-gallery-margin-container-comp-m4sgx9rv')
cards=json.loads((ROOT/'migration/reference/home-cards.json').read_text())
gallery.children=[Tree(html).root.children[0] for _,html in cards]
markup=serialize(root)
lossless=json.loads((ROOT/'migration/reference/lossless-assets.json').read_text())
for old,new in lossless.items():markup=markup.replace(old,new)
file.write_text(front+'\n---\n'+markup)

def fetch(item):
    path,url=item
    target=ROOT/'public'/lossless.get(path,path).lstrip('/')
    if target.exists():return
    request=urllib.request.Request(quote(url,safe=':/%?,=&~+'),headers={'User-Agent':'Mozilla/5.0'})
    target.write_bytes(urllib.request.urlopen(request,timeout=60).read())
list(ThreadPoolExecutor(max_workers=6).map(fetch,downloads.items()))
print(f'Assembled all {len(cards)} original home cards without virtualization.')
