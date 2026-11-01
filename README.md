# Psy-Tours

Version statique du site d’Elisa Gatay-Hauet, psychopraticienne en Gestalt-thérapie à Tours.

Le site final est constitué de fichiers HTML, d’une feuille CSS, d’images locales et d’un PDF. Aucun serveur applicatif, compte CMS, base de données ou JavaScript côté visiteur n’est nécessaire. Eleventy sert uniquement à fabriquer ces fichiers à partir de textes Markdown et de modèles partagés.

## Modifier le site avec un agent

Vous pouvez simplement demander, par exemple :

- « Prépare un article sur la difficulté à dire non, en brouillon, avec le même ton que les articles existants. »
- « Voici mon texte : ajoute-le comme article, dans la catégorie Relations, puis montre-moi le résultat. »
- « Ajoute une page sur les consultations en visio et propose un lien dans le menu. »
- « Remplace le numéro de téléphone partout sur le site. »
- « Montre-moi les changements sur téléphone avant toute mise en ligne. »

L’agent lit `AGENTS.md`, prépare le contenu, génère un aperçu et contrôle les liens. Une modification locale ou un changement de statut de brouillon **ne met rien en ligne**. La mise en ligne doit être demandée explicitement.

## Commandes pour les agents

Pré-requis : Node.js 22 ou plus récent ; Python 3 pour les contrôles.

```sh
rtk npm ci
rtk npm run dev
# Aperçu : http://localhost:8080

rtk npm run check
# Résultat à héberger : dist/ uniquement

rtk npm run new -- post poser-ses-limites "Poser ses limites"
rtk npm run new -- page mon-accompagnement "Mon accompagnement"
```

Les nouveaux fichiers commencent avec `draft: true` : ils sont exclus du HTML, du blog, des catégories, du flux et du sitemap. Pour un aperçu du texte final, l’agent peut passer `draft` à `false` localement après validation éditoriale. Le déploiement reste une action distincte.

## Organisation

| Emplacement | Contenu |
| --- | --- |
| `content/pages/` | Textes des pages, dont l’accueil |
| `content/posts/` | Articles, dates, auteurs et catégories |
| `data/site.json` | Coordonnées et lien de réservation partagés |
| `data/categories.json` | Catégories et adresses historiques |
| `templates/` | Modèles communs et navigation |
| `public/assets/` | Images WebP, PDF, favicon et CSS |
| `migration/` | Archives Wix, captures et inventaires ; jamais déployés |
| `docs/migration.md` | Décisions, limites et préparation du changement d’hébergement |

Les articles apparaissent automatiquement sur le blog, dans leurs catégories, dans le flux Atom et dans le sitemap. L’accueil montre les trois articles les plus récents. Une nouvelle page doit recevoir un lien pertinent dans un menu ou dans un texte existant.

## Mise en ligne ultérieure

Lire `docs/migration.md`. `dist/` peut être servi par un hébergeur statique. La configuration doit gérer les répertoires avec `index.html`, les URL accentuées, la page 404 et les redirections. Ne pas remplacer les pages inconnues par l’accueil avec une réponse 200.

Le site Wix de production n’a pas été modifié.
