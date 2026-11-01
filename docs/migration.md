# Migration du site Wix — 1er novembre 2026

## Inventaire et sources

Source publique : https://www.psy-tours.fr. Les trois sitemaps Wix ont fourni 32 URL uniques : 8 pages d’information (accueil compris), 11 articles, le blog et 12 catégories. Ces routes sont reproduites, avec une barre oblique finale adaptée à l’hébergement statique. Les anciennes adresses sans barre oblique doivent être redirigées par l’hébergeur vers leur répertoire.

`migration/source/manifest.json` associe chaque URL à son HTML d’origine. Les XML et HTML complets sont conservés. `content-import.json` donne la correspondance avec les textes migrés ; `assets.json` garde les sources des images et du PDF avant optimisation. Les tailles de cet inventaire sont celles de l’import, avant recompression. Les captures dans `migration/screenshots/` conservent les références visuelles de l’accueil, du blog, d’un article, du programme et de la prise de rendez-vous.

Une ancienne adresse `/services-3`, trouvée dans un article, redirige chez Wix vers `/prendre-rendez-vous`. Le lien interne a été corrigé ; la règle 301 est fournie dans `public/_redirects`. Ce format est interprété par certains hébergeurs, et doit être transposé dans la configuration des autres.

## Choix techniques

- **Eleventy 3.1.7, dépendance de développement uniquement.** Il apporte Markdown, modèles partagés, brouillons, catégories et génération automatique du blog, du sitemap et d’un flux Atom. Cela évite la duplication du HTML et un moteur Markdown artisanal. Documentation : https://www.11ty.dev/docs/.
- **Aucun CMS hébergé.** Le besoin actuel est la rédaction assistée par agents ; une interface d’administration, une authentification et une base de données n’apporteraient pas de valeur suffisante.
- **Aucun JavaScript visiteur.** Le menu mobile utilise le composant HTML natif `details`. L’aperçu Eleventy injecte son propre outil de rechargement uniquement en développement.
- Polices système et Georgia : aucune police distante, aucune requête Google Fonts.
- Images et PDF copiés localement. Les 30 images importées ont été recompressées en WebP : environ 15,7 Mo → 2,6 Mo. Le portrait de l’accueil est un recadrage du visuel existant, sans modification du visage ; le visuel entier est conservé dans `migration/assets/`.
- Nouvelle mise en page responsive, palette crème, olive et rose inspirée du site existant. La mise en page Wix n’est pas reproduite pixel pour pixel. Le titre d’accueil et quelques textes d’interface sont reformulés ; les textes des articles sont conservés.
- `npm run build` recrée `dist/` pour éviter qu’une ancienne page supprimée ou repassée en brouillon reste dans un déploiement.

## Fonctions conservées ou adaptées

| Fonction Wix | Version statique |
| --- | --- |
| Pages d’information | Markdown + HTML sémantique |
| Blog et catégories | Archives générées, dates et auteurs conservés |
| Réservation | Lien existant vers Psychologue.net, téléphone, email |
| Bibliographie | Livres et liens libraires conservés |
| Histoire de la thérapie | PDF local, lien depuis l’accueil |
| Newsletter Wix CRM | Formulaire retiré ; flux Atom disponible ; aucun faux message d’inscription réussie |
| Voyage intérieur | Présentation et illustrations conservées, contact par email |
| Commentaires / likes / compteur Wix | Non repris : pas de service social ni de base de données |
| Suivi et widgets Wix | Retirés ; aucun outil de mesure ou cookie ajouté |

Le contenu public du Voyage intérieur ne révèle ni les vidéos et exercices privés, ni un lecteur de cours ni un processus d’inscription utilisable. La migration couvre sa présentation publique. Un éventuel espace de cours, des membres, des paiements, les contacts CRM et les abonnements email nécessitent un export ou une intégration séparée, si ces fonctions existent et doivent être conservées. Les données privées ne sont pas accessibles par une capture publique.

## Points éditoriaux constatés

- Les pages actuelles de rendez-vous et de visio indiquent **80 € pour 45 minutes**. Certaines descriptions SEO et six articles plus anciens indiquent **70 €**. Les descriptions des pages actuelles sont alignées sur 80 €. Les articles datés restent fidèles à la source et portent une note renvoyant vers les conditions actuelles.
- La page d’accueil Wix évoque Paris dans une phrase, alors que le pied de page, la biographie et les autres pages détaillent Tours et la visio. La nouvelle interface indique Tours et visio ; une présence à Paris reste à confirmer avant de l’ajouter.
- La source comporte quelques coquilles, notamment « ce allowing » dans la page Gestalt et « Catherie Clouzard » dans la bibliographie. Elles restent visibles pour éviter une réécriture substantielle silencieuse ; leur correction éditoriale pourra être demandée.
- Les témoignages existants et leurs attributions sont conservés. Aucun avis ni résultat clinique n’a été ajouté.
- Les mentions d’urgence existantes sont reprises de la source ; aucun nouveau conseil clinique n’est rédigé.

## Vérifications

`npm run check` génère le site et vérifie : couverture des 32 routes, couverture du sitemap, liens et fichiers locaux, un titre H1 par page, métadonnées, langue française, XML valide, données structurées valides, absence de runtime et d’assets Wix distants dans le HTML, absence d’archives dans le déploiement. Une comparaison séparée des mots des 11 articles avec leur HTML archivé n’a trouvé aucun mot manquant.

L’aperçu a été contrôlé sur ordinateur et sur un écran de 390 px : navigation mobile, liens de rendez-vous et absence de débordement horizontal. Ces contrôles ne constituent pas un audit complet d’accessibilité ou une certification de performance.

Les résultats des contrôles sur cinq pages représentatives à 390 et 1440 px sont conservés dans `migration/responsive-check.json`. La comparaison des articles est enregistrée dans `migration/article-text-check.json` ; elle contrôle les mots, sans prouver l’ordre de chaque phrase. Le cycle complet création d’un brouillon → activation locale → retour en brouillon a également été vérifié, y compris le retrait du HTML et des index.

L’installation signale trois avis npm de sévérité modérée liés à `minimatch` via `@11ty/recursive-copy`. Ce sont des outils de fabrication, absents du site déployé. Aucun remplacement forcé par une version incompatible n’a été appliqué. Réexaminer les avis lors de la prochaine mise à jour d’Eleventy.

## Avant changement de production

1. Faire relire les textes, les tarifs, les images et le nouvel aspect par Elisa.
2. Choisir l’hébergement statique et configurer HTTPS, domaine canonique `www.psy-tours.fr`, redirection du domaine nu, répertoires `index.html`, URL accentuées et véritable réponse 404.
3. Appliquer la redirection `/services-3` et importer toute autre redirection connue depuis l’administration Wix. L’inventaire public ne peut garantir la découverte de toutes les anciennes adresses.
4. Décider si une newsletter ou un espace privé de cours doit être conservé, puis exporter les données nécessaires et installer un service adapté avant bascule.
5. Déployer uniquement `dist/` sur un environnement de prévisualisation ; vérifier les liens, le PDF, les réservations externes, le sitemap et les redirections sur l’hébergement réel.
6. Demander l’autorisation explicite de mise en ligne ; ensuite seulement effectuer la bascule DNS. Conserver l’ancien site et une possibilité de retour arrière jusqu’à validation.

Aucun changement DNS, envoi de formulaire, abonnement, paiement ou publication n’a été effectué pendant cette migration.
