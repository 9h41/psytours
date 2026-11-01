export default function (config) {
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
    permalink: data => data.draft ? false : data.permalink
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
