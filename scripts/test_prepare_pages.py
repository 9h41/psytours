"""Ensure project-site URL rewriting preserves fidelity and external links."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from prepare_pages import prepare, rewrite_urls
from check_assets import audit_assets

class PagesTests(unittest.TestCase):
    def test_svg_masks_and_self_closing_elements_stay_intact(self):
        mask="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 0h10v10z'/%3E%3C/svg%3E"
        svg='<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0h10v10z"/></svg>'
        source=f'.image{{mask-image:url("{mask}")}}\n{svg}\n<img src="/assets/photo.jpg"/>'
        result=rewrite_urls(source,'/psytours/','https://9h41.github.io')
        self.assertIn(mask,result)
        self.assertIn(svg,result)
        self.assertIn('<img src="/psytours/assets/photo.jpg"/>',result)
        self.assertNotIn("'/psytours/%3E",result)

    def test_all_url_contexts_and_unrelated_content(self):
        source='''<a href="/">Accueil</a><a href="/blog/">Blog</a>
<template><img src="/assets/a.jpg" srcset="/assets/a.jpg 1x, /assets/b.jpg 2x"></template>
<style>.x{background:url(/assets/a.jpg);grid-area:1 / 1 / 2 / 2}</style>
<meta content="https://www.psy-tours.fr/assets/a.jpg">
<a href="https://www.psy-tours.fr/">Source</a><iframe src="https://maps.google.com/maps?q=Tours"></iframe>'''
        result=rewrite_urls(source,'/psytours/','https://9h41.github.io')
        self.assertIn('href="/psytours/"',result)
        self.assertIn('href="/psytours/blog/"',result)
        self.assertIn('srcset="/psytours/assets/a.jpg 1x, /psytours/assets/b.jpg 2x"',result)
        self.assertIn('url(/psytours/assets/a.jpg)',result)
        self.assertIn('grid-area:1 / 1 / 2 / 2',result)
        self.assertIn('https://9h41.github.io/psytours/assets/a.jpg',result)
        self.assertIn('href="https://www.psy-tours.fr/"',result)
        self.assertIn('https://maps.google.com/maps?q=Tours',result)

    def test_artifact_stays_separate_and_checks_embedded_assets(self):
        with TemporaryDirectory() as directory:
            root=Path(directory); source=root/'dist'; output=root/'pages'
            (source/'assets').mkdir(parents=True)
            (source/'prendre-rendez-vous').mkdir()
            (source/'prendre-rendez-vous/index.html').write_text('<html><head></head><body></body></html>')
            (source/'index.html').write_text('<html><head></head><body><iframe src="/assets/frame.html"></iframe></body></html>')
            (source/'assets/frame.html').write_text('<img src="/assets/photo.jpg">')
            (source/'assets/photo.jpg').write_bytes(b'fixture')
            (source/'CNAME').write_text('unwanted.example')
            prepare(source,output,'/psytours/','https://9h41.github.io')
            self.assertNotIn('noindex', (source/'index.html').read_text())
            self.assertIn('noindex', (output/'index.html').read_text())
            self.assertFalse((output/'CNAME').exists())
            self.assertTrue((output/'services-3/index.html').is_file())
            self.assertEqual([],audit_assets(output,'/psytours/','https://9h41.github.io')[0])
            (output/'assets/frame.html').write_text('<img src="/assets/photo.jpg">')
            self.assertTrue(audit_assets(output,'/psytours/','https://9h41.github.io')[0])
