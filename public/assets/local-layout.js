// A small adapter for the two original layouts; no Wix runtime or animations.
const desktop = document.getElementById('desktop-layout');
const mobile = document.getElementById('mobile-layout');
const desktopMarkup = desktop.innerHTML;
const narrow = window.matchMedia('(max-width: 767px)');
function applyLayout() {
  const useMobile = narrow.matches && mobile;
  document.body.classList.toggle('device-mobile-optimized', Boolean(useMobile));
  desktop.innerHTML = useMobile ? mobile.innerHTML : desktopMarkup;
  document.body.classList.remove('menu-open');
  document.getElementById('local-viewport').content = useMobile ? 'width=320, user-scalable=yes' : 'width=device-width, initial-scale=1';
  for (const item of desktop.querySelectorAll('nav li[data-state]')) {
    const link = item.querySelector('a[href]');
    if (link && new URL(link.href).pathname.replace(/\/$/, '') === location.pathname.replace(/\/$/, '')) {
      item.dataset.state = 'menu selected link';
      link.setAttribute('aria-current', 'page');
    }
  }
  for (const action of desktop.querySelectorAll('.item-link-wrapper .item-action')) {
    action.setAttribute('role', 'link');
    action.tabIndex = 0;
  }
}
applyLayout();
narrow.addEventListener('change', applyLayout);
document.addEventListener('click', event => {
  const card = event.target.closest('.item-link-wrapper');
  if (card && !event.target.closest('a,button,input')) {
    const link = card.querySelector('a[href]');
    if (link) location.assign(link.href);
  }
  const categoryButton = event.target.closest('button.V5u6Ga');
  if (categoryButton) {
    const current = categoryButton.parentElement.querySelector('[data-hook="blog-desktop-header-dropdown-menu-container"]');
    if (current) current.remove();
    else categoryButton.parentElement.append(document.getElementById('category-overflow').content.cloneNode(true));
    categoryButton.setAttribute('aria-expanded', String(!current));
  }
  const share = event.target.closest('[data-hook^="share-button__"]');
  if (share) {
    const url = document.querySelector('link[rel="canonical"]').href;
    const kind = share.dataset.hook.split('__')[1];
    const destinations = { facebook:'https://www.facebook.com/sharer/sharer.php?u=', twitter:'https://twitter.com/intent/tweet?url=', 'linked-in':'https://www.linkedin.com/sharing/share-offsite/?url=' };
    if (destinations[kind]) window.open(destinations[kind] + encodeURIComponent(url), '_blank', 'noopener');
    else if (kind === 'print') window.print();
    else if (kind === 'link') navigator.clipboard?.writeText(url);
  }
  const trigger = event.target.closest('#MENU_AS_CONTAINER_TOGGLE');
  if (trigger) {
    const menu = document.getElementById('MENU_AS_CONTAINER');
    const open = menu.dataset.staticOpen !== 'true';
    menu.dataset.staticOpen = String(open);
    menu.dataset.undisplayed = String(!open);
    trigger.setAttribute('aria-expanded', String(open));
    document.body.classList.toggle('menu-open', open);
  }
  if (event.target.closest('.czm-button,.czm-popup-close')) {
    document.querySelector('.czm-chat-support').classList.toggle('czm-popup-show');
  }
  if (event.target.closest('.czm-popup-start-chat-button')) location.href = 'tel:+33652147436';
});
document.addEventListener('keydown', event => {
  if (event.target.matches('.item-link-wrapper .item-action') && event.key === 'Enter') event.target.click();
  if (event.target.closest('#MENU_AS_CONTAINER_TOGGLE') && ['Enter', ' '].includes(event.key)) {
    event.preventDefault();
    event.target.closest('#MENU_AS_CONTAINER_TOGGLE').click();
  }
  if (event.key === 'Escape' && document.body.classList.contains('menu-open')) document.getElementById('MENU_AS_CONTAINER_TOGGLE').click();
});
document.addEventListener('submit', event => {
  if (!event.target.matches('[data-local-newsletter]')) return;
  event.preventDefault();
  const input = event.target.querySelector('input[type="email"]') || event.target.querySelector('input');
  if (input) {
    input.setCustomValidity('L’inscription à la newsletter n’est pas disponible dans cet aperçu local.');
    input.reportValidity();
    input.addEventListener('input', () => input.setCustomValidity(''), { once: true });
  }
});
