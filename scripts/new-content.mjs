import { existsSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const [kind, slug, ...words] = process.argv.slice(2);
if (!['page', 'post'].includes(kind) || !slug || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug) || !words.length) {
  console.error('Usage: npm run new -- page|post slug "Titre de la page"');
  process.exit(1);
}
const title = words.join(' ');
const target = resolve('content', kind === 'post' ? 'posts' : 'pages', `${slug}.md`);
if (existsSync(target)) throw new Error('Ce fichier existe déjà : ' + target);
const fields = {
  title, description: 'À compléter avant publication.',
  permalink: `${kind === 'post' ? '/post' : ''}/${slug}/`,
  layout: `${kind}.njk`, draft: true,
  ...(kind === 'post' ? { tags: ['posts'], date: new Date().toISOString(), updated: new Date().toISOString(),
    author: 'Elisa Gatay-Hauet', image: '/assets/e9956e39b637e044.webp', imageAlt: 'Elisa Gatay-Hauet', categories: [] } : {})
};
writeFileSync(target, '---\n' + Object.entries(fields).map(([key, value]) => `${key}: ${JSON.stringify(value)}`).join('\n') + '\n---\n\nVotre texte commence ici.\n', { flag: 'wx' });
console.log(`Brouillon créé : ${target}\nIl est exclu du site tant que draft: true.`);
