// The original map runs in its own third-party iframe, as it does on Wix.
// Only public coordinates and presentation settings are supplied; no site runtime.
const frame = document.getElementById('original-map');
fetch('/assets/original/map-configs.json').then(response => response.json()).then(configs => {
  const config = configs[document.body.dataset.map];
  const url = new URL(config.renderer);
  url.searchParams.set('origin', location.origin);
  frame.addEventListener('load', () => {
    frame.contentWindow.postMessage({ type: 'SET_INITIAL_LOCATIONS', data: JSON.stringify(config.settings) }, url.origin);
  }, { once: true });
  frame.src = url.href;
});
