"""One-time importer. Read archived Wix HTML; write plain Markdown and local assets.

Re-running overwrites migrated content: do not run after editorial changes.
The regular build never uses this script or accesses Wix.
"""
from pathlib import Path
from html import escape
from urllib.parse import urlsplit, unquote, quote
import concurrent.futures
import hashlib
import json
import re
import urllib.request
from html_tree import Tree, Node

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'migration/source'
ASSETS = ROOT / 'public/assets'
assets = {}

def local_url(url):
    if url.startswith(('https://www.psy-tours.fr', 'https://psy-tours.fr')):
        url = unquote(urlsplit(url).path) or '/'
    if url.startswith('/_files/'):
        original = 'https://www.psy-tours.fr' + url
        target = '/assets/' + urlsplit(url).path.rsplit('/', 1)[-1]
        assets[target] = original
        return target
    if 'static.wixstatic.com/media/' in url:
        base = url.split('/v1/')[0]
        media = base.rsplit('/', 1)[-1]
        target = '/assets/' + hashlib.sha256(base.encode()).hexdigest()[:16] + '.webp'
        assets[target] = base + '/v1/fit/w_1400,h_1400,q_82,enc_webp/' + media.rsplit('.', 1)[0] + '.webp'
        return target
    return url

def render(node):
    if isinstance(node, str):
        return node.replace('\u200b', '').replace('\xa0', ' ')
    tag = node.tag
    if tag in {'script','style','svg','button','iframe','input'}:
        return ''
    if tag == 'img':
        src = node.attrs.get('src', '')
        if not src:
            ancestor = node.parent
            while ancestor:
                try:
                    info = json.loads(ancestor.attrs.get('data-image-info', '{}'))
                    uri = info.get('imageData', {}).get('uri', '')
                    if uri:
                        src = uri if uri.startswith('http') else 'https://static.wixstatic.com/media/' + uri
                        break
                except ValueError:
                    pass
                ancestor = ancestor.parent
        if 'static.wixstatic.com/media/' not in src:
            return ''
        alt = node.attrs.get('alt', '').replace('[', '').replace(']', '')
        return '\n\n![' + alt + '](' + local_url(src) + ')\n\n'
    body = ''.join(render(c) for c in node.children)
    if tag == 'br': return '\n\n'
    if tag == 'a':
        href = node.attrs.get('href', '')
        if not body.strip() or not href or href.startswith(('javascript:', '#')): return body
        return '[' + body.strip() + '](' + local_url(href).replace(' ', '%20') + ')'
    if tag in {'h1','h2','h3','h4','h5','h6'}:
        level = min(int(tag[1]), 3)
        if level == 1: level = 2
        return '\n\n' + '#' * level + ' ' + re.sub(r'\s+', ' ', body).strip() + '\n\n'
    if tag == 'li': return '\n- ' + re.sub(r'\s+', ' ', body).strip() + '\n'
    if tag in {'strong','b'} and body.strip(): return '**' + body.strip() + '**'
    if tag in {'em','i'} and body.strip(): return '*' + body.strip() + '*'
    if tag == 'blockquote': return '\n\n> ' + body.strip().replace('\n', '\n> ') + '\n\n'
    if tag in {'p','div','section','ul','ol','figure'}: return '\n\n' + body + '\n\n'
    return body

def clean(text):
    return re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+', '\n\n', text).strip() + '\n'

def frontmatter(data):
    # JSON is valid YAML and avoids ambiguous dates, colons and accent quoting.
    return '---\n' + '\n'.join(k + ': ' + json.dumps(v, ensure_ascii=False) for k,v in data.items()) + '\n---\n\n'

def meta(tree, key):
    n = tree.find(lambda n: n.tag == 'meta' and (n.attrs.get('name') == key or n.attrs.get('property') == key))
    return n.attrs.get('content','') if n else ''

