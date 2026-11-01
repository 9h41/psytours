"""One-time completion of virtualized mobile cards and responsive image assets.

Do not rerun after editorial changes. The four offscreen cards reuse the source
mobile card structure, original post data and the same Wix 4:3 crop parameters.
"""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from html import escape, unescape
from pathlib import Path
from urllib.parse import quote, urlsplit, unquote
import json
import re
import urllib.request

from html_tree import Tree, Node
from restore_fidelity import ROOT, serialize, local_asset, downloads

reference = ROOT/'migration/reference'
file = ROOT/'templates/original/home.mobile.html'
root = Tree(file.read_text()).root
gallery = root.find(lambda n:n.attrs.get('id')=='pro-gallery-margin-container-comp-m4sgx9rv')
existing = [n for n in gallery.children if isinstance(n, Node) and n.attrs.get('class')=='item-link-wrapper']
cards = json.loads((reference/'home-cards.json').read_text())
assert len(existing) == 7, 'Run only against the original seven-card mobile capture'
regular = existing[1]
old_id = regular.find(lambda n:n.attrs.get('data-hook')=='item-wrapper').attrs['id'].removeprefix('item-wrapper-')
mobile_image = regular.find(lambda n:n.tag=='source').attrs['srcset'].split('/v1/')[0]
for index, (identifier, markup) in enumerate(cards[7:], 7):
    desktop = Tree(markup).root
    uuid = desktop.find(lambda n:n.attrs.get('data-hook')=='item-wrapper').attrs['id'].removeprefix('item-wrapper-')
    image_url = desktop.find(lambda n:n.tag=='img').attrs['src']
    image_base = image_url.split('/v1/')[0]
    # Replace both the media identity and its trailing filename in the original
    # mobile crop URLs, retaining focal point, dimensions and quality settings.
    card_html = serialize(regular).replace(old_id, uuid).replace(old_id.replace('-',''), uuid.replace('-',''))
    card_html = card_html.replace(mobile_image, image_base).replace(mobile_image.rsplit('/',1)[-1], image_base.rsplit('/',1)[-1])
    card = Tree(card_html).root.children[0]
    container = card.find(lambda n:n.attrs.get('data-hook')=='item-container')
    container.attrs['id'] = 'pgi'+uuid.replace('-','')+'_'+str(index)
    container.attrs['style'] = re.sub(r'top:220px',f'top:{index*220}px',container.attrs['style'])
    source_title = desktop.find(lambda n:n.tag=='h2').text()
    card.find(lambda n:n.tag=='h2').children = [source_title]
    card.find(lambda n:n.attrs.get('data-hook')=='item-action').attrs['aria-label'] = source_title
    link = desktop.find(lambda n:n.tag=='a' and '/post/' in n.attrs.get('href','')).attrs['href']
    card.find(lambda n:n.tag=='a').attrs['href'] = link
    source_date = desktop.find(lambda n:n.attrs.get('data-hook')=='time-ago')
    date = card.find(lambda n:n.attrs.get('data-hook')=='time-ago')
    date.children = [source_date.text()]
    date.attrs['title'] = source_date.text()
    post_slug = unquote(urlsplit(link).path).strip('/').split('/')[-1]
    post = Tree((ROOT/'content/posts'/f'{post_slug}.njk').read_text().split('\n---\n',1)[1]).root
    read_time = post.find(lambda n:n.attrs.get('data-hook')=='time-to-read').text()
    time = card.find(lambda n:n.attrs.get('data-hook')=='time-to-read')
    time.children = [read_time]
    time.attrs['title'] = read_time
    for image in card.walk():
        if image.tag=='img':
            image.attrs['alt'] = desktop.find(lambda n:n.tag=='img').attrs.get('alt','')
            # The picture sources below provide the original responsive crop.
            source = card.find(lambda n:n.tag=='source' and 'blur_' not in n.attrs.get('srcset',''))
            image.attrs['src'] = local_asset(source.attrs['srcset'].split(' 1x')[0])
    gallery.children.append(card)
file.write_text(serialize(root))

# Source <picture> elements need localization as well as fallback <img> URLs.
# Commas inside Wix crop URLs are not srcset separators; parse descriptors.
changed = 0
for folder in ['templates', 'content']:
    for path in (ROOT/folder).rglob('*'):
        if path.suffix not in {'.html','.njk'}:
            continue
        original = path.read_text()
        def replace(match):
            value = unescape(match.group(1))
            candidates = re.findall(r'(\S+)\s+(\d+(?:\.\d+)?[wx])(?:,\s*|$)',value)
            if not candidates:
                raise ValueError('Unrecognized srcset in '+str(path))
            return 'srcset="'+escape(', '.join(local_asset(url)+' '+size for url,size in candidates),quote=True)+'"'
        localized = re.sub(r'srcset="([^"]+)"',replace,original)
        if localized != original:
            path.write_text(localized)
            changed += 1

lossless=json.loads((reference/'lossless-assets.json').read_text())
aliases=json.loads((reference/'asset-aliases.json').read_text())
def fetch(item):
    path, url = item
    path = aliases.get(lossless.get(path,path),lossless.get(path,path))
    target = ROOT/'public'/path.lstrip('/')
    if not target.exists():
        request=urllib.request.Request(quote(url,safe=':/%?,=&~+'),headers={'User-Agent':'Mozilla/5.0'})
        target.write_bytes(urllib.request.urlopen(request,timeout=90).read())
    return {'path':path,'source':url,'bytes':target.stat().st_size}
assets=list(ThreadPoolExecutor(max_workers=6).map(fetch,downloads.items()))
for folder in ['templates','content']:
    for path in (ROOT/folder).rglob('*'):
        if path.suffix in {'.html','.njk'}:
            text=path.read_text()
            for old,new in {**lossless,**aliases}.items():text=text.replace(old,new)
            path.write_text(text)
old=json.loads((reference/'asset-manifest.json').read_text())
(reference/'asset-manifest.json').write_text(json.dumps(list({a['path']:a for a in old+assets}.values()),ensure_ascii=False,indent=2))
print(f'Completed 11 mobile cards; localized responsive images in {changed} files; {len(assets)} responsive assets.')
