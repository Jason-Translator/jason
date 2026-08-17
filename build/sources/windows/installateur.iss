; Installateur Windows de Jason (Inno Setup).
;
; Produit JasonInstallateur.exe : l'utilisateur double-clique, suit trois
; écrans, et trouve Jason dans son menu Démarrer. Aucune notion technique
; requise, aucun droit administrateur (installation dans le dossier de
; l'utilisateur).
;
; Se compile avec ISCC (Inno Setup), sur une machine Windows dédiée ou une
; VM — pas de chaîne d'intégration continue pour l'instant.

#define Nom "Jason"
#define Version "0.1.0"
#define Executable "jason.exe"

[Setup]
AppName={#Nom}
AppVersion={#Version}
AppVerName={#Nom} {#Version}
DefaultDirName={autopf}\{#Nom}
DefaultGroupName={#Nom}
; Chemins relatifs à ce fichier, qui vit dans build/sources/windows/ — d'où
; les "..\..\.." pour remonter à la racine du dépôt jusqu'à apps/.
OutputDir=..\..\..\apps\windows
OutputBaseFilename=JasonInstallateur
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
; Installation pour l'utilisateur courant : évite la demande de mot de passe
; administrateur, qui bloque beaucoup de monde.
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#Executable}
DisableProgramGroupPage=yes
; L'application pèse plus d'un giga-octet une fois décompressée.
DiskSpanning=no

[Languages]
Name: "francais"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "raccourcibureau"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis :"

[Files]
Source: "..\..\dist\jason\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#Nom}"; Filename: "{app}\{#Executable}"
Name: "{autodesktop}\{#Nom}"; Filename: "{app}\{#Executable}"; Tasks: raccourcibureau

[Run]
Filename: "{app}\{#Executable}"; Description: "Lancer {#Nom}"; Flags: nowait postinstall skipifsilent
