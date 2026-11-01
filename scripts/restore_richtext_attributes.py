"""One-time restoration of CSS presentation attributes in imported rich text.

Match the captured rich-text tree structurally, preserving current local assets
and content. Fail rather than silently attach attributes to the wrong element.
"""
import json
from pathlib import Path
from urllib.parse import urlsplit, unquote

from html_tree import Tree, Node
from restore_fidelity import ROOT, serialize

reference = ROOT/'migration/reference'
manifest=json.loads((reference/'manifest.json').read_text())
attributes={'data-gap-spacer-top-margin','data-breakout','data-ricos-font','data-ricos-responsive','data-font-size','data-list-style','data-list-style-position','data-heading-level','data-type','data-indent','data-color'}
ignored={'script','style','noscript','link','meta','title'}

def viewer(root):
    return root.find(lambda n:'jRZWf' in n.attrs.get('class','').split())

def copy_attributes(source,target):
    normalized={'wow-image':'div','wix-dropdown-menu':'nav'}
    assert normalized.get(source.tag,source.tag)==target.tag, (source.tag,target.tag)
    copied=0
    for key in attributes:
        if key in source.attrs:
            target.attrs[key]=source.attrs[key]
            copied+=1
    children=lambda node:[c for c in node.children if isinstance(c,Node) and c.tag not in ignored]
    left,right=children(source),children(target)
    assert len(left)==len(right),(source.tag,source.attrs,len(left),len(right))
    for a,b in zip(left,right):copied+=copy_attributes(a,b)
    return copied

total=0
for record in manifest:
    route=unquote(urlsplit(record['url']).path)
    if not route.startswith('/post/'):continue
    slug=route.strip('/').split('/')[-1]
    target=ROOT/'content/posts'/f'{slug}.njk'
    front,body=target.read_text().split('\n---\n',1)
    source=Tree((reference/record['file']).read_text()).root
    local=Tree(body).root
    total+=copy_attributes(viewer(source),viewer(local))
    target.write_text(front+'\n---\n'+serialize(local))
    mobile=ROOT/'templates/original'/f'post__{slug}.mobile.html'
    original_mobile=Tree((reference/'mobile'/record['file']).read_text()).root
    local_mobile=Tree(mobile.read_text()).root
    total+=copy_attributes(viewer(original_mobile),viewer(local_mobile))
    mobile.write_text(serialize(local_mobile))
print(f'Restored {total} rich-text presentation attributes across 11 desktop/mobile articles.')
