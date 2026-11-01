"""One-time conversion of captured Wix presentation to self-contained HTML/CSS.

This is an import tool, never part of the regular offline build. Re-running it
overwrites page sources. Retains presentation, removes application/runtime code.
"""
from pathlib import Path
from html import escape
from urllib.parse import urlsplit, unquote, quote
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import re
import urllib.request
import sys
from html_tree import Tree, Node, VOID

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / 'migration/reference'
MANIFEST = json.loads((ROOT / 'migration/source/manifest.json').read_text())
if '--extra-only' in sys.argv:
    MANIFEST = json.loads((REFERENCE / 'extra-pages.json').read_text())
ASSET_DIR = ROOT / 'public/assets/original'
TEMPLATES = ROOT / 'templates/original'
ASSET_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES.mkdir(parents=True, exist_ok=True)
downloads = {}
download_results = []

def local_asset(url):
    if url.startswith('data:') or not url:
        return url
    if url.startswith('//'): url = 'https:' + url
    if url.startswith('/_files/'): url = 'https://www.psy-tours.fr' + url
    parsed = urlsplit(url)
    if not parsed.netloc: return url
    # Keep the exact crop/quality selected by the original layout, without blur placeholders.
    url = re.sub(r',?blur_\d+', '', url)
    ext = Path(unquote(parsed.path)).suffix.lower()
    if ext not in {'.woff','.woff2','.ttf','.png','.jpg','.jpeg','.webp','.avif','.svg','.gif','.pdf','.html','.mp4','.webm','.mp3','.ogg','.ico'}:
        ext = '.asset'
    if 'enc_avif' in url: ext = '.avif'
    name = hashlib.sha256(url.encode()).hexdigest()[:20] + ext
    target = '/assets/original/' + name
    downloads[target] = url
    return target

def local_link(url):
    p = urlsplit(url)
    if p.netloc in {'www.psy-tours.fr','psy-tours.fr'}:
        if p.path.startswith('/_files/'): return local_asset(url)
        path = unquote(p.path) or '/'
        if path == '/services-3': path = '/prendre-rendez-vous'
        return path.rstrip('/') + '/' + ('#'+p.fragment if p.fragment else '')
    return url

def rewrite_css(css):
    def replace(match):
        value = match.group(1).strip('"\' ')
        if value.startswith(('https://','http://','//')):
            return 'url("' + local_asset(value) + '")'
        return match.group(0)
    return re.sub(r'url\(([^)]+)\)',replace,css)

