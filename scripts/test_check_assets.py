"""Regression cases for the deployable asset-locality guarantee."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from check_assets import audit_assets

class LocalAssetsTests(unittest.TestCase):
    def audit(self,html='',css=''):
        with TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'index.html').write_text(html)
            (root/'styles.css').write_text(css)
            (root/'photo.jpg').write_bytes(b'fixture')
            return audit_assets(root)[0]

    def test_hotlinks_are_rejected_in_every_asset_context(self):
        cases=[
            '<img src="https://static.wixstatic.com/media/photo.jpg">',
            '<img src="/photo.jpg" srcset="/photo.jpg 1x, https://example.org/photo.jpg 2x">',
            '<video poster="https://example.org/poster.jpg"></video>',
            '<link rel="stylesheet" href="https://example.org/styles.css">',
            '<meta property="og:image" content="https://example.org/social.jpg">',
            '<script type="application/ld+json">{"image":{"@type":"ImageObject","url":"https://example.org/social.jpg"}}</script>',
            '<svg><image href="https://example.org/photo.jpg"/></svg>',
            '<style>@import "https://fonts.googleapis.com/css?family=Example";</style>',
            '<iframe src="https://static.parastorage.com/map.html"></iframe>',
            '<img src="https://maps.google.com/photo.jpg">',
        ]
        for html in cases:
            with self.subTest(html=html):self.assertTrue(self.audit(html))
        self.assertTrue(self.audit(css='@font-face{src:url(https://example.org/font.woff2)}'))

    def test_local_assets_and_navigation_are_allowed(self):
        self.assertEqual([],self.audit('<img src="/photo.jpg"><a href="https://example.org/booking">Réserver</a><link rel="canonical" href="https://www.psy-tours.fr/">'))

    def test_only_direct_google_map_frames_are_exempt(self):
        self.assertEqual([],self.audit('<iframe src="https://maps.google.com/maps?q=Tours&output=embed"></iframe>'))
        self.assertTrue(self.audit('<iframe src="https://maps.google.com/not-a-map"></iframe>'))

    def test_missing_local_files_are_rejected(self):
        self.assertTrue(self.audit('<img src="/missing.jpg">'))

if __name__=='__main__':unittest.main()
