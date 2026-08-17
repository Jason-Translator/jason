## Jason

Un traducteur qui fonctionne sur votre ordinateur : pas de compte, pas de
publicité, et vos textes ne sont jamais envoyés sur Internet. La traduction
elle-même se fait entièrement en local, sur votre machine.

Internet ne sert qu'à une chose : télécharger les langues que vous ajoutez.
Chacune se télécharge une fois, puis fonctionne hors connexion.

Site du projet : jason-translator.github.io/jason

### Pourquoi « Jason » ?

Sous le capot, la traduction est faite par un moteur libre nommé Argos
Translate. Dans la mythologie grecque, Argos est le charpentier qui
construisit l'*Argo*, le navire avec lequel Jason et les Argonautes
partirent chercher la Toison d'or. Le clin d'œil était trop beau : Argos
bâtit le navire, Jason le mène à bon port.

### Ce que Jason traduit mal

Autant le dire franchement : Jason traduit moins bien que les grands
services en ligne. C'est le prix du hors ligne — chaque langue doit tenir
en ~170 Mo sur votre machine, là où les services en ligne font tourner des
modèles géants dans des centres de données.

Les traductions passent par l'anglais (français → anglais → japonais), et
chaque étape ajoute ses erreurs. Les langues proches du français (espagnol,
italien...) s'en sortent bien ; l'arabe, le russe, le japonais ou le chinois
beaucoup moins — attendez-vous à saisir le sens général, pas à obtenir une
phrase parfaite.

Jason sert à **comprendre** un texte. Pour un document important que
quelqu'un d'autre lira, faites-le relire ou utilisez un autre outil.

### Qui a construit Jason

**François Guerin** — l'architecte : l'idée, les choix techniques, le dessin
de l'interface, et les essais jusqu'à ce que tout tienne debout.

**Claude** (Anthropic) — le maçon : l'écriture du code, d'après les plans de
l'architecte.

### Remerciements

Jason ne réinvente rien. Il repose sur des projets libres et sur leurs
contributeurs, souvent anonymes, sans qui rien de tout cela ne serait
possible.

Il traduit grâce à **Argos Translate** et **CTranslate2**, reconnaît les
langues avec **Lingua**, découpe les phrases avec **Stanza**, et affiche
tout cela avec **Qt** et **PySide6**, en **Python**.

Pour arriver jusqu'à vous, il est empaqueté avec **PyInstaller**, puis
distribué en **AppImage** sous Linux et avec **Inno Setup** sous Windows.
