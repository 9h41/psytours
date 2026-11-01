# Dépôt et hébergement

Le dépôt source privé est https://github.com/9h41/psytours.

- `main` : version stable, destinée plus tard au site de production `psy-tours.fr`.
- `preview` : travail en cours, destiné à `preview.psy-tours.fr`.
- Les modifications de `preview` seront promues vers `main` après validation.
- Le workflow `check.yml` contrôle les deux branches et leurs pull requests. Il ne déploie rien.

## État vérifié le 1er novembre 2026

Le domaine est enregistré chez **Gandi** (WHOIS AFNIC). La zone DNS est déléguée à **Wix** : `ns2.wixdns.net` et `ns3.wixdns.net`. Les adresses IPv4 du domaine pointent vers Wix. Le sous-domaine `preview` n'a pas de CNAME observé. Aucun DNS ni site de production n'a été modifié.

L'organisation GitHub `9h41` utilise le forfait **Free**. L'API Pages a refusé l'activation pour ce dépôt privé : « Your current plan does not support GitHub Pages for this repository. » Un forfait GitHub Team ou une autre solution d'hébergement sera nécessaire pour garder le dépôt privé.

GitHub Pages ne fournit qu'un site par dépôt. Les deux branches d'un même dépôt ne permettent donc pas deux sites Pages indépendants avec deux domaines. Pour rester sur GitHub Pages, il faudra prévoir un deuxième dépôt cible pour la prévisualisation, avec un mécanisme de déploiement autorisé entre dépôts. Il n'est pas créé à ce stade.

La future mise en place devra aussi tenir compte des chemins d'assets absolus (`/assets/...`) : ils fonctionnent à la racine d'un domaine personnalisé, mais pas tels quels sous le chemin par défaut d'un site projet GitHub (`/psytours/`). GitHub Pages n'interprète pas le fichier `_redirects` : l'alias `/services-3` devra recevoir une page de redirection statique de secours, ou une redirection HTTP via un service compatible.

Avant tout déploiement, adapter l'origine des médias de métadonnées au domaine de chaque environnement et empêcher l'indexation du site de prévisualisation. Ne publier que `dist/`. La bascule du domaine de production reste une opération distincte, soumise à autorisation explicite.

Références : [disponibilité de GitHub Pages selon le forfait](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site), [limite d'un site par dépôt](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages), [domaines personnalisés](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site).
