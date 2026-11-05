"""Validate deployable HTML, migration route parity, links and SEO output."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import re
from collections import Counter
import sys
import xml.etree.ElementTree as ET
from html_tree import Tree, Node
from check_assets import audit_assets

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
errors = []
def require(condition, message):
    if not condition: errors.append(message)

def destination(path):
    target = DIST / unquote(path).lstrip('/')
    return target / 'index.html' if not target.suffix else target

pages = [p for p in DIST.rglob('*.html') if 'assets' not in p.relative_to(DIST).parts]
require(bool(pages), 'No generated pages')
routes = set()
for file in pages:
    html = file.read_text()
    root = Tree(html).root
    rel = str(file.relative_to(DIST))
    route = '/' + rel.removesuffix('index.html') if rel.endswith('index.html') else '/' + rel
    routes.add(route.rstrip('/') or '/')
    # Existing pages preserve the original heading hierarchy, including Wix's h6 home introduction.
    require(root.find(lambda n:n.tag=='main'), f'{rel}: missing main landmark')
    require(root.find(lambda n:n.tag=='html' and n.attrs.get('lang')=='fr'), f'{rel}: missing lang=fr')
    for key in ['description', 'viewport']:
        require(root.find(lambda n:n.tag=='meta' and n.attrs.get('name')==key), f'{rel}: missing {key}')
    require(root.find(lambda n:n.tag=='link' and n.attrs.get('rel')=='canonical'), f'{rel}: no canonical')
    for node in root.walk():
        if node.tag=='script':
            require(node.attrs.get('type')=='application/ld+json' or node.attrs.get('src') in {'/assets/local-layout.js','/assets/site-motion.js'} or (rel == 'index.html' and node.attrs.get('src') in {'/assets/google-reviews.js','/assets/home-faq.js'}),f'{rel}: unexpected runtime script found')
            if node.attrs.get('type')=='application/ld+json':
                try: json.loads(node.text())
                except ValueError: errors.append(f'{rel}: invalid structured data')
        if node.tag=='img':
            require('alt' in node.attrs,f'{rel}: image without alt')
        if node.attrs.get('srcset'):
            candidates = re.findall(r'(\S+)\s+\d+(?:\.\d+)?[wx](?:,\s*|$)', node.attrs['srcset'])
            for url in candidates:
                require(url.startswith('/') and destination(url).is_file(), f'{rel}: nonlocal or missing responsive image: {url}')
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
    require(not root.find(lambda n:n.tag=='script' and ('wix' in n.attrs.get('src','') or 'parastorage' in n.attrs.get('src',''))), f'{rel}: Wix runtime retained')
    # Empty spacer headings present in the source are retained for visual fidelity.

manifest = json.loads((ROOT/'migration/reference/page-manifest.json').read_text())
for stylesheet in DIST.rglob('*.css'):
    for url in re.findall(r'url\(\s*[\'"]?([^\)\'"\s]+)', stylesheet.read_text()):
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        target = DIST/unquote(parsed.path).lstrip('/') if parsed.path.startswith('/') else stylesheet.parent/unquote(parsed.path)
        require(target.is_file(), f'{stylesheet.relative_to(DIST)}: broken CSS asset: {url}')
original_routes = {unquote(urlsplit(r['url']).path).rstrip('/') or '/' for r in manifest}
require(original_routes <= routes, 'Missing migrated routes: ' + repr(original_routes-routes))
sitemap = ET.parse(DIST/'sitemap.xml')
sitemap_routes = {unquote(urlsplit(n.text).path).rstrip('/') or '/' for n in sitemap.findall('.//{*}loc')}
require(original_routes <= sitemap_routes, 'Missing sitemap routes: ' + repr(original_routes-sitemap_routes))
def editorial_text(node):
    if node.tag in {'script', 'style', 'template'}:
        return ''
    return ' '.join(editorial_text(child) if isinstance(child, Node) else child for child in node.children)

# Detect lost words when cleaning captured HTML. This supplements visual review;
# it deliberately does not claim that word counts verify ordering or styling.
reference = ROOT/'migration/reference'
captures = json.loads((reference/'manifest.json').read_text()) + json.loads((reference/'extra-pages.json').read_text())
text_report = []
for entry in captures:
    source_file = reference/entry['file']
    if not source_file.exists():
        source_file = reference/'raw'/entry['file']
    source = Tree(source_file.read_text()).root
    source = source.find(lambda n:n.attrs.get('id')=='PAGES_CONTAINER') or source.find(lambda n:n.tag=='main')
    target_file = destination(urlsplit(entry['url']).path)
    if not target_file.exists():
        continue  # Route check above reports missing files.
    target = Tree(target_file.read_text()).root.find(lambda n:n.attrs.get('id')=='PAGES_CONTAINER')
    if not source or not target:
        require(False, f"Cannot compare captured text: {entry['url']}")
        continue
    words = lambda node: Counter(re.findall(r'[\w’]+', editorial_text(node)))
    missing = dict(words(source) - words(target))
    text_report.append({'url': entry['url'], 'missing': missing})
    require(not missing, f"Lost captured text on {entry['url']}: {missing}")
    if '/post/' in urlsplit(entry['url']).path:
        # These passive attributes are CSS inputs, not removable Wix runtime
        # metadata. Losing data-breakout previously widened article text by 198px.
        presentation = {'data-breakout', 'data-ricos-font', 'data-ricos-responsive', 'data-font-size', 'data-list-style', 'data-list-style-position'}
        style_attributes = lambda tree: Counter((key,value) for node in tree.walk() for key,value in node.attrs.items() if key in presentation)
        lost_attributes = style_attributes(source) - style_attributes(target)
        require(not lost_attributes, f"Lost rich-text formatting on {entry['url']}: {dict(lost_attributes)}")
(reference/'text-check.json').write_text(json.dumps(text_report, ensure_ascii=False, indent=2))
require(len(sitemap_routes)==len(sitemap.findall('.//{*}loc')), 'Duplicate sitemap URLs')
ET.parse(DIST/'feed.xml')
require(not (DIST/'migration').exists(), 'Source archive leaked into deployment')
require(not (DIST/'node_modules').exists(), 'Build dependencies leaked into deployment')
asset_errors, audited_files = audit_assets(DIST)
errors.extend(asset_errors)
if errors:
    print('\n'.join(errors))
    sys.exit(1)
total = sum(p.stat().st_size for p in DIST.rglob('*') if p.is_file())
print(f'PASS: {len(pages)} HTML pages; all {len(original_routes)} original routes and sitemap entries; local links/assets; metadata; XML; no Wix runtime.')
print(f'Captured main-page words preserved on {len(text_report)} routes; responsive images and CSS assets verified.')
print(f'Asset audit: {audited_files} deployable text files; no Wix URLs or unapproved hotlinked assets. Google Maps and Places are approved exceptions.')
print(f'Deployment size: {total / 1024 / 1024:.2f} MiB. Home HTML: {(DIST/"index.html").stat().st_size / 1024:.1f} KiB.')
