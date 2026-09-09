# 4.1.3 — dessinateur natif et diagnostic avant dialogue

## Preuves reçues

Les captures 4.1.1/4.1.2 restent un échec du critère visuel de disparition de la card. Cette itération part du HEAD `0269065a672d5018f5393d9a1d9f1d04f1a75c1a`, sans modifier le renderer multi-player, les politiques MobileConfig ou le lifecycle pour provoquer un reload.

Deux relevés 4.1.2 ont ensuite été fournis. Seules leurs données structurelles utiles sont résumées ici.

| Preuve | Interprétation |
|---|---|
| Interne : WIDE, 657 × 870 dp, `active=true`, `card=false`, metadata FULL | Profil interne ; l’absence de mutations cover est attendue |
| Player interne : `TextureView`, page `com.instagram.ui.widget.roundedcornerlayout.RoundedCornerFrameLayout` | Identification concrète du wrapper natif du player |
| `ClipsViewerActionBar#clips_viewer_action_bar`, background `GradientDrawable`, BOTTOM_TOP, deux couleurs, `contrastEdges=1`, hauteur 158 pixels | Identification concrète du top scrim natif, distinct de la card |
| Externe : COMPACT, 444 × 701 dp ; window/visual 0,0–1248,1972 ; viewer 0,110–1248,1837 | Le viewport full-screen était correctement calculé ; l’interactif gardait les retraits natifs |
| Externe : `not-presentable`, `lifecycleKnown=false`, `focus=false`, players et candidats vidés | Le dialogue de diagnostic a fait arrêter la présentation tardivement installée ; ces zéros ne mesurent pas la détection pendant la lecture |
| Footer mask de hauteur zéro dans les deux relevés | Ce footer ne peut pas être attribué au bottom scrim visible sur ces instantanés |
| Relevés coupés dans les ancêtres, avant le sous-arbre du player | Le dessin précis des metadata et du bottom scrim reste non attribué |

Les arbres publics décompilés de la classe native montrent un chemin que 4.1.2 ne traitait pas : `RoundedCornerFrameLayout.dispatchDraw(Canvas)` appelle d’abord `super.dispatchDraw`, puis un helper qui dessine le masque des coins et un stroke via `Canvas.drawPath`. Ils ne sont pas des slots `background`/`foreground`. Ces artefacts ne sont **pas** assimilés à une vérification de l’APKM 439 fourni au téléphone :

