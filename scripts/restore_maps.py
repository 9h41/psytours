"""Extract public map settings and keep the original isolated map service."""
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
import json
import urllib.request
from html_tree import Tree

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'migration/reference'
def walk(value):
    if isinstance(value,dict):
        yield value
        for item in value.values():yield from walk(item)
    elif isinstance(value,list):
        for item in value:yield from walk(item)

configs={}
for page in ['qui-suis-je','etique-et-déonthologie']:
    tree=Tree((REF/'raw'/(page+'.html')).read_text()).root
    link=tree.find(lambda n:n.tag=='link' and n.attrs.get('id','').startswith('features_') and n.attrs.get('id')!='features_masterPage')
    data=urllib.request.urlopen(link.attrs['href'],timeout=40).read()
    (REF/(page+'-features.json')).write_bytes(data)
    for item in walk(json.loads(data)):
        if 'mapData' not in item:continue
        identifier=parse_qs(item['urlQueries'])['id'][0]
        configs[identifier]=item['mapData']

manifest=json.loads((REF/'asset-manifest.json').read_text())
for record in manifest:
    if '/googleMap.' not in record['source']:continue
    identifier=parse_qs(urlsplit(record['source']).query)['id'][0]
    if identifier not in configs:raise ValueError('Missing map settings: '+identifier)
    configs[identifier]={'settings':configs[identifier],'renderer':record['source']}
    (ROOT/'public'/record['path'].lstrip('/')).write_text('<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>html,body,iframe{margin:0;width:100%;height:100%;border:0;overflow:hidden}</style></head><body data-map="'+identifier+'"><iframe id="original-map" title="Google Maps" allowfullscreen></iframe><script src="/assets/map-frame.js"></script></body></html>')
(ROOT/'public/assets/original/map-configs.json').write_text(json.dumps(configs,ensure_ascii=False))
print('Restored original map styles, markers, controls and zoom for both map instances.')
