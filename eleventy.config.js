export default function (config) {
  // Only the dedicated local watch process may render one selected draft.
  // Drafts remain excluded from collections, feeds and normal production builds.
  const previewSlug = process.argv.includes('--watch') && !process.argv.includes('--serve')
    ? process.env.PSYTOURS_PREVIEW_DRAFT : undefined;
  const previewDraft = data => previewSlug && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(previewSlug) &&
    data.page?.inputPath?.replaceAll('\\', '/').endsWith(`/content/posts/${previewSlug}.md`);
  const assetOrigin = process.argv.includes('--serve') ? 'http://localhost:8080' : 'https://www.psy-tours.fr';
  const metadataAssets = value => {
    if (typeof value === 'string') return value.startsWith('/assets/') ? new URL(value, assetOrigin).href : value;
    if (Array.isArray(value)) return value.map(metadataAssets);
    if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, metadataAssets(item)]));
    return value;
  };
  config.addFilter('metadataAssets', metadataAssets);
  config.addPassthroughCopy({ public: '/' });
  config.addCollection('posts', api => api.getFilteredByGlob('content/posts/*')
    .filter(item => !item.data.draft).sort((a, b) => b.date - a.date));
  config.addFilter('limit', (items, count) => items.slice(0, count));
  config.addFilter('additionalPosts', (items, url) => items.filter(item => item.data.additionalPost &&
    (!url?.startsWith('/blog/categories/') || (item.data.categories || []).some(c => url === `/blog/categories/${c.slug}/`))));
  config.addFilter('readableDate', date => new Intl.DateTimeFormat('fr-FR', {
    day: 'numeric', month: 'long', year: 'numeric', timeZone: 'Europe/Paris'
  }).format(new Date(date)));
  config.addFilter('isoDate', date => new Date(date).toISOString());
  config.addFilter('absolute', path => new URL(path, 'https://www.psy-tours.fr').href);
  config.addFilter('json', value => JSON.stringify(value).replace(/</g, '\\u003c'));
  config.addFilter('categoryPosts', (posts, category) => posts.filter(p => (p.data.categories || []).some(c => c.slug === category)));
  config.addFilter('canonical', url => url);
  config.addGlobalData('eleventyComputed', {
    permalink: data => data.draft && !previewDraft(data) ? false : data.permalink,
    eleventyExcludeFromCollections: data => Boolean(data.draft || data.eleventyExcludeFromCollections)
  });
  config.addTransform('lazy-content-images', function (html) {
    if (typeof this.page.outputPath !== 'string' || !this.page.outputPath.endsWith('.html')) return html;
    return html.replace(/<img\b[^>]*>/g, tag => {
      if (!tag.includes('fetchpriority=') && !tag.includes('loading=')) tag = tag.replace('<img', '<img loading="lazy"');
      if (!tag.includes('decoding=')) tag = tag.replace('<img', '<img decoding="async"');
      return tag;
    });
  });
  return { dir: { input: 'content', includes: '../templates', data: '../data', output: 'dist' },
    markdownTemplateEngine: false, htmlTemplateEngine: 'njk', templateFormats: ['md', 'njk'] };
}
