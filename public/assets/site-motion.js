// Start the entrance effects captured in the local Wix styles, without Wix runtime.
(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let observer;
  let timerIds = [];

  function clearMotion() {
    observer?.disconnect();
    observer = null;
    timerIds.forEach(clearTimeout);
    timerIds = [];
    document.querySelectorAll('#desktop-layout .site-motion-pending, #desktop-layout [data-local-motion]').forEach(element => {
      element.classList.remove('site-motion-pending');
      element.style.removeProperty('animation');
      delete element.dataset.localMotion;
    });
  }

  function initializeMotion() {
    clearMotion();
    if (reduced.matches || !('IntersectionObserver' in window)) return;
    const elements = new Map();
    function collect(rules) {
      for (const rule of rules) {
        if (rule.conditionText && rule.cssRules) {
          if (matchMedia(rule.conditionText).matches) collect(rule.cssRules);
          continue;
        }
        if (!rule.selectorText?.includes('data-motion-enter') || !rule.style) continue;
        const animation = rule.style.getPropertyValue('animation');
        if (!animation.includes('motion-') || !animation.includes('paused')) continue;
        try {
          document.querySelectorAll(`#desktop-layout ${rule.selectorText}`).forEach(element => elements.set(element, animation));
        } catch (_) { /* Ignore selectors the browser cannot apply. */ }
      }
    }
    for (const sheet of document.styleSheets) {
      if (sheet.media.mediaText && !matchMedia(sheet.media.mediaText).matches) continue;
      try { collect(sheet.cssRules); } catch (_) { /* External styles are not needed. */ }
    }
    const currentObserver = new IntersectionObserver(entries => {
      if (observer !== currentObserver) return;
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        const element = entry.target;
        currentObserver.unobserve(element);
        element.classList.remove('site-motion-pending');
        const animation = elements.get(element);
        element.dataset.localMotion = '';
        element.style.setProperty('animation', animation.replace(/\bpaused\b/g, 'running'), 'important');
        if (!animation.includes('infinite')) {
          const durations = [...animation.matchAll(/([\d.]+)ms/g)].map(match => Number(match[1]));
          timerIds.push(setTimeout(() => {
            element.style.removeProperty('animation');
            delete element.dataset.localMotion;
          }, Math.max(0, ...durations) + 100));
        }
      }
    }, { threshold: 0 });
    observer = currentObserver;
    elements.forEach((_, element) => {
      element.classList.add('site-motion-pending');
      observer.observe(element);
    });
  }

  initializeMotion();
  document.addEventListener('site-layout-changed', initializeMotion);
  reduced.addEventListener('change', initializeMotion);
})();
