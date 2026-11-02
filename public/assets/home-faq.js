document.addEventListener('click', event => {
  const tab = event.target.closest('.home-faq [role="tab"]');
  if (!tab) return;
  const faq = tab.closest('.home-faq');
  faq.querySelectorAll('[role="tab"]').forEach(button => button.setAttribute('aria-selected', String(button === tab)));
  faq.querySelector('input').value = '';
  faq.querySelectorAll('.home-faq__item').forEach(item => { item.hidden = item.dataset.category !== tab.dataset.category; item.open = false; });
});

document.addEventListener('input', event => {
  if (!event.target.matches('.home-faq input')) return;
  const faq = event.target.closest('.home-faq');
  const term = event.target.value.trim().toLocaleLowerCase('fr');
  const selected = faq.querySelector('[role="tab"][aria-selected="true"]').dataset.category;
  faq.querySelectorAll('.home-faq__item').forEach(item => {
    item.hidden = term ? !item.textContent.toLocaleLowerCase('fr').includes(term) : item.dataset.category !== selected;
    item.open = false;
  });
});
