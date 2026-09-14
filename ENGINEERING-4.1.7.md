> État final du 14 septembre : l'APKM original est disponible et les 60 patches ont réussi avec Morphe Patcher 1.14.0-dev.1. La seconde régression du RC et sa correction sont détaillées dans `RC-REPAIR-4.1.7.md`. Les preuves actuelles sont dans `APK-VALIDATION-4.1.7.json`. Le texte initial ci-dessous conserve l'audit réalisé avant réception de l'APK ; ses réserves sur la disponibilité de celui-ci ne sont plus actuelles. Le test ART/Samsung reste à faire.

# Audit et correctif candidat 4.1.7

Base : `senor-roboto/PatchInsta@80d7b37da2b5b35f3a83c65563850f580e33ba34` (4.1.6).
Piko reste épinglé à `50744aa07bb41c4e1f942a06614ef4e6f2e3610c`.
Cible inchangée : Instagram 439.0.0.37.89, arm64, versionCode 384510827.

## Ce qui est établi, et ce qui ne l'est pas

La reconstruction exacte du HEAD applique le patch principal puis trois hotfixes.
La 4.1.3 ne reconnaissait qu'un dispatch à quatre instructions appelant un helper à
deux `Canvas.drawPath`. La 4.1.4 a toléré `/range` et les NOP. La 4.1.5 a ignoré le
code après le premier retour, sans analyser son CFG. La 4.1.6 a changé de concept :
elle tente de sauter depuis l'entrée vers un `invoke-super; return-void` existant.
Les deux fonctions de l'ancien concept et leurs tests restaient pourtant présentes.

La condition 4.1.6 impose `ref.definingClass == superclass`. C'est plus strict que
la sémantique de `invoke-super` : un DEX peut référencer un ancêtre de la classe
immédiate. Elle ne valide pas non plus la provenance des arguments, la joignabilité
ou les régions protégées du fallback. Son garde est inséré sans isoler explicitement
les `try_item` natifs. Ces défauts sont établis dans le code, indépendamment des noms
obfusqués.

**La cause exacte du `candidates=0` sur l'APK de l'utilisateur n'est pas encore
prouvée.** Sa trace fournit les opcodes, mais pas le propriétaire de l'appel, ses
registres ou les adresses de handlers. Aucun APK/DEX n'est joint ou présent dans
l'espace de travail. Le cas de test reproduit la forme à 27 instructions signalée,
avec références/champs synthétiques explicitement identifiés. Ce n'est pas un dump
Instagram et ce n'est pas une preuve que les 60 patches passent sur l'APK réel.

## Identification et injection

`identifyRoundedCard` exige un seul override d'instance `dispatchDraw(Canvas)V` dans
la classe ciblée. Il résout ses ancêtres dans les classes de l'APK jusqu'aux classes
publiques Android `FrameLayout`, `ViewGroup`, `View`. Une classe obfusquée manquante,
un cycle ou une hiérarchie incompatible sont rejetés.

`DrawFlow` travaille en unités de code DEX. Il vérifie les destinations des branches,
les limites de try/catch et les entrées `move-exception`. Un candidat doit être
joignable depuis l'entrée native, appeler `dispatchDraw(Canvas)V` sur un ancêtre
vérifié avec `this` et le Canvas d'origine, et aboutir au retour sans nettoyage ni
travail intermédiaire. Les NOP et goto de retour sont admis. Aucun candidat n'est
choisi arbitrairement : zéro ou plusieurs candidats produisent un rapport ciblé.
Une méthode à switch/payload est rejetée explicitement, car cette analyse de CFG ne
prétend pas prendre en charge ces variantes non observées.

`installRoundedCardEntryBypass` construit une nouvelle implémentation sans modifier
l'original. Le garde de 10 unités de code appelle le lease runtime. Faux : exécuter
l'instruction native zéro. Vrai : réutiliser la référence exacte du parent validée,
dessiner avec les paramètres originaux puis retourner. Il n'y a plus de saut vers
une branche interne obfusquée. Les indices des registres et les offsets relatifs
natifs sont conservés. Les adresses absolues des try, handlers et informations de
debug sont décalées ensemble de 10. Le garde est hors de toutes les régions
protégées. `v0` est un local non paramètre libre à l'entrée ; aucun registre de
paramètre n'est réaffecté. La classe reçoit la nouvelle méthode seulement après
réussite de la construction.

