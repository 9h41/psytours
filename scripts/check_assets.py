"""Audit deployable files for hotlinked assets, including nested local embeds."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import re

from html_tree import Tree

SITE_HOSTS={'www.psy-tours.fr','psy-tours.fr','localhost:8080'}
WIX_HOST=re.compile(r'(?:[\w-]+\.)*(?:wixstatic\.com|parastorage\.com|wix\.com)',re.I)
MEDIA_FIELDS={'image','logo','thumbnailUrl','contentUrl','embedUrl'}

def audit_assets(dist):
    errors=[]
    def asset(url,file,allow_map=False):
        if not url or url.startswith(('data:','#')):return
        parsed=urlsplit(url)
        if allow_map and parsed.scheme=='https' and parsed.hostname in {'maps.google.com','www.google.com'} and parsed.path.startswith('/maps'):
            return  # Explicitly approved interactive Google Maps service.
        if parsed.scheme not in {'','http','https'} or (parsed.netloc and parsed.netloc not in SITE_HOSTS):
            errors.append(f'{file.relative_to(dist)}: external asset: {url}')
            return
        path=unquote(parsed.path)
        target=dist/path.lstrip('/') if path.startswith('/') else file.parent/path
        if target.is_dir():target=target/'index.html'
        if not target.is_file():errors.append(f'{file.relative_to(dist)}: missing local asset: {url}')

    def css(text,file):
        for url in re.findall(r'url\(\s*[\'"]?([^\)\'"\s]+)',text):asset(url,file)
        for url in re.findall(r'@import\s+[\'"]([^\'"]+)',text):asset(url,file)
        for url in re.findall(r'sourceMappingURL=([^\s*]+)',text):asset(url,file)

    def structured(value,file,media=False):
        if isinstance(value,str):
            if media:asset(value,file)
        elif isinstance(value,list):
            for item in value:structured(item,file,media)
        elif isinstance(value,dict):
            image_object=value.get('@type')=='ImageObject'
            for key,item in value.items():
                structured(item,file,key in MEDIA_FIELDS or (key=='url' and (media or image_object)))

    files=[p for p in dist.rglob('*') if p.is_file() and p.suffix in {'.html','.css','.js','.json','.xml','.svg'}]
    for file in files:
        text=file.read_text()
        if WIX_HOST.search(unquote(text)):
            errors.append(f'{file.relative_to(dist)}: Wix-hosted URL remains in deployment')
        if file.suffix=='.css':css(text,file)
        if file.suffix=='.js':
            for url in re.findall(r'(?:fetch|import|importScripts|Worker)\(\s*[\'"]([^\'"]+)',text):asset(url,file)
        if file.suffix not in {'.html','.svg'}:continue
        root=Tree(text).root
        for node in root.walk():
            for key in ['src','poster']:
                if node.attrs.get(key):asset(node.attrs[key],file,allow_map=node.tag=='iframe' and key=='src')
            if node.attrs.get('srcset'):
                for url in re.findall(r'(\S+)\s+\d+(?:\.\d+)?[wx](?:,\s*|$)',node.attrs['srcset']):asset(url,file)
            if node.tag=='link' and set(node.attrs.get('rel','').split()) & {'stylesheet','icon','shortcut','apple-touch-icon','preload','modulepreload'}:
                asset(node.attrs.get('href',''),file)
            if node.tag in {'image','use'}:
                asset(node.attrs.get('href',node.attrs.get('xlink:href','')),file)
            if node.tag=='meta' and node.attrs.get('property',node.attrs.get('name','')) in {'og:image','og:image:url','og:image:secure_url','og:video','og:video:url','twitter:image','twitter:image:src'}:
                asset(node.attrs.get('content',''),file)
            if node.tag=='script' and node.attrs.get('type')=='application/ld+json':
                try:structured(json.loads(node.text()),file)
                except ValueError:errors.append(f'{file.relative_to(dist)}: invalid structured metadata')
            if node.tag=='style':css(node.text(),file)
            if node.attrs.get('style'):css(node.attrs['style'],file)
    return sorted(set(errors)),len(files)

if __name__=='__main__':
    dist=Path(__file__).resolve().parents[1]/'dist'
    errors,count=audit_assets(dist)
    print('\n'.join(errors) if errors else f'PASS: {count} deployable text files audited; assets are local; direct Google Maps iframes are the sole external asset service.')
    raise SystemExit(bool(errors))
