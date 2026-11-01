"""Prepare a separate GitHub project-site artifact; leave normal builds intact."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import argparse
import re
import shutil

from check_assets import audit_assets
from html_tree import Tree

ROOT=Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS={'.html','.css','.js','.json','.xml','.svg'}

def rewrite_urls(text,base_path,origin):
    # Quoted HTML/JSON/JS URLs, including URLs in the mobile template.
    text=re.sub(r'''(["'])/(?!/)([^\s"'<>]*)''',
                lambda m:m[1]+base_path+m[2],text)
    # Unquoted CSS url() and subsequent responsive-image candidates.
    text=re.sub(r'(?<![\w/.:])/assets/',base_path+'assets/',text)
    # Social/structured-data media must use this deployment, not production.
    for host in ('https://www.psy-tours.fr','https://psy-tours.fr'):
        text=text.replace(host+'/assets/',origin+base_path+'assets/')
    return text

def prepare(source,output,base_path,origin):
    if not source.is_dir() or output.resolve()==source.resolve():
        raise ValueError('A separate output directory and an existing build are required')
    shutil.rmtree(output,ignore_errors=True)
    shutil.copytree(source,output)
    for file in output.rglob('*'):
        if not file.is_file() or file.suffix not in TEXT_EXTENSIONS:continue
        text=rewrite_urls(file.read_text(),base_path,origin)
        if file.suffix=='.html':
            text=text.replace('</head>','<meta name="robots" content="noindex, nofollow">\n</head>')
        file.write_text(text)
    (output/'CNAME').unlink(missing_ok=True)
    (output/'.nojekyll').touch()
    (output/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
    # GitHub Pages does not support the original host's HTTP redirect file.
    alias=output/'services-3'
    alias.mkdir(exist_ok=True)
    target=base_path+'prendre-rendez-vous/'
    (alias/'index.html').write_text(f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="robots" content="noindex, nofollow"><meta http-equiv="refresh" content="0;url={target}"><title>Prendre rendez-vous</title></head><body><a href="{target}">Prendre rendez-vous</a></body></html>')
    errors,count=audit_assets(output,base_path,origin)
    # Check navigation too: asset checks alone cannot prove subpath routing.
    for file in output.rglob('*.html'):
        for node in Tree(file.read_text()).root.walk():
            if node.tag!='a':continue
            parsed=urlsplit(node.attrs.get('href',''))
            if parsed.scheme or parsed.netloc or not parsed.path.startswith('/'):continue
            if not parsed.path.startswith(base_path):
                errors.append(f'{file.relative_to(output)}: link outside deployment base: {parsed.path}')
                continue
            target=output/unquote(parsed.path[len(base_path):])
            if target.is_dir():target=target/'index.html'
            if not target.is_file():errors.append(f'{file.relative_to(output)}: missing link: {parsed.path}')
    if errors:raise ValueError('\n'.join(errors))
    return count

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-path',default='/psytours/')
    parser.add_argument('--origin',default='https://9h41.github.io')
    args=parser.parse_args()
    if not re.fullmatch(r'/[\w-]+/',args.base_path):parser.error('Expected a single project path, for example /psytours/')
    origin=urlsplit(args.origin)
    if origin.scheme!='https' or not origin.netloc or origin.path not in {'','/'}:parser.error('Expected an HTTPS origin without a path')
    count=prepare(ROOT/'dist',ROOT/'.pages',args.base_path,args.origin.rstrip('/'))
    print(f'PASS: {count} deployable text files and internal links checked for {args.origin}{args.base_path}; no CNAME.')
