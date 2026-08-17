# Brief — site vitrine une page pour Jason

Document d'instructions destiné à Claude Design. Il se suffit à lui-même :
aucune connaissance préalable du projet n'est nécessaire.

**Livrable attendu : un `index.html` autonome + un dossier `images/`**, prêts
à déposer dans un dépôt GitHub Pages.

---

## 1. Ce qu'est Jason

Jason est un **traducteur de bureau qui fonctionne hors ligne**. On écrit un
texte dans une langue, on lit sa traduction dans une autre. La traduction est
calculée sur la machine de l'utilisateur : aucun texte n'est envoyé à un
serveur.

Les faits, à respecter scrupuleusement :

- **Plateformes : Windows et Linux uniquement.** Pas de macOS. Ne pas le
  laisser entendre, ne pas afficher de logo Apple.
- **Internet sert à une seule chose** : télécharger les langues choisies. Une
  fois installées, elles fonctionnent sans connexion. Ce n'est pas un détail à
  cacher — c'est une étape réelle de la prise en main.
- **50 langues** au catalogue. On les ajoute et on les supprime depuis les
  Paramètres.
- La langue du texte saisi est **reconnue automatiquement**. Si elle est
  ambiguë, Jason le dit au lieu de deviner.
- **Gratuit, sans compte, sans publicité.**
- Auteur : **François Guerin**. Projet réalisé pour le concours Innovez du
  magazine *Science & Vie Junior*.

Le site est en **français uniquement**.

---

## 2. Les deux boutons de téléchargement — la partie à ne pas rater

L'exigence : **les boutons doivent toujours servir la dernière version
publiée, sans jamais rééditer le site.** GitHub fournit pour cela des URL
permanentes (documentées sur
`docs.github.com/en/repositories/releasing-projects-on-github/linking-to-releases`) :

```
https://github.com/UTILISATEUR/DEPOT/releases/latest/download/JasonInstallateur.exe
https://github.com/UTILISATEUR/DEPOT/releases/latest/download/Jason-x86_64.AppImage
```

`UTILISATEUR` et `DEPOT` sont à compléter par le propriétaire du site ; le
dépôt n'existe pas encore au moment de la rédaction de ce brief.

### Règles impératives

1. **Le nom des fichiers ne doit jamais changer d'une release à l'autre** —
   aucun numéro de version dans le nom. C'est ce qui fait tenir le mécanisme.
   Les deux livrables actuels respectent déjà cette règle.
2. **Les deux URL vivent dans un seul bloc de configuration en haut du
   `index.html`**, précédé d'un commentaire expliquant à quoi il sert. Changer
   de dépôt, ou de forge, doit rester une modification de deux lignes.
3. **Les boutons doivent fonctionner sans JavaScript** : de simples `<a href>`.
4. **Aucun appel à l'API GitHub** pour afficher dynamiquement le numéro de
   version. Deux raisons : la limite de débit non authentifiée, et surtout le
   fait que cela ferait contacter un tiers par le navigateur du visiteur — ce
   qui contredirait frontalement l'argument du logiciel.
5. Sous chaque bouton, une ligne discrète :
   - Windows : « installateur, environ 300 Mo — aucun droit administrateur
     nécessaire » ;
   - Linux : « AppImage, environ 520 Mo — à rendre exécutable avant le premier
     lancement (clic droit → Propriétés → Autoriser l'exécution, ou
     `chmod +x`) ».
6. Un lien secondaire discret vers `https://github.com/UTILISATEUR/DEPOT/releases`,
   libellé « toutes les versions ».

### Annexe : si le projet change un jour de forge

- **GitLab** (documenté) :
  `https://gitlab.com/UTILISATEUR/DEPOT/-/releases/permalink/latest/downloads/CHEMIN`
  — impose de déclarer chaque fichier comme *asset link* à chaque release.
- **Gitea / Forgejo / Codeberg** : la même forme que GitHub semble fonctionner
  en pratique, mais **elle n'apparaît pas dans la documentation officielle**.
  À vérifier sur l'instance retenue avant de s'y fier.