def serialize(node, shared=False):
    if isinstance(node,str):
        # Whitespace has the same rendered meaning; readable newlines can be added between blocks.
        return escape(re.sub(r'[ \t\r\n]+', ' ', node), quote=False)
    tag, attrs = node.tag, dict(node.attrs)
    if tag in {'script','style','noscript','link','meta','title'}: return ''
    if shared and attrs.get('id') in {'SITE_HEADER','SITE_FOOTER'}:
        return '{% include "original/' + ('header' if attrs['id']=='SITE_HEADER' else 'footer') + '.njk" %}'
    if tag == 'root': return ''.join(serialize(c,shared) for c in node.children)
    if tag == 'wix-dropdown-menu': tag='nav'
    elif tag == 'wow-image': tag='div'
    # Restore an ordinary link for the keyboard skip control.
    if attrs.get('id')=='SKIP_TO_CONTENT_BTN':
        return '<a class="static-skip" href="#PAGES_CONTAINER">Skip to Main Content</a>'
    for key in list(attrs):
        if key.startswith('on') or key.startswith('data-'):
            # CSS uses these presentation hooks. Runtime models and event metadata are discarded.
            if key not in {'data-hook','data-testid','data-mesh-id','data-motion-part','data-angle','data-state','data-align','data-direction','data-preview','data-undisplayed','data-index','data-stretch','data-margin','data-menuposition','data-gap-spacer-top-margin','data-breakout','data-ricos-font','data-ricos-responsive','data-font-size','data-list-style','data-list-style-position','data-heading-level','data-type','data-indent','data-color'}:
                del attrs[key]
    if tag == 'img':
        src = attrs.get('src','')
        ancestor = node.parent
        responsive = attrs.get('srcset','')
        while ancestor:
            try:
                info=json.loads(ancestor.attrs.get('data-image-info','{}'))
                image=info.get('imageData',{})
                if info.get('isLQIP') and info.get('alignType')=='center' and info.get('displayMode')=='fill' and image.get('uri'):
                    width,height=info.get('targetWidth',0),info.get('targetHeight',0)
                    if width>0 and height>0:
                        base='https://static.wixstatic.com/media/'+image['uri']
                        variants=[(base+f'/v1/fill/w_{width*density},h_{height*density},al_c,q_85,enc_avif,quality_auto/'+image['uri'],density) for density in [1,2,3] if width*density<=image.get('width',width) and height*density<=image.get('height',height)]
                        if variants:
                            src=variants[0][0]
                            responsive=', '.join(url+f' {density}x' for url,density in variants)
                    break
            except (ValueError,TypeError): pass
            ancestor=ancestor.parent
        if not src:
            ancestor = node.parent
            while ancestor:
                try:
                    info=json.loads(ancestor.attrs.get('data-image-info','{}'))
                    uri=info.get('imageData',{}).get('uri','')
                    if uri:
                        src = uri if uri.startswith('http') else 'https://static.wixstatic.com/media/'+uri
                        break
                except ValueError: pass
                ancestor=ancestor.parent
        if src: attrs['src']=local_asset(src)
        attrs.pop('srcset',None)
        if responsive:
            candidates=re.findall(r'(\S+)\s+(\d+(?:\.\d+)?[wx])(?:,\s*|$)',responsive)
            if candidates:attrs['srcset']=', '.join(local_asset(url)+' '+density for url,density in candidates)
        attrs.pop('sizes',None)
        attrs.setdefault('alt','')
        attrs['decoding']='async'
    if tag=='a' and attrs.get('href'): attrs['href']=local_link(attrs['href'])
    if tag=='iframe' and attrs.get('src'):
        attrs['src']=local_asset(attrs['src'])
        attrs['loading']='lazy'
    if attrs.get('style'): attrs['style']=rewrite_css(attrs['style'])
    if tag=='form':
        attrs['data-local-newsletter']=''
    if tag=='input': attrs.pop('value',None)
    html_attrs=''.join(' '+key+('="'+escape(str(value),quote=True)+'"' if value is not None else '') for key,value in attrs.items())
    if tag in VOID: return '<'+tag+html_attrs+'>'
    body=''.join(serialize(c,shared) for c in node.children)
    return '<'+tag+html_attrs+'>'+body+'</'+tag+'>'

def style_files(tree,variant):
    result=[]
    seen=set()
    for node in tree.walk():
        if node.tag!='style':continue
        css=rewrite_css(node.text())
        if not css.strip():continue
        # Preserve the original selector names as styling identifiers, without custom elements.
        css=css.replace('wix-dropdown-menu','nav').replace('wow-image','div')
        name=hashlib.sha256(css.encode()).hexdigest()[:20]+'.css'
        if name not in seen:
            (ASSET_DIR/name).write_text(css)
            result.append('/assets/original/'+name)
            seen.add(name)
    return result

def find_id(tree,id): return tree.find(lambda n:n.attrs.get('id')==id)

def format_html(html):
    return re.sub(r'(?<=</(?:div)>)(?=<)', '\n', html) if False else html.replace('</section>','</section>\n').replace('</article>','</article>\n')

