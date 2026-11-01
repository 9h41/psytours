# Restauration de la fidélité Wix — 1er novembre 2026

Ce document remplace les choix de présentation du premier essai décrits dans `migration.md`. Le propriétaire a demandé une copie visuelle exacte. Le dépôt Git a été initialisé et l’intégralité des sources du premier essai sauvegardée dans `bb7b400` **avant** les changements ci-dessous. Aucun push n’a été effectué.

## Référence

La nouvelle référence est le site Wix public, avec des captures fraîches dans `migration/reference/raw/` et `migration/reference/mobile/`. Les contenus de pages après rendu sont également conservés. Le site utilise des mises en page différentes sur ordinateur et téléphone ; les deux sont reprises.

Les 32 routes des sitemaps et 37 archives de tags découvertes dans les articles sont reproduites : 69 routes publiques, plus une page 404. Les textes, prix, mentions de Paris, titres, champs de formulaire, images, logos, crédits et métadonnées sont repris de la source. Aucune correction éditoriale n’est appliquée sans demande.

## Modification autorisée

Seul le bord supérieur de l’image principale peut différer du cadrage Wix. Les animations sont désactivées. Le site public a changé pendant la migration : le montage initial de l’accueil a été remplacé sur Wix par un portrait séparé du texte. La version locale reprend maintenant ce nouveau visuel et son cadrage actuel, avec l’arrondi conservé.

## Conversion statique

- Les scripts, modèles JSON d’application, télémétrie et dépendances au runtime Wix sont retirés.
- Les styles et identifiants de présentation nécessaires sont conservés pour éviter une approximation du rendu. Les pages existantes restent du HTML dans des modèles Nunjucks, avec des éléments partagés.
- Les polices et images sont locales. Les PNG les plus lourds ont été convertis **sans perte** en WebP, avec conservation des pixels, et les anciennes ressources inutilisées du premier essai supprimées.
- Un petit script local choisit la variante mobile et gère les menus, le partage et le retour explicite du formulaire dans l’aperçu. Il ne charge pas Wix.
- Les cartes du blog Wix sont virtualisées. La capture a été complétée par plusieurs positions de défilement pour récupérer les 11 cartes entières sur ordinateur. Sur téléphone, les quatre cartes absentes du HTML initial réutilisent la structure mobile originale, les textes des articles et les mêmes paramètres de cadrage d’image. Les 11 cartes sont présentes dans les deux mises en page.
- Les variantes d’images pour écrans haute densité sont également locales. Les fichiers identiques sont mutualisés et les images de préchargement floutées, liées aux animations, sont retirées.
- Une règle de placement du repeater de la page Gestalt est nécessaire : Wix l’injectait après le démarrage. Elle est extraite dans une feuille CSS locale.
- Les nouvelles pages et articles peuvent être rédigés en Markdown avec des modèles basés sur la présentation d’origine. Les nouveaux articles sont ajoutés au blog et aux catégories par un point d’extension qui n’altère pas les cartes déjà migrées.

## Services et limites

La photo du cabinet sur l’accueil mobile utilisait initialement la miniature de chargement Wix (80×77 px). Elle est remplacée par trois variantes locales issues de la même image et du même cadrage : 320×306, 640×612 et 960×918 px. Le navigateur sélectionne la densité adaptée, sans modifier la taille de la section. Le sérialiseur reconnaît désormais les métadonnées `isLQIP` et conserve les sources responsives.

La copie statique ne peut pas recréer à elle seule les services Wix CRM et les données privées. Le formulaire de newsletter conserve son apparence, mais une soumission locale affiche un message d’indisponibilité au lieu d’une fausse confirmation. Les vues, commentaires et likes sont des valeurs de la capture ; aucune persistance n’est inventée.

Les réservations externes conservent leurs destinations. Le bouton Liberlo est localisé ; son logo est déjà manquant sur le site source (HTTP 404) et n’a pas été remplacé par une autre illustration. Le contrôle de contact conserve sa présentation et permet d’appeler le numéro public.

Le propriétaire a ensuite demandé que tous les médias et ressources soient locaux. Les 19 dernières URL de médias Wix ont été localisées, y compris les images Open Graph/JSON-LD et une vidéo de fond. Les commentaires de source maps distantes et les appels externes du bouton Liberlo ont été retirés ou localisés. La génération contrôle aussi les ressources des pages HTML embarquées.