C'est précisément pour cela que les URL doivent être regroupées en un seul
endroit du fichier.

---

## 3. Contraintes techniques

- **Une seule page**, un seul `index.html`, CSS écrit en ligne dans le fichier.
- **Zéro requête vers un tiers.** Pas d'analytics, pas de police depuis un CDN,
  pas d'image distante, pas de bibliothèque externe. Tout est embarqué ou
  servi depuis le dépôt. *C'est la contrainte la plus importante de ce brief :
  le site d'un logiciel qui promet que rien ne sort de votre machine ne peut
  pas pister ses visiteurs.* Utiliser les polices système
  (`system-ui`, `-apple-system`, `Segoe UI`, `Roboto`, sans-serif).
- **Thème clair et sombre** via `prefers-color-scheme`, avec la palette réelle
  de l'application :

  | Rôle | Clair | Sombre |
  |---|---|---|
  | Fond | `#f5f6f8` | `#14161b` |
  | Surface (cartes) | `#ffffff` | `#1d2028` |
  | Texte | `#1f2430` | `#e7e9ee` |
  | Texte discret | `#6b7382` | `#98a0af` |
  | Bordure | `#e2e5ea` | `#2b2f39` |
  | Accent (boutons, liens) | `#2f6fed` | `#4c8dff` |
  | Accent survol | `#245ad4` | `#5f9bff` |

- **Responsive** : lisible à partir de 360 px de large, aucune image ni aucun
  bloc ne doit provoquer de défilement horizontal.
- `<title>`, `<meta name="description">` et balises Open Graph
  (`og:title`, `og:description`, `og:image`) pour que le lien s'affiche
  correctement quand il est partagé.
- HTML sémantique, contraste suffisant, `alt` sur toutes les images.

---

## 4. Plan de la page, avec le texte à utiliser

Le texte ci-dessous est à reprendre tel quel. Il a été écrit et relu pour ce
projet ; il ne s'agit pas d'un canevas à reformuler.

### En-tête

> # Jason
>
> ## Traduisez sans connexion, et sans que rien ne quitte votre ordinateur.
>
> Jason est un traducteur qui fonctionne entièrement sur votre machine. Aucun
> compte, aucune publicité, aucun serveur : le texte que vous écrivez n'est
> envoyé nulle part.

Puis les deux boutons, côte à côte (empilés sur mobile) : **Télécharger pour
Windows** et **Télécharger pour Linux**.

### Trois arguments

> **Il fonctionne hors ligne.**
> Dans un train, un avion, une zone sans réseau, ou un pays sans forfait de
> données. Une fois vos langues installées, Internet n'est plus nécessaire.
>
> **Vos textes restent chez vous.**
> Les traducteurs en ligne envoient chaque phrase saisie à un serveur
> distant. Un texte personnel, médical ou professionnel y passe comme le
> reste. Avec Jason, la traduction est calculée sur votre ordinateur.
>
> **Rien à créer, rien à accepter.**
> Pas de compte, pas d'abonnement, pas de publicité, pas de bandeau de
> consentement.

### Capture d'écran

La capture principale de la fenêtre de traduction, en grand, avec une légende
sobre : « Une traduction réelle de l'anglais vers le français. La langue du
texte saisi a été reconnue automatiquement. »

### Comment ça marche

Trois étapes numérotées :

> **1. Installez Jason.** Un installateur sous Windows, un fichier unique à
> double-cliquer sous Linux. Rien d'autre à installer.
>
> **2. Choisissez vos langues.** Au premier lancement, Jason ouvre la liste
> des langues : téléchargez celles dont vous avez besoin, parmi cinquante.
> C'est le seul moment où une connexion est nécessaire.
>
> **3. Écrivez à gauche, lisez à droite.** La langue de votre texte est
> reconnue toute seule. Vous pouvez ajouter ou supprimer des langues à tout
> moment depuis les Paramètres.

### Crédits

