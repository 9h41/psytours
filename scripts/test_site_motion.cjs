const { test } = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');

const source = fs.readFileSync('public/assets/site-motion.js', 'utf8');

function fixture(reducedMotion = false) {
  const classes = new Set();
  const styles = new Map();
  const element = {
    dataset: {},
    classList: {add: value => classes.add(value), remove: value => classes.delete(value)},
    style: {setProperty: (key, value) => styles.set(key, value), removeProperty: key => styles.delete(key)}
  };
  const listeners = {};
  const reduced = {matches: reducedMotion, addEventListener: (_, callback) => { listeners.reduced = callback; }};
  const document = {
    styleSheets: [{media: {mediaText: ''}, cssRules: [{
      selectorText: '#portrait:not([data-motion-enter="done"])',
      style: {getPropertyValue: () => 'motion-fadeIn 1200ms 1ms ease backwards 1 paused'}
    }]}],
    querySelectorAll: selector => selector.includes('site-motion-pending') ? [element] : selector.includes('#portrait') ? [element] : [],
    addEventListener: (name, callback) => { listeners[name] = callback; }
  };
  let observer;
  class IntersectionObserver {
    constructor(callback) { this.callback = callback; this.targets = []; observer = this; }
    observe(target) { this.targets.push(target); }
    unobserve() {}
    disconnect() { this.disconnected = true; }
  }
  const window = {IntersectionObserver};
  vm.runInNewContext(source, {document, window, IntersectionObserver, matchMedia: () => reduced, setTimeout: () => 1, clearTimeout() {}});
  return {element, classes, styles, reduced, listeners, get observer() { return observer; }};
}

test('starts captured animation when the element enters the viewport', () => {
  const f = fixture();
  assert.equal(f.classes.has('site-motion-pending'), true);
  f.observer.callback([{target: f.element, isIntersecting: true}]);
  assert.equal(f.classes.has('site-motion-pending'), false);
  assert.match(f.styles.get('animation'), /motion-fadeIn.*running/);
});

test('reduced motion keeps content visible and clears an active effect', () => {
  const f = fixture();
  f.observer.callback([{target: f.element, isIntersecting: true}]);
  const oldObserver = f.observer;
  f.reduced.matches = true;
  f.listeners.reduced();
  assert.equal(f.styles.has('animation'), false);
  assert.equal(f.classes.has('site-motion-pending'), false);
  assert.equal(oldObserver.disconnected, true);
  assert.doesNotThrow(() => oldObserver.callback([{target: f.element, isIntersecting: true}]));
});