def main():
    pages=[]
    for record in MANIFEST:
        path=unquote(urlsplit(record['url']).path) or '/'
        slug='home' if path=='/' else path.strip('/').replace('/','__')
        desktop=Tree((REFERENCE/'raw'/record['file']).read_text()).root
        mobile=Tree((REFERENCE/'mobile'/record['file']).read_text()).root
        container=find_id(desktop,'SITE_CONTAINER')
        # Captured browser content includes final image crops, widget layout and current counters.
        rendered_file=REFERENCE/record['file']
        if rendered_file.exists():
            rendered=Tree(rendered_file.read_text()).root.find(lambda n:n.tag=='main')
            previous=find_id(container,'PAGES_CONTAINER')
            if rendered and previous:
                previous.parent.children[previous.parent.children.index(previous)]=rendered
        header=Tree((REFERENCE/'header.html').read_text()).root
        footer=Tree((REFERENCE/'footer.html').read_text()).root
        for id,replacement in [('SITE_HEADER',header.children[0]),('SITE_FOOTER',footer.children[0])]:
            old=find_id(container,id)
            if old:old.parent.children[old.parent.children.index(old)]=replacement
        if path=='/':
            (TEMPLATES/'header.njk').write_text(serialize(header))
            (TEMPLATES/'footer.njk').write_text(serialize(footer))
        desktop_styles=style_files(desktop,'desktop')
        mobile_styles=style_files(mobile,'mobile')
        mobile_container=find_id(mobile,'SITE_CONTAINER')
        mobile_html=serialize(mobile_container)
        mobile_name=slug+'.mobile.html'
        (TEMPLATES/mobile_name).write_text(format_html(mobile_html))
        title=desktop.find(lambda n:n.tag=='title').text()
        description=desktop.find(lambda n:n.tag=='meta' and n.attrs.get('name')=='description')
        meta_description=description.attrs.get('content','') if description else ''
        data={'layout':'exact-base.njk','title':title,'description':meta_description,
              'permalink':path.rstrip('/')+'/', 'originalDesktopStyles':desktop_styles,
              'originalMobileStyles':mobile_styles,'mobileTemplate':'original/'+mobile_name}
        old_markdown = ROOT/'content'/('posts' if path.startswith('/post/') else 'pages')/((path.rsplit('/',1)[-1] if path!='/' else 'home')+'.md')
        if not old_markdown.exists():
            old_markdown = old_markdown.with_suffix('.njk')
        if old_markdown.exists():
            old=old_markdown.read_text()
            for key in ['date','updated','author','image','imageAlt','categories','tags','articleTitle']:
                m=re.search(r'^'+key+r': (.*)$',old,re.M)
                if m:data[key]=json.loads(m.group(1))
            if path.startswith('/post/'):
                # The collection title is the visible post title, not the SEO title suffix.
                m=re.search(r'^title: (.*)$',old,re.M)
                if m and 'articleTitle' not in data:data['articleTitle']=json.loads(m.group(1))
            old_markdown.unlink()
        if path=='/blog': target=ROOT/'content/blog.njk'
        elif path.startswith('/blog/categories/'):
            target=ROOT/'content/archives'/(slug+'.njk')
        elif path.startswith('/post/'):
            target=ROOT/'content/posts'/(path.rsplit('/',1)[-1]+'.njk')
        else:target=ROOT/'content/pages'/('home.njk' if path=='/' else path.strip('/')+'.njk')
        target.parent.mkdir(parents=True,exist_ok=True)
        front='---\n'+'\n'.join(key+': '+json.dumps(value,ensure_ascii=False) for key,value in data.items())+'\n---\n'
        target.write_text(front+format_html(serialize(container,shared=True)))
        pages.append({'url':record['url'],'file':str(target.relative_to(ROOT)),'styles':len(desktop_styles),'mobileStyles':len(mobile_styles)})

    # Category archives now have their exact individual source markup rather than the redesign's grid.
    old=ROOT/'content/categories.njk'
    if old.exists():old.unlink()

    def download(item):
        target,url=item
        file=ROOT/'public'/target.lstrip('/')
        if not file.exists():
            req=urllib.request.Request(quote(url,safe=':/%?,=&~+'),headers={'User-Agent':'Mozilla/5.0'})
            file.write_bytes(urllib.request.urlopen(req,timeout=90).read())
        return {'path':target,'source':url,'bytes':file.stat().st_size}

    results=list(ThreadPoolExecutor(max_workers=8).map(download,downloads.items()))
    if '--extra-only' in sys.argv:
        previous_assets=json.loads((REFERENCE/'asset-manifest.json').read_text())
        results=list({item['path']:item for item in previous_assets+results}.values())
        previous_pages=json.loads((REFERENCE/'page-manifest.json').read_text())
        pages=list({item['url']:item for item in previous_pages+pages}.values())
    (REFERENCE/'asset-manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
    (REFERENCE/'page-manifest.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2))
    print(f'Converted {len(pages)} routes, both layouts; downloaded {len(results)} assets.')


if __name__ == "__main__":
    main()