Reprendre la structure et le ton du fichier `a-propos.md` de l'application,
qui dit exactement ceci — la cohérence entre le site et le logiciel compte :

> ### Qui a construit Jason
>
> **François Guerin** — l'architecte : l'idée, les choix techniques, le dessin
> de l'interface, et les essais jusqu'à ce que tout tienne debout.
>
> **Claude** (Anthropic) — le maçon : l'écriture du code, d'après les plans de
> l'architecte.
>
> ### Remerciements
>
> Jason ne réinvente rien. Il repose sur des projets libres et sur leurs
> contributeurs, souvent anonymes, sans qui rien de tout cela ne serait
> possible.
>
> Il traduit grâce à **Argos Translate** et **CTranslate2**, reconnaît les
> langues avec **Lingua**, découpe les phrases avec **Stanza**, et affiche
> tout cela avec **Qt** et **PySide6**, en **Python**.
>
> Pour arriver jusqu'à vous, il est empaqueté avec **PyInstaller**, puis
> distribué en **AppImage** sous Linux et avec **Inno Setup** sous Windows.

### Pied de page

Lien vers le dépôt, et la mention « Projet présenté au concours Innovez de
Science & Vie Junior ».

---

## 5. Ce qu'il ne faut pas écrire

Cette section prime sur toute considération esthétique.

- **Pas de superlatif marketing** : ni « révolutionnaire », ni « la meilleure
  solution », ni « enfin ».
- **Aucun chiffre inventé** : pas de nombre d'utilisateurs, de
  téléchargements, d'étoiles, de pourcentage de précision. Les seuls chiffres
  autorisés sont ceux de ce brief (50 langues, tailles des fichiers).
- **Ne pas prétendre que Jason traduit mieux** que Google Traduction ou DeepL.
  C'est faux. Son avantage est ailleurs : la confidentialité et le hors ligne.
  Une comparaison honnête est possible, une comparaison flatteuse ne l'est pas.
- **Ne rien masquer** : ni le téléchargement initial des langues, ni l'absence
  de version macOS, ni la taille des fichiers.
- **Pas de faux badges, pas de fausses citations d'utilisateurs, pas de logos
  d'entreprises** qui laisseraient croire à un partenariat.

---

## 6. Ressources fournies

À recopier dans le dossier `images/` du site.

**Captures d'écran** (dans `Dossier Jason concours innovez SVJ/`) :

| Fichier | Contenu |
|---|---|
| `01-fenetre-principale-traduction-sombre.png` | Fenêtre principale, thème sombre, traduction réelle anglais → français. **La capture principale.** |
| `02-fenetre-principale-theme-clair.png` | La même en thème clair. |
| `03-parametres-langues.png` | Onglet Langues : installées et disponibles. |
| `04-parametres-apparence.png` | Onglet Apparence. |
| `05-parametres-a-propos.png` | Onglet À propos. |

Les captures 01 et 02 permettent, si le rendu s'y prête, de montrer la
version correspondant au thème du visiteur.

**Icône** (dans `build/sources/jason/ui/resources/`) : `jason.svg` (vectorielle,
à préférer) et `jason-256.png`.

**Texte des crédits** : `build/sources/jason/ui/resources/a-propos.md`.

---

## 7. Vérification du résultat

À faire avant de considérer le site terminé :

1. Ouvrir `index.html` en local, **sans connexion** : la page s'affiche
   entièrement.
2. Onglet « Réseau » des outils de développement : **aucune requête vers un
   domaine tiers**.
3. Basculer le thème du système : les deux variantes sont lisibles, aucun
   texte à faible contraste.
4. Réduire la fenêtre à 360 px de large : aucun débordement horizontal.
5. Désactiver JavaScript : les deux boutons fonctionnent toujours.
6. Une fois la première release publiée, cliquer les deux boutons et vérifier
   que le bon fichier arrive. Publier ensuite une seconde release et
   recliquer **sans avoir touché au site** : les nouveaux fichiers doivent
   arriver. C'est le test qui valide tout le mécanisme.
