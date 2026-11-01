# Dépôt et hébergement

Le dépôt source est https://github.com/9h41/psytours. Le propriétaire a autorisé sa visibilité **publique temporaire** pour tester GitHub Pages ; ne pas le rendre privé avant d'avoir décidé du prochain hébergement, car cela interromprait Pages sur le forfait Free.

- `main` : version stable, destinée plus tard au site de production `psy-tours.fr`.
- `preview` : travail en cours, destiné à `preview.psy-tours.fr`.
- Les modifications de `preview` seront promues vers `main` après validation.
- Le workflow `check.yml` contrôle les deux branches et leurs pull requests. Il ne déploie rien.
- Le workflow `preview.yml` déploie uniquement `preview` vers https://9h41.github.io/psytours/ ; l'environnement `github-pages` accepte cette branche. `main` ne déploie pas en production.

## État vérifié le 1er novembre 2026

Le domaine est enregistré chez **Gandi** (WHOIS AFNIC). La zone DNS est déléguée à **Wix** : `ns2.wixdns.net` et `ns3.wixdns.net`. Les adresses IPv4 du domaine pointent vers Wix. Le sous-domaine `preview` n'a pas de CNAME observé. Aucun DNS ni site de production n'a été modifié.

L'organisation GitHub `9h41` utilise le forfait **Free**. L'API Pages a d'abord refusé l'activation pour le dépôt privé. Le propriétaire a ensuite autorisé le passage temporaire en public pour tester. Pages est maintenant activé en mode GitHub Actions, **sans domaine personnalisé ni CNAME**. Un forfait GitHub Team ou une autre solution d'hébergement restera nécessaire pour revenir à des sources privées avec un site hébergé.

GitHub Pages ne fournit qu'un site par dépôt. Les deux branches d'un même dépôt ne permettent donc pas deux sites Pages indépendants avec deux domaines. Pour rester sur GitHub Pages, il faudra prévoir un deuxième dépôt cible pour la prévisualisation, avec un mécanisme de déploiement autorisé entre dépôts. Il n'est pas créé à ce stade.

`python3 scripts/prepare_pages.py` prépare un artefact séparé `.pages/` à partir du build vérifié dans `dist/`. Il adapte les liens, CSS, images responsives et enveloppes embarquées au préfixe `/psytours/`, utilise l'origine GitHub pour les médias de métadonnées, ajoute `noindex, nofollow` et un `robots.txt` restrictif, et exclut tout CNAME. L'audit vérifie les assets et la navigation après adaptation. Les URL canoniques éditoriales restent celles du site de production. Le script ne modifie ni les sources ni `dist/` ni l'aperçu local `.preview/`.

GitHub Pages n'interprète pas `_redirects` : `.pages/services-3/index.html` fournit une redirection statique de secours vers la prise de rendez-vous. Ce n'est pas une redirection HTTP 301.

Pour ce test Pages, ne publier que `.pages/`. Pour un hébergement à la racine d'un domaine, le build habituel reste `dist/`. Ne jamais déployer le dépôt complet ou les archives de migration. La bascule du domaine de production reste une opération distincte, soumise à autorisation explicite.

Références : [disponibilité de GitHub Pages selon le forfait](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site), [limite d'un site par dépôt](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages), [domaines personnalisés](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site).
