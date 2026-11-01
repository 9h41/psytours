# Psy-Tours — copie locale du site Wix

Cette version reprend la présentation de https://www.psy-tours.fr : textes, polices, couleurs, images, menus, pied de page fixe et blog. La seule modification visuelle demandée est l’arrondi supérieur de la photo principale. Les animations Wix sont retirées.

Le premier essai, avec une présentation différente, est conservé dans le commit Git `bb7b400`.

## Utilisation avec un agent

Vous pouvez demander simplement :

- « Lance le site en local pour que je le relise. »
- « Remplace ce paragraphe sur la page Qui suis-je, sur ordinateur et téléphone. »
- « Prépare ce texte comme nouvel article, sans le publier. »
- « Ajoute une page sur ce sujet, en gardant la présentation actuelle. »

L’agent doit lire `AGENTS.md`, préparer les changements, vérifier les deux mises en page et montrer le résultat. Rien n’est publié automatiquement.

## Lancer et vérifier

Prérequis : Node.js 22+ et Python 3.

```sh
rtk npm ci
rtk npm run dev
# http://localhost:8080

rtk npm run check
# Fichiers à héberger : dist/ uniquement

rtk npm run new -- post mon-article "Titre de mon article"
rtk npm run new -- page ma-page "Titre de ma page"
```

Les nouveaux fichiers sont des brouillons Markdown. Les pages migrées utilisent du HTML/Nunjucks pour garder leur mise en forme exacte. Eleventy génère les fichiers statiques ; aucun CMS ou serveur applicatif n’est nécessaire pour les servir.

## Organisation

| Dossier | Usage |
| --- | --- |
| `content/pages/` | Pages existantes et nouvelles pages |
| `content/posts/` | Articles |
| `content/archives/` | Catégories existantes |
| `templates/original/` | Présentation mobile, éléments partagés et menus d’origine |
| `public/assets/original/` | Polices et images locales |
| `public/assets/fidelity.css` | Arrondi et adaptation statique des mises en page |
| `migration/` | Sources archivées, inventaires et preuves visuelles, jamais déployés |

Les nouveaux articles apparaissent sur le blog, dans les catégories correspondantes, le sitemap et le flux. Une nouvelle page doit recevoir un lien dans le contenu ou un menu.

Les images, vidéos, polices, fichiers et aperçus de partage sont hébergés localement avec le site. Les cartes interactives chargent directement Google Maps, seule exception externe approuvée ; elles utilisent son interface standard. Le formulaire de newsletter et les compteurs gardent leur présentation originale ; leur service en ligne n’est pas simulé. Consulter `docs/fidelity.md` pour les limites de services et la préparation de production.

Le site Wix et le DNS de production n’ont pas été modifiés.
