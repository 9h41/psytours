# Restauration de la fidélité Wix — 1er novembre 2026

Ce document remplace les choix de présentation du premier essai décrits dans `migration.md`. Le propriétaire a demandé une copie visuelle exacte. Le dépôt Git a été initialisé et l’intégralité des sources du premier essai sauvegardée dans `bb7b400` **avant** les changements ci-dessous. Aucun push n’a été effectué.

## Référence

La nouvelle référence est le site Wix public, avec des captures fraîches dans `migration/reference/raw/` et `migration/reference/mobile/`. Les contenus de pages après rendu sont également conservés. Le site utilise des mises en page différentes sur ordinateur et téléphone ; les deux sont reprises.

Les 32 routes des sitemaps et 37 archives de tags découvertes dans les articles sont reproduites : 69 routes publiques, plus une page 404. Les textes, prix, mentions de Paris, titres, champs de formulaire, images, logos, crédits et métadonnées sont repris de la source. Aucune correction éditoriale n’est appliquée sans demande.

## Modification autorisée

Seul le bord supérieur de l’image principale est arrondi. Les animations sont désactivées. Le visuel complet de Wix est utilisé avec son cadrage original ; le portrait recadré du premier essai n’est plus utilisé.

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

La copie statique ne peut pas recréer à elle seule les services Wix CRM et les données privées. Le formulaire de newsletter conserve son apparence, mais une soumission locale affiche un message d’indisponibilité au lieu d’une fausse confirmation. Les vues, commentaires et likes sont des valeurs de la capture ; aucune persistance n’est inventée.

Les réservations externes conservent leurs destinations. Le bouton Liberlo est localisé ; son logo est déjà manquant sur le site source (HTTP 404) et n’a pas été remplacé par une autre illustration. Le contrôle de contact conserve sa présentation et permet d’appeler le numéro public.

Les cartes conservent volontairement le moteur public isolé de Wix, hébergé sur `static.parastorage.com`, et Google Maps. Des enveloppes locales lui transmettent les réglages capturés : couleurs personnalisées, marqueur, adresse, zoom et contrôles. Le rendu a été vérifié dans l’aperçu local. Cette dépendance externe reste nécessaire pour conserver l’apparence exacte du widget ; le runtime du site Wix complet est retiré. Le contenu privé du Voyage intérieur, les membres, paiements et données CRM ne sont pas présents dans les captures publiques.

## Validation et revue

Vérifier la génération, les routes originales et les tags, les liens et ressources locales, les XML et l’absence de scripts du runtime Wix. Comparer les textes avec les sources et les positions des composants sur les pages principales. Les transformations animées et l’arrondi autorisé sont exclus d’une comparaison de géométrie.

Le contrôle final valide 70 pages HTML, dont les 69 routes migrées, leurs liens et ressources locales, les images responsives, les feuilles CSS et les XML. Un comptage des mots des contenus principaux ne détecte aucune perte sur les 69 routes (`text-check.json`). Sur les huit pages principales à 1440 px, les écarts de géométrie restants correspondent aux animations du site source (`geometry-check.json`). Le centrage du repeater Gestalt a aussi été vérifié à 1280 px. Le menu mobile, la galerie complète, la carte et le cycle brouillon → actif → brouillon ont été contrôlés.

Les captures de comparaison et mesures se trouvent dans `migration/reference/`. Ces vérifications ne constituent pas un audit complet de tous les états interactifs du site Wix. Les services de newsletter/réactions doivent être raccordés avant une bascule de production ; la carte reste dépendante de services tiers.

Aucune publication, modification du DNS ou soumission de données de visiteur n’a été effectuée. L’autorisation de mise en ligne reste nécessaire.