- [Classe native, snapshot carter-0](https://github.com/carter-0/instagram-decompiled/blob/52284f22a48cecfd448ae9516cf49bcdfaa03db2/sources/com/instagram/ui/widget/roundedcornerlayout/RoundedCornerFrameLayout.java) et [helper](https://github.com/carter-0/instagram-decompiled/blob/52284f22a48cecfd448ae9516cf49bcdfaa03db2/sources/X/AnonymousClass3Ur.java).
- [Même contrat, autre snapshot](https://github.com/m0mosenpai/instadamn/blob/3d9fa70d8b36182d3fc7c3c5759db68f8a6d9402/our-instagram/base/sources/com/instagram/ui/widget/roundedcornerlayout/RoundedCornerFrameLayout.java).

**Cause certaine dans notre code :** ce chemin de dessin personnalisé est invisible à CardChrome 4.1.2. **Attribution du rectangle sur ce téléphone :** la classe observée et son rôle de wrapper constituent une justification concrète pour cibler ce chemin, mais les captures et les relevés tronqués ne prouvent pas que tous les traits proviennent exclusivement de lui. Les compteurs du nouveau hook permettront de vérifier son exécution. La ligne de progression et les éventuelles décorations Litho restent distinctes.

## Changement choisi

### Contour natif : intervenir au dessin, sans écraser les propriétés

`RoundedCardHook.kt` résout la classe et le helper dans l’APKM réellement patché. Il exige un dispatch de la forme `super.draw → charger le helper → dessiner avec le helper → return`, avec vérification des registres/références. Le helper doit être un dessinateur sans écriture d’état, avec seulement deux appels `Canvas.drawPath`. Une structure différente provoque une erreur explicite de patchage, avant toute substitution du dessinateur. Aucun nom de helper obfusqué n’est figé.

L’injection conserve toujours `super.dispatchDraw` et ses enfants. Elle conditionne seulement le dessin suivant des coins/stroke. L’extension accorde une autorisation temporaire aux wrappers du chemin des players **réellement transformés**, en cover avec nettoyage de card actif. Les cards voisines bénéficient du même état avant d’entrer. Les autres instances de cette classe restent natives.

Il n’y a aucune écriture du Paint, des rayons ou du helper Instagram. Une modification native reste donc disponible à la restauration. L’acquisition et la libération invalident la View pour reconstruire sa display list. Fold, fit, désactivation, detach, recyclage hors viewer et erreur libèrent l’autorisation. Le diagnostic compte les appels réellement exécutés et supprimés.

C’est la différence visible attendue avec 4.1.2 : **le dessinateur natif du trait devient effectivement conditionné**, alors qu’agrandir le viewport ou retirer des drawables ne pouvait jamais l’atteindre.

### Gradients et repères

La distinction visual/interactive de 4.1.2 est conservée. Les gradients sont translatés vers leur bord, élargis horizontalement et conservent leur hauteur de fondu ; aucune mise à l’échelle verticale n’est appliquée. Pour un gradient à deux bords, chaque moitié native est conservée à son bord avec un espace transparent entre les deux si le viewport est plus haut. La découpe entre pages reste alignée sur le player.

Le background du `ClipsViewerActionBar` explicitement observé est reconnu indépendamment de la présence de TextViews. Ses enfants et dimensions interactives ne sont pas agrandis. Le diagnostic garde aussi ce candidat sur l’interne, tout en restaurant le dessin natif. La 4.1.2 le retirait de son suivi lorsque le clip boundary devenait le viewer, alors que cette action bar est une sœur du viewer.

Un remplacement natif du drawable est réappliqué et compté. Les modifications de couleurs/alpha/état du drawable original sont suivies. Les wrappers rapportent aussi leurs appels de dessin et le clip Canvas observé, au lieu de fournir uniquement une géométrie attendue. Cela ne prouve pas, à lui seul, le résultat du compositeur Samsung.

### Metadata et diagnostic

L’identité sans Follow exige maintenant un label d’auteur explicitement identifié. Une image profile générique et un texte cliquable ne suffisent plus. Les branches nommées social context/proof, facepile, friending ou suggestions ne deviennent pas des identités compactées. L’interface incertaine reste native ; aucun contenu utilisateur n’est copié pour recréer une interface parallèle.

Le diagnostic est figé à l’ouverture des réglages, **avant** la perte de focus. Les chemins des players sont placés avant les ancêtres ; les GONE et vues de taille zéro ne saturent plus le rapport. Les objets ont des identifiants d’instance et l’export texte utilise le sélecteur Android existant de Piko. Pour les `ComponentHost`, seule l’[API publique des drawables montés](https://fblitho.com/javadoc/com/facebook/litho/ComponentHost.html) est interrogée lorsque disponible : classes/bounds/alpha, jamais les textes, comptes, descriptions ou médias. Les limites et la fin du rapport sont explicites.

## Fichiers principaux

- `RoundedCardHook.kt`, `AdaptiveFoldReelsPatch.kt` : vérification/injection dans le dessinateur natif.
- `FoldReelsNativeDecoration.java`, `FoldReelsCardChrome.java`, `FoldReelsRenderer.java` : autorisations temporaires du dessin, dépendantes du player transformé.
- `FoldReelsScrim.java`, `FoldReelsHeader.java` : gradient, suivi des réécritures et reconnaissance de l’action bar.
- `FoldReelsMetadata.java` : refus des identités ambiguës.
- `FoldReels.java`, `FoldReelsDiagnostics.java`, `BackupPrefActivity.java` : capture avant dialogue et export.

## Validation et limites

Gates requis : 113 tests Android, 5 tests de garde bytecode, 305 assertions policy/geometry, 13 mappings et XML FR/EN, 14 tests distribution, compilation et chargement du MPP par Morphe, vérification ZIP/SHA et téléchargements publics. La publication est exécutée par le job qui dépend de l’ensemble des gates.

Nouveaux tests : suppression du dessin personnalisé sans supprimer les enfants ; original Paint modifié pendant le crop puis conservé ; active/voisins et fold ; absence d’effet sur autre instance/player non transformé ; detach/recyclage ; compteurs d’exécution ; gradient natif BOTTOM_TOP et falloff haut/bas ; candidat partagé inactif sur interne ; rebinding/couleurs modifiées ; diagnostic avant perte de focus et sans spam ; metadata social context et avatar ambigu. Les anciens tests qui exigeaient un étirement vertical ont été adaptés au nouveau contrat de distance de fondu constante.

**À confirmer sur le Fold :** disparition de tous les traits (dont l’éventuel trait indépendant de progression), rendu du gradient derrière le bandeau, identification du bottom scrim et des branches Litho restantes, continuité visuelle réelle pendant les swipes et les changements d’écran. Ni la fixture portant le nom d’une classe Instagram, ni Skia/Robolectric, ni le chargement du MPP ne sont un test pixel Samsung ou un patchage exécuté sur l’APKM 439. Aucun APK utilisateur n’a été fourni dans cette itération.