manifest = json.loads((SOURCE / 'manifest.json').read_text())
report = []
category_data = []
for record in manifest:
    url = record['url']
    route = unquote(urlsplit(url).path) or '/'
    tree = Tree((SOURCE / record['file']).read_text()).root
    if '/blog/categories/' in route:
        slug = route.rsplit('/',1)[-1]
        category_data.append({'slug': slug, 'title': meta(tree,'og:title').split('|')[0].strip() or slug})
        continue
    if route == '/blog': continue
    description = meta(tree, 'description')
    title_node = tree.find(lambda n: n.tag=='title')
    title = title_node.text().split('|')[0].strip()
    data = {'title': title, 'description': description, 'permalink': '/' if route == '/' else route + '/'}
    if route.startswith('/post/'):
        article = tree.find(lambda n: n.attrs.get('data-hook') == 'post-description')
        if article is None: raise RuntimeError('Missing article: ' + route)
        ld = json.loads(tree.find(lambda n:n.attrs.get('type')=='application/ld+json').text())
        data.update({'layout':'post.njk','tags':['posts'], 'title':ld['headline'],
                     'date':ld['datePublished'], 'updated':ld['dateModified'],
                     'author':ld['author']['name'], 'image':local_url(ld['image']['url']),
                     'imageAlt':ld['headline'], 'categories':[]})
        seen = set()
        category_root = tree.find(lambda n:n.attrs.get('aria-label')=='Post categories')
        for n in category_root.walk() if category_root else []:
            href = n.attrs.get('href', '')
            if '/blog/categories/' in href:
                slug = unquote(urlsplit(href).path).rsplit('/',1)[-1]
                if slug not in seen:
                    data['categories'].append({'slug':slug,'title':n.text().strip() or slug})
                    seen.add(slug)
        body = clean(render(article))
        target = ROOT / 'content/posts' / (route.rsplit('/',1)[-1] + '.md')
    else:
        main = tree.find(lambda n:n.attrs.get('id')=='PAGES_CONTAINER')
        if main is None:
            main = tree.find(lambda n:n.attrs.get('id')=='SITE_PAGES')
        if main is None: raise RuntimeError('Missing page container: '+route)
        blocks = [n for n in main.walk() if n.attrs.get('data-testid')=='richTextElement']
        body = clean('\n\n'.join(render(n) for n in blocks))
        # The newsletter belongs to Wix CRM, not the static site. Keep contact in shared footer.
        body = re.split(r'(?:#+ )?Restons en contact',body)[0].strip() + '\n'
        body = re.sub(r'\n(?:#+ )?Mes coordonnées[\s\S]*$', '\n', body)
        body = body.replace("S'abonner", '')
        # Page title is emitted by the layout.
        lines = body.splitlines()
        if lines and lines[0].lstrip('# ').strip().lower() in {title.lower(), route.strip('/').replace('-',' '), 'qui sui-je ?', 'qui suis-je ?', 'bibliographie', 'la gestalt', 'cadre et éthique', 'prendre rendez-vous', 'consultation en visio'}:
            body = '\n'.join(lines[1:]).strip() + '\n'
        if route == '/qui-suis-je':
            body = re.sub(r'^## Qui suis-je \?\s*', '', body)
        images = [n for n in main.walk() if n.tag=='img' and 'static.wixstatic.com/media/' in n.attrs.get('src','')]
        data['layout'] = 'page.njk'
        if images and route not in {'/','/prendre-rendez-vous','/etique-et-déonthologie','/la-gestalt','/consultation-en-visio','/lectures'}:
            # Retain meaningful programme graphics and portrait, independently of Wix layout.
            data['image'] = local_url(images[0].attrs['src'])
            data['imageAlt'] = 'Elisa Gatay-Hauet' if route == '/qui-suis-je' else 'Le Voyage intérieur'
            if route == '/voyage-interieur':
                body += '\n\n' + '\n\n'.join(render(n) for n in images[1:])
        if route == '/':
            data.update({'layout':'home.njk','title':'Gestalt-thérapie à Tours',
                         'image':local_url(images[0].attrs['src']), 'imageAlt':'Elisa Gatay-Hauet'})
            # The home layout carries the introductory copy and generated blog listing.
            body = body[body.index('## Pour quelles raisons consulter'):]
            body = re.split(r'## Blog', body)[0]
            pdf = main.find(lambda n: n.tag=='a' and '/_files/' in n.attrs.get('href',''))
            if pdf:
                body += '\n\n[Lire cette histoire](' + local_url(pdf.attrs['href']) + ')\n'
            # Preserve original illustrations in their related section.
            for n in images[2:6]:
                marker = {'Raked':'Clarifier', 'AdobeStock':'Réguler', 'Act one':'Agir autrement' }
                for prefix, label in marker.items():
                    if n.attrs.get('alt','').startswith(prefix):
                        body = body.replace('\n\n'+label+'\n', render(n)+'\n### '+label+'\n',1)
        # Buttons outside rich-text containers still carry essential destinations.
        if route == '/lectures':
            links = [n.attrs['href'] for n in main.walk() if n.tag=='a' and n.text().strip()=='Read More']
            titles = ['Le grand livre de la Gestalt, Chantal et Gonzague Masquelier', '50 exercices de Gestalt-thérapie, Catherie Clouzard', 'Manuel de gestalt-thérapie, Fritz Perls', 'Gestalt therapie, Frederick Perls/Ralph Hefferline/Paul Goodman']
            for title_text, href in zip(titles, links):
                body = body.replace(title_text, '['+title_text+']('+href+')')
        target = ROOT / 'content/pages' / ('home.md' if route=='/' else route.strip('/')+'.md')
    target.write_text(frontmatter(data) + body)
    report.append({'url':url,'content':str(target.relative_to(ROOT)),'characters':len(body)})

def download(item):
    target, source = item
    file = ROOT / 'public' / target.lstrip('/')
    if not file.exists():
        request = urllib.request.Request(quote(source, safe=':/%,?=&~'), headers={'User-Agent':'Mozilla/5.0'})
        file.write_bytes(urllib.request.urlopen(request,timeout=60).read())
    return {'path':target,'source':source,'bytes':file.stat().st_size}

ROOT.joinpath('data').mkdir(exist_ok=True)
ROOT.joinpath('data/categories.json').write_text(json.dumps(category_data,ensure_ascii=False,indent=2))
asset_report = list(concurrent.futures.ThreadPoolExecutor(max_workers=6).map(download,assets.items()))
SOURCE.joinpath('content-import.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
SOURCE.joinpath('assets.json').write_text(json.dumps(asset_report,ensure_ascii=False,indent=2))
print(f'Imported {len(report)} content files and {len(asset_report)} local assets.')
