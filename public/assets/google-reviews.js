// The Maps browser key is intentionally public and must be origin/API restricted.
const reviewWidget = document.querySelector('.google-reviews');
const reviewTeaser = reviewWidget?.querySelector('.google-reviews__toggle');
const desktopReview = window.matchMedia('(min-width: 768px)');
let reviewRequestStarted = false;

reviewTeaser?.addEventListener('mouseenter', () => {
  if (window.matchMedia('(hover: hover)').matches && !reviewWidget.open) reviewWidget.open = true;
});

function makeReviewElement(tag, className, value) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (value != null) element.textContent = value;
  return element;
}

function safeGoogleLink(url) {
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'https:' && (parsed.hostname === 'google.com' || parsed.hostname.endsWith('.google.com')) ? parsed.href : '';
  } catch { return ''; }
}

function makeReview(review) {
  const author = review.authorAttribution;
  if (!author?.displayName) return null;
  const article = makeReviewElement('article', 'google-reviews__review');
  const avatar = makeReviewElement('span', 'google-reviews__avatar', author.displayName.slice(0, 1));
  if (author.photoURI) {
    try {
      const photoUrl = new URL(author.photoURI);
      if (photoUrl.protocol === 'https:' && (photoUrl.hostname === 'googleusercontent.com' || photoUrl.hostname.endsWith('.googleusercontent.com'))) {
        const photo = makeReviewElement('img');
        photo.src = photoUrl.href;
        photo.alt = '';
        avatar.replaceChildren(photo);
      }
    } catch { /* Keep the initials if Google supplies an invalid URL. */ }
  }
  const body = makeReviewElement('div', 'google-reviews__body');
  const profile = safeGoogleLink(author.uri);
  const name = makeReviewElement(profile ? 'a' : 'span', 'google-reviews__name', author.displayName);
  if (profile) { name.href = profile; name.target = '_blank'; name.rel = 'noopener noreferrer'; }
  body.append(name);
  if (typeof review.rating === 'number') {
    const stars = makeReviewElement('div', 'google-reviews__stars', '★'.repeat(Math.max(0, Math.min(5, Math.round(review.rating)))));
    stars.setAttribute('aria-label', `${review.rating} étoiles sur 5`);
    body.append(stars);
  }
  if (review.publishTime instanceof Date && !Number.isNaN(review.publishTime.valueOf())) {
    body.append(makeReviewElement('div', '', new Intl.DateTimeFormat('fr-FR', {dateStyle: 'medium'}).format(review.publishTime)));
  }
  if (Number.isInteger(review.visitDateYear) && Number.isInteger(review.visitDateMonth)) {
    const visit = new Date(Date.UTC(review.visitDateYear, review.visitDateMonth, 1));
    body.append(makeReviewElement('div', '', `Visite : ${new Intl.DateTimeFormat('fr-FR', {month: 'long', year: 'numeric', timeZone: 'UTC'}).format(visit)}`));
  }
  const text = review.originalText || review.text;
  if (text) body.append(makeReviewElement('p', 'google-reviews__review-text', text));
  const reviewLink = safeGoogleLink(review.googleMapsURI);
  if (reviewLink) {
    const link = makeReviewElement('a', '', 'Voir cet avis sur Google Maps');
    link.href = reviewLink; link.target = '_blank'; link.rel = 'noopener noreferrer';
    body.append(link);
  }
  article.append(avatar, body);
  return article;
}

async function loadGoogleReviews() {
  if (!reviewWidget || reviewRequestStarted || !desktopReview.matches || !reviewWidget.dataset.apiKey) return;
  reviewRequestStarted = true;
  try {
    await new Promise((resolve, reject) => {
      const script = document.createElement('script');
      const url = new URL('https://maps.googleapis.com/maps/api/js');
      url.search = new URLSearchParams({key: reviewWidget.dataset.apiKey, loading: 'async', callback: '__psyToursMapsReady', language: 'fr'}).toString();
      const timer = setTimeout(() => reject(new Error('Google Maps timed out')), 15000);
      window.__psyToursMapsReady = () => { clearTimeout(timer); resolve(); delete window.__psyToursMapsReady; };
      script.onerror = () => { clearTimeout(timer); reject(new Error('Google Maps could not load')); delete window.__psyToursMapsReady; };
      script.src = url.href;
      script.async = true;
      document.head.append(script);
    });
    const {Place} = await google.maps.importLibrary('places');
    const place = new Place({id: reviewWidget.dataset.placeId, requestedLanguage: 'fr'});
    await place.fetchFields({fields: ['rating', 'userRatingCount', 'reviews']});
    if (!Number.isFinite(place.rating) || !Number.isInteger(place.userRatingCount)) throw new Error('Rating unavailable');
    const rating = place.rating.toFixed(1);
    for (const element of reviewWidget.querySelectorAll('.google-reviews__score, .google-reviews__large-score')) element.textContent = rating;
    for (const element of reviewWidget.querySelectorAll('.google-reviews__average-stars')) {
      const count = Math.max(0, Math.min(5, Math.round(place.rating)));
      element.textContent = '★'.repeat(count) + '☆'.repeat(5 - count);
      element.setAttribute('aria-label', `${rating} étoiles sur 5`);
    }
    reviewWidget.querySelector('.google-reviews__count').textContent = `${place.userRatingCount} REVIEWS`;
    reviewWidget.querySelector('.google-reviews__total').textContent = `Based on ${place.userRatingCount} reviews`;
    const items = reviewWidget.querySelector('.google-reviews__items');
    for (const review of place.reviews || []) {
      const element = makeReview(review);
      if (element) items.append(element);
    }
    for (const attribution of place.attributions || []) {
      const provider = typeof attribution === 'string' ? attribution : attribution.provider;
      if (!provider) continue;
      const link = typeof attribution === 'string' ? '' : safeGoogleLink(attribution.providerURI);
      const element = makeReviewElement(link ? 'a' : 'span', '', provider);
      if (link) { element.href = link; element.target = '_blank'; element.rel = 'noopener noreferrer'; }
      reviewWidget.querySelector('.google-reviews__attributions').append(element);
    }
    reviewWidget.hidden = false;
  } catch (error) {
    console.warn('Google reviews unavailable:', error.message);
  }
}

desktopReview.addEventListener('change', loadGoogleReviews);
loadGoogleReviews();
