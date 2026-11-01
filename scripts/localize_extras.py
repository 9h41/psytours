"""One-time localization of the public contact widget and embedded booking button."""
from pathlib import Path
from urllib.parse import urljoin,urlsplit,quote
import hashlib
import re
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'public/assets/original'
seen={}
def asset(url):
    if url in seen:return seen[url]
    ext=Path(urlsplit(url).path).suffix or '.css'
    if 'fonts.googleapis.com' in url:ext='.css'
    target='/assets/original/'+hashlib.sha256(url.encode()).hexdigest()[:20]+ext
    seen[url]=target
    try:
        data=urllib.request.urlopen(urllib.request.Request(quote(url,safe=':/?=&,%+'),headers={'User-Agent':'Mozilla/5.0'}),timeout=60).read()
    except urllib.error.HTTPError as error:
        if error.code != 404:raise
        # The public Liberlo embed itself refers to a missing logo. Preserve that
        # empty image locally rather than introducing a different illustration.
        data=b''
        print('Original asset is missing (404): '+url)
    if ext=='.css':
        css=data.decode()
        css=re.sub(r'url\(([^)]+)\)',lambda m:'url("'+asset(urljoin(url,m.group(1).strip('"\' ')))+'")' if not m.group(1).strip('"\' ').startswith('data:') else m.group(0),css)
        css=re.sub(r'@import[ \t]*["\']([^"\']+)["\']',lambda m:'@import "'+asset(urljoin(url,m.group(1)))+'"',css)
        data=css.encode()
    (ROOT/'public'/target.lstrip('/')).write_bytes(data)
    return target

widget_css=asset('https://js.certifiedcode.io/whatsapp/czm-chat-support.css')
icon_css=asset('https://js.certifiedcode.io/whatsapp/components/font-awesome/css/solid.min.css')
widget=(ROOT/'migration/reference/contact-widget.html').read_text()
widget=re.sub(r' src="(https:[^"]+)"',lambda m:' src="'+asset(m.group(1))+'"',widget)
widget=widget.replace('data-czm-update-visibility="true"','')
(ROOT/'templates/original/contact.njk').write_text(widget)
(ROOT/'templates/original/contact-styles.njk').write_text(f'<link rel="stylesheet" href="{widget_css}">\n<link rel="stylesheet" href="{icon_css}">\n')

frame=PUBLIC/'c5b4c4db13349926ebad.html'
html=frame.read_text()
html=re.sub(r'@import url\(["\']([^"\']+)["\']\)',lambda m:'@import url("'+asset(m.group(1))+'")',html)
html=re.sub(r' src="(https:[^"]+)"',lambda m:' src="'+asset(m.group(1))+'"',html)
frame.write_text(html)
print('Localized contact styles, fonts, icons and Liberlo embed assets.')
