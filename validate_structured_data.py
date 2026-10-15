#!/usr/bin/env python3
"""Check generated JSON-LD and the two Search Console regressions.

Run after build_site.py. This is a local check, not Google's Rich Results Test.
Requirements: developers.google.com/search/docs/appearance/structured-data/dataset
and developers.google.com/search/docs/appearance/structured-data/product-snippet.
"""
import json
import pathlib
from html.parser import HTMLParser


class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.buffer = ''
        self.items = []

    def handle_starttag(self, tag, attrs):
        if tag == 'script' and dict(attrs).get('type') == 'application/ld+json':
            self.active = True
            self.buffer = ''

    def handle_data(self, data):
        if self.active:
            self.buffer += data

    def handle_endtag(self, tag):
        if tag == 'script' and self.active:
            self.items.append(json.loads(self.buffer))
            self.active = False


def nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def validate(root):
    pages = list(root.rglob('*.html'))
    datasets = tracked = blocks = 0
    assert pages, 'No generated pages found'
    for path in pages:
        parser = Markup()
        parser.feed(path.read_text())
        blocks += len(parser.items)
        all_nodes = list(nodes(parser.items))
        for node in all_nodes:
            types = node.get('@type', [])
            if isinstance(types, str):
                types = [types]
            if 'Dataset' in types:
                datasets += 1
                assert node.get('name'), path
                assert 50 <= len(node.get('description', '')) <= 5000, path
            if 'Product' in types:
                assert node.get('name'), path
                assert any(node.get(k) for k in ('offers', 'review', 'aggregateRating')), path
        if path.parent == root / 'products' and path.name != 'index.html':
            tracked += 1
            assert any(n.get('@type') == 'WebPage' and n.get('identifier') for n in all_nodes), path
            assert not any(n.get('@type') in ('Product', 'Offer', 'Review', 'AggregateRating') for n in all_nodes), path
    assert datasets and tracked, 'Expected dataset and tracking pages'
    print(f'PASS: {len(pages)} HTML pages, {blocks} JSON-LD blocks, {datasets} Dataset, {tracked} tracking pages')


if __name__ == '__main__':
    validate(pathlib.Path(__file__).parent / 'site')