Le propriétaire a explicitement choisi de conserver les cartes **Google Maps interactives** comme exception. Les enveloppes locales chargent désormais Google directement, sans moteur, script, icône ni configuration Wix. L’interface et les couleurs sont celles de l’intégration Google standard. La carte à la même adresse a été vérifiée dans l’aperçu local. Les anciens réglages du widget sont archivés uniquement dans `migration/reference/previous-map-configs.json`. Le contenu privé du Voyage intérieur, les membres, paiements et données CRM ne sont pas présents dans les captures publiques.

L’audit automatique examine tous les fichiers texte déployables, les variantes responsives, les styles, les médias de métadonnées et les enveloppes HTML locales. Des tests vérifient qu’il rejette les hotlinks d’images, polices, styles, vidéos, SVG et métadonnées, tout en autorisant les liens de navigation et les iframes Google Maps approuvées. L’inventaire des ressources observées dans les documents principaux de six pages représentatives (`runtime-assets.json`) ne contient que l’origine locale ; les ressources internes à l’iframe Google constituent l’exception explicite. Le cache de l’aperçu a aussi été nettoyé de l’ancien transport cartographique.

## Validation et revue

### Comparaison avec le site public actualisé

Les captures `home-current-*` et `voyage-current-*` conservent la nouvelle version publique de ces deux pages. Leurs contenus ordinateur et téléphone ont été synchronisés, sans réintroduire les cartes virtualisées manquantes. L’espacement du menu commun est passé de 44 à 20 px sur Wix ; cette différence de 24 px est corrigée sur les pages importées.

La comparaison des articles a détecté la suppression indue d’attributs de présentation Ricos : `data-breakout` applique notamment les marges intérieures du texte. Ils ont été restaurés dans les 11 articles, ordinateur et téléphone. La colonne de texte retrouve ses 740 px sur ordinateur, et les listes, images et retours à la ligne retrouvent leur disposition. Une règle de spacer de 14 px chargée tardivement par Wix est également conservée. Le contrôle de génération vérifie désormais la conservation de ces attributs ; la comparaison des polices et boîtes de texte est consignée dans `article-visual-parity.json`.

À 1280 px, les 494 blocs de texte comparés dans les 11 articles ont les mêmes positions, dimensions, polices et couleurs (tolérance de 1 px). Les composants des huit pages principales et du blog sont comparés dans `current-parity.json` ; la seule différence restante mesurée provient d’une animation sur Qui suis-je. Les contrôles à 390 px de l’accueil, du Voyage intérieur, du blog et d’un article ne montrent pas de débordement horizontal (`responsive-review.json`). Ces derniers valident la mise en page locale issue des captures mobiles ; ils ne constituent pas une comparaison avec un téléphone réel. Les paires de captures actualisées sont nommées `live-current-*-desktop.png` et `local-current-*-desktop.png`.

### Correction de la grille d’accueil

Le contrôle initial des routes, textes et dimensions extérieures avait manqué une régression visuelle : le conteneur anonyme entre chaque carte et son image n’avait pas de hauteur. Les hauteurs en pourcentage de l’image et de la superposition de titre se résolvaient donc à zéro, laissant la grille vide. La feuille `fidelity.css` donne maintenant une hauteur à ce conteneur. Les 11 images et titres sont vérifiés au sein des cartes à 980, 1280, 1440 et 390 px (`home-gallery-check.json`) et une capture de la grille visible est conservée dans `screenshots/local-home-blog-desktop.png`. La présence des articles ou de leurs liens seule ne suffit pas à valider cette section.

Vérifier la génération, les routes originales et les tags, les liens et ressources locales, les XML et l’absence de scripts du runtime Wix. Comparer les textes avec les sources et les positions des composants sur les pages principales. Les transformations animées et l’arrondi autorisé sont exclus d’une comparaison de géométrie.

Le contrôle final valide 70 pages HTML, dont les 69 routes migrées, leurs liens et ressources locales, les images responsives, les feuilles CSS et les XML. Un comptage des mots des contenus principaux ne détecte aucune perte sur les 69 routes (`text-check.json`). Sur les huit pages principales à 1440 px, les écarts de géométrie restants correspondent aux animations du site source (`geometry-check.json`). Le centrage du repeater Gestalt a aussi été vérifié à 1280 px. Le menu mobile, la galerie complète, la carte et le cycle brouillon → actif → brouillon ont été contrôlés.

Les captures de comparaison et mesures se trouvent dans `migration/reference/`. Ces vérifications ne constituent pas un audit complet de tous les états interactifs du site Wix. Les services de newsletter/réactions doivent être raccordés avant une bascule de production ; la carte reste dépendante de services tiers.

Aucune publication, modification du DNS ou soumission de données de visiteur n’a été effectuée. L’autorisation de mise en ligne reste nécessaire.
