"""Write local wrappers for the explicitly approved direct Google Maps service.

No Wix map renderer, billing client, scripts, icons or configuration are used.
"""
from pathlib import Path
from html import escape
from urllib.parse import urlencode

ROOT=Path(__file__).resolve().parents[1]
url='https://maps.google.com/maps?'+urlencode({
    'q':'22 Rue des Halles, 37000 Tours, France',
    'll':'47.3935091,0.6856165','z':15,'hl':'fr','output':'embed'
})
markup='<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>html,body,iframe{margin:0;width:100%;height:100%;border:0;overflow:hidden}</style></head><body><iframe title="Cabinet — 22 rue des Halles à Tours" src="'+escape(url,quote=True)+'" allowfullscreen loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></body></html>'
for name in ['1faf59318048136c87d4.html','5f2bae6492bf239185f3.html']:
    (ROOT/'public/assets/original'/name).write_text(markup)
print('Both maps load directly from Google; no Wix map assets.')
