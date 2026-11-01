"""Validate deployable HTML, migration route parity, links and SEO output."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import sys
import xml.etree.ElementTree as ET
from html_tree import Tree

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
errors = []
def require(condition, message):
    if not condition: errors.append(message)

def destination(path):
    target = DIST / unquote(path).lstrip('/')
    return target / 'index.html' if not target.suffix else target

pages = list(DIST.rglob('*.html'))
require(bool(pages), 'No generated pages')
routes = set()
for file in pages:
    html = file.read_text()
    root = Tree(html).root
    rel = str(file.relative_to(DIST))
    route = '/' + rel.removesuffix('index.html') if rel.endswith('index.html') else '/' + rel
    routes.add(route.rstrip('/') or '/')
    require(len([n for n in root.walk() if n.tag=='h1']) == 1, f'{rel}: expected one h1')
    require(root.find(lambda n:n.tag=='html' and n.attrs.get('lang')=='fr'), f'{rel}: missing lang=fr')
    for key in ['description', 'viewport']:
        require(root.find(lambda n:n.tag=='meta' and n.attrs.get('name')==key and n.attrs.get('content')), f'{rel}: missing {key}')
    require(root.find(lambda n:n.tag=='link' and n.attrs.get('rel')=='canonical'), f'{rel}: no canonical')
    for node in root.walk():
        if node.tag=='script':
            require(node.attrs.get('type')=='application/ld+json',f'{rel}: runtime script found')
            try: json.loads(node.text())
            except ValueError: errors.append(f'{rel}: invalid structured data')
        if node.tag=='img':
            require('alt' in node.attrs,f'{rel}: image without alt')
        for attribute in ['src', 'href']:
            url = node.attrs.get(attribute,'')
            parsed = urlsplit(url)
            if parsed.netloc or parsed.scheme or not parsed.path:
                continue
            if parsed.path.startswith('/'):
                require(destination(parsed.path).is_file(), f'{rel}: broken {attribute}: {url}')
                if parsed.fragment and destination(parsed.path).suffix=='.html':
                    target = Tree(destination(parsed.path).read_text()).root if destination(parsed.path).exists() else None
                    require(target and target.find(lambda n:n.attrs.get('id')==unquote(parsed.fragment)), f'{rel}: missing anchor {url}')
        require('static.wixstatic.com' not in node.attrs.get('src',''),f'{rel}: Wix asset dependency')
    require('parastorage' not in html and 'wixui-' not in html, f'{rel}: Wix runtime retained')
    require(not root.find(lambda n:n.tag in {'h1','h2','h3'} and not n.text().strip()), f'{rel}: empty heading')

manifest = json.loads((ROOT/'migration/source/manifest.json').read_text())
original_routes = {unquote(urlsplit(r['url']).path).rstrip('/') or '/' for r in manifest}
require(original_routes <= routes, 'Missing migrated routes: ' + repr(original_routes-routes))
sitemap = ET.parse(DIST/'sitemap.xml')
sitemap_routes = {unquote(urlsplit(n.text).path).rstrip('/') or '/' for n in sitemap.findall('.//{*}loc')}
require(original_routes <= sitemap_routes, 'Missing sitemap routes: ' + repr(original_routes-sitemap_routes))
require(len(sitemap_routes)==len(sitemap.findall('.//{*}loc')), 'Duplicate sitemap URLs')
ET.parse(DIST/'feed.xml')
require(not (DIST/'migration').exists(), 'Source archive leaked into deployment')
require(not (DIST/'node_modules').exists(), 'Build dependencies leaked into deployment')
if errors:
    print('\n'.join(errors))
    sys.exit(1)
total = sum(p.stat().st_size for p in DIST.rglob('*') if p.is_file())
print(f'PASS: {len(pages)} HTML pages; all {len(original_routes)} original routes and sitemap entries; local links/assets; metadata; XML; no browser JavaScript.')
print(f'Deployment size: {total / 1024 / 1024:.2f} MiB. Home HTML: {(DIST/"index.html").stat().st_size / 1024:.1f} KiB.')
