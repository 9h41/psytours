const { test } = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');

const source = fs.readFileSync('public/assets/google-reviews.js', 'utf8');

function fixture(key, fail = false) {
  class Element {
    constructor() { this.children = []; this.dataset = {}; this.hidden = false; this.attributes = {}; }
    append(...children) { this.children.push(...children); }
    replaceChildren(...children) { this.children = children; }
    setAttribute(name, value) { this.attributes[name] = value; }
    addEventListener() {}
  }
  const widget = new Element();
  widget.hidden = Boolean(key);
  widget.dataset = {apiKey: key, placeId: 'place-id'};
  const bySelector = new Map();
  widget.querySelector = selector => {
    if (!bySelector.has(selector)) bySelector.set(selector, new Element());
    return bySelector.get(selector);
  };
  widget.querySelectorAll = selector => selector.includes('average-stars') ? [widget.querySelector('stars')] : [widget.querySelector('score')];
  const window = {matchMedia: () => ({matches: true, addEventListener() {}})};
  let scripts = 0;
  const document = {
    querySelector: () => widget,
    createElement: () => new Element(),
    head: {append(script) { scripts++; queueMicrotask(() => fail ? script.onerror() : window.__psyToursMapsReady()); }}
  };
  class Place {
    constructor(options) { assert.equal(options.id, 'place-id'); }
    async fetchFields() {
      this.rating = 4.5; this.userRatingCount = 12;
      this.reviews = [{authorAttribution: {displayName: 'Test'}, rating: 4, text: 'Review'}];
      this.attributions = [];
    }
  }
  const google = {maps: {importLibrary: async () => ({Place})}};
  vm.runInNewContext(source, {document, window, google, URL, URLSearchParams, Intl, Date, Number, setTimeout, clearTimeout, console: {warn() {}}});
  return {widget, get scripts() {return scripts;}};
}

test('no configured key leaves the captured widget visible without loading Google', async () => {
  const f = fixture('');
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(f.widget.hidden, false);
  assert.equal(f.scripts, 0);
});

test('a response renders the live rating and review', async () => {
  const f = fixture('restricted-browser-key');
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(f.widget.hidden, false);
  assert.equal(f.widget.querySelector('score').textContent, '4.5');
  assert.equal(f.widget.querySelector('.google-reviews__count').textContent, '12 REVIEWS');
  assert.equal(f.widget.querySelector('.google-reviews__items').children.length, 1);
});

test('a failed Google load does not display a stale rating', async () => {
  const f = fixture('restricted-browser-key', true);
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(f.widget.hidden, true);
});