Les trois hotfixes séparés, `roundedCardHelper` et `installRoundedCardHook` sont
supprimés. La CI et le kit appliquent/distribuent un unique patch source cumulatif.

## Revue visuelle et lifecycle

Le renderer, ses surfaces active ±1, ses transformations, le routage tactile,
les politiques MobileConfig et les limites visuelles/interactives restent inchangés.
Le lease du bypass n'est actif que pour une card sur le chemin d'un player réellement
recadré en cover avec nettoyage des cards activé. En interne, en mode entier,
sur une vue indépendante, après detach/recycle ou restauration, le dessin natif
s'exécute. Aucun `recreate`, reload ou listener natif n'est ajouté/remplacé.

La différence attendue sur cover vient de la suppression du dispatch arrondi natif
uniquement sous lease, pas d'un agrandissement supplémentaire des bounds. Sa preuve
sur appareil sera `native-rounded-dispatch enabled=true`, avec `drawCalls` et
`suppressed` qui augmentent. Un compteur de candidats seul ne suffit pas.

La 4.1.2 calculait déjà, dans le diagnostic cover fourni, la fenêtre réelle
`0,0–1248,1972`. Le manque de changement visuel ne s'expliquait donc pas par ce
rectangle de calcul. Les captures et l'arbre identifiaient la page
`RoundedCornerFrameLayout`, mais pas l'instruction qui dessinait chaque trait.
Le gradient supérieur est identifié : background `GradientDrawable` de
`ClipsViewerActionBar#clips_viewer_action_bar`, hauteur native 158 px dans ce rapport.
Le footer à hauteur zéro n'est pas une preuve de bottom scrim. Sans capture runtime
complète après un patch applicable, attribuer tous les traits ou fonds à des
Drawables précis serait une supposition.

Les scrims existants conservent leur falloff vertical et leur couche de dessin ;
le metadata reste dans les limites tactiles natives et ne copie pas les textes
Litho. Les tests existants couvrent les pages adjacentes, le commentaire, la
restauration et les scrims synthétiques. Ils ne certifient pas les pixels Samsung.
Le numéro affiché par le diagnostic, encore figé à 4.1.3 en 4.1.6, devient 4.1.7.

## Validations et outil APK

19 tests Kotlin : forme rapportée, référence à ancêtre, instructions supplémentaires,
registres déplacés, `/range`, ambiguïté, absence, parent manquant, méthode statique,
Canvas incorrect/réaffecté, absence de local, nettoyage après super, fallback
injoignable/protégé, position du garde, debug, seconde injection et cycle DEX
écriture/relecture avec vérification des références/branches/handlers.

113 scénarios Android existants, 305 vérifications JVM de politique/géométrie,
13 mappings/XML et 14 tests de distribution restent des gates. Le vrai `.mpp` est
chargé par Morphe ; les quatre méthodes publiques statiques appelées par les hooks
sont aussi vérifiées dans le DEX `.mpe` compilé.

L'audit suivant utilise l'APK local fourni, sans téléchargement ni données de compte :

```sh
./gradlew :patches:auditFoldApk \
  -PfoldApk=/chemin/absolu/base.apk \
  -PfoldAuditOutput=/chemin/absolu/nouveau-dossier-audit
```

Il écrit `before.txt`, `audit.txt` et un DEX d'inspection de la classe modifiée,
puis relit ce DEX. Ce DEX isolé n'est pas un APK installable. Un APKM doit être extrait
pour fournir son `base.apk`. La session complète Morphe avec les 60 patches, la
vérification ART et l'essai Fold restent des validations distinctes.

La compilation locale a été tentée : téléchargement Gradle bloqué (`Network is
unreachable`). GitHub Actions réalise la compilation réelle. Les résultats et le
commit exact seront consignés dans `VERIFICATION-4.1.7.json` après les gates.
La source Morphe stable ne doit pas annoncer ce candidat comme réparation prouvée
sur 439 tant que l'APK réel n'a pas été inspecté et patché.
