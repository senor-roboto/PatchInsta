# Piko — Réels adaptés au Fold, v4 expérimentale

Importer **`piko-fold-reels-v4.mpp`** dans Morphe. Ce bundle contient Piko complet, avec notre modification non officielle. Cible inchangée : **Instagram 439.0.0.37.89, arm64-v8a, versionCode 384510827**, à partir de son **APKM original**. Base : Piko 3.9.0 au commit `50744aa07bb41c4e1f942a06614ef4e6f2e3610c`.

## Ce que corrige la v4

Le retour sur la v3 signale un crop qui s’enclenche pendant l’arrivée du Réel suivant. Le code avait deux causes compatibles avec ce défaut : une passe toutes les 100 ms et la sélection d’une seule surface suffisamment visible.

La v4 conserve un état pour chaque surface vidéo rattachée au lecteur, y compris les vidéos adjacentes préchargées. Elle les cadre avant le dessin, sans seuil d’entrée dans l’écran. La recherche des vues se fait lors des changements de disposition ou de rattachement, avec une vérification de secours toutes les 400 ms pendant le rendu. La passe de transformation travaille à chaque image sur les surfaces déjà connues.

Chaque surface reçoit aussi une découpe correspondant à sa page. Quand la vidéo utilise la place libérée par la barre Instagram, l’espacement visuel des pages suit cette nouvelle hauteur : on ne laisse pas deux vidéos agrandies empiéter simplement sur le même espace. La position native du pager n’est pas modifiée.

La colonne d’actions est recherchée comme un groupe vertical contenant plusieurs catégories distinctes, dont les commentaires. C’est le groupe complet qui est déplacé. Un traitement tactile dans le lecteur maintient l’accès aux boutons lorsqu’ils dépassent leur ancien conteneur ; un glissement commencé sur un bouton annule son clic et rend le geste au pager. Les panneaux natifs gardent la priorité. Le placement peut être désactivé.

Les flags MobileConfig restent stables comme en v3. **Aucun rechargement automatique au pliage, au swipe ou au changement de cadrage.** L’ancien interrupteur v2 n’est plus utilisé.

## Profils et réglages

| Réglage initial | Écran externe | Écran interne |
| --- | --- | --- |
| Vidéo | Remplissage/crop | Présentation native entière |
| Barres Android | Masquées pendant les Réels | Conservées |
| Navigation Instagram | Masquée si reconnue | Conservée |
| Colonne d’actions | Proche du bord, cible 7 dp | Proche du bord, cible 14 dp |
| Like, commentaire, partage, sauvegarde | Conservés | Conservés |
| Mode minimal | Désactivé | Non appliqué |

La navigation Instagram et les actions du Réel ont désormais **deux réglages indépendants**. On peut gagner la hauteur des onglets sans retirer les boutons du Réel. La navigation est masquée avec `INVISIBLE`, pour éviter une remise en page provoquée par `GONE`.

- Toucher **Remplir** ou **Entière**, sur le lecteur, pour basculer immédiatement. Le libellé indique l’action proposée. Cela remet le zoom supplémentaire à 100 %.
- Faire un **appui long** sur ce bouton pour ouvrir **Cadrage Fold** : zoom, barres Android, navigation Instagram, placement des actions et mode minimal. Le même menu reste accessible par **⋯ → Cadrage Fold**.
- Le cadrage et le zoom sont mémorisés séparément pour les deux écrans. Les préférences v3 existantes sont conservées.
- **Commandes allégées** reste une option pour retirer les actions reconnues. Les commentaires et leurs parents sont protégés ; des boutons non reconnus peuvent rester visibles.
- Désactiver **Rapprocher les actions du bord** pour restaurer leur placement natif. Le déplacement reste limité à la zone tactile du lecteur ; les 7/14 dp sont une cible, pas une promesse sur toutes les variantes Instagram.

Un balayage depuis un bord peut révéler les barres système. Elles reviennent hors des Réels et pendant la saisie. **Recharger le lecteur…** reste un dépannage manuel avec une seconde confirmation, car il peut changer le Réel. Le cadrage courant n’en dépend pas.

## Installer dans Morphe

1. Se connecter à GitHub et ouvrir la dernière [compilation réussie de PatchInsta](https://github.com/senor-roboto/PatchInsta/actions/workflows/build-fold-reels.yml) correspondant à la v4.
2. Dans **Artifacts**, télécharger **piko-fold-reels-v4**, décompresser le ZIP et récupérer `piko-fold-reels-v4.mpp`. Le `.patch` du dépôt contient les sources, pas le fichier à importer dans Morphe.
3. Ouvrir le `.mpp` avec Morphe pour ajouter **Piko + Adaptive Fold Reels v4 (unofficial)**.
4. Repartir de l’APKM original **439.0.0.37.89 / arm64**. Pour cette opération, sélectionner les patches de **la source v4 uniquement** ; désélectionner Piko officiel et les anciennes sources Fold pour éviter les doublons.
5. Cocher **Adaptive Fold Reels (experimental)**, décoché par défaut, avec **Add settings** et les autres patches Piko habituels.
6. Conserver **le même package Clone et la même clé de signature Morphe** pour mettre à jour le clone installé. Patcher puis installer le résultat ; ne pas désinstaller le clone auparavant.
7. Ouvrir un Réel et essayer le nouveau comportement. Les options sont aussi disponibles dans **Piko → Divers**.

Le ZIP contient le bundle, `SHA256SUMS.txt`, ce guide, `LICENSE` et `NOTICE`. Les artefacts GitHub expirent après 14 jours ; **Run workflow** permet de les reconstruire.

## Vérification

Les contrôles JVM exécutent **253 assertions** de géométrie et de profil, dont le raccord entre pages pendant un swipe avec un viewport agrandi. Les **13 clés natives** restent vérifiées contre les mappings Piko, ainsi que les ressources françaises et anglaises.

Le workflow ajoute **14 scénarios de vues Android avec Robolectric** : voisins cadrés avant affichage, 121 étapes de swipe sans nouvelle découverte, stabilité des transformations, première disposition d’une nouvelle surface, détachement, restauration, changement de viewport, colonne entière, clic déplacé, passage du bouton au pager, priorité d’un panneau natif, annulation d’un appui, partage du clipping et indépendance des options. Leur réussite et la compilation du `.mpp` doivent être confirmées par le statut GitHub Actions de la révision téléchargée.

**Ces tests ne décodent pas de vidéos Instagram et ne valident pas le compositeur graphique Samsung.** L’APKM exact n’étant pas présent ici, l’injection du nouveau point d’entrée tactile doit aussi être confirmée au patching. La compilation ne constitue pas une garantie de fluidité ou de compatibilité visuelle sur l’appareil.

## Essai sur le Fold et diagnostic

Sur écran externe, faire quelques swipes lents, puis rapides. Le Réel entrant doit arriver déjà cadré. Vérifier ensuite le commentaire, le like et le partage ; commencer aussi un swipe depuis un bouton. Désactiver puis réactiver **Masquer la navigation Instagram** en laissant le mode minimal désactivé.

Ouvrir le téléphone sur un Réel en cours, tester **Remplir → Entière**, puis refermer. Le patch ne doit ni passer au Réel suivant ni demander une actualisation. Android ou Instagram peuvent encore reconstruire eux-mêmes l’écran lors d’un changement de configuration.

Si une variante du lecteur résiste, ouvrir **Cadrage Fold → Diagnostic du lecteur → Copier**, puis joindre ce texte et une courte capture vidéo. Le rapport indique les surfaces trouvées, les passes de recherche/rendu, les colonnes reconnues et la géométrie. Il n’inclut ni légendes, ni identifiants de Réels, ni données de compte, et n’est jamais envoyé automatiquement.

**Cadrage ?** indique qu’aucune surface utilisable n’a été cadrée. Les petites surfaces et les lecteurs sans page identifiable sont laissés à Instagram. Les bandes intégrées aux pixels peuvent nécessiter le zoom manuel. Si la détection des écrans se trompe avec le zoom d’affichage ou le partage d’écran, utiliser temporairement **Détection des écrans**, puis revenir sur **Automatique**.

## Sources et licence

Le rendu utilise les transformations et le clipping des vues Android ; le comportement matériel des surfaces distinctes reste dépendant de la plateforme. Voir l’implémentation officielle de [SurfaceView](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/core/java/android/view/SurfaceView.java) et la documentation de [TextureView](https://developer.android.com/reference/android/view/TextureView). Les tests de vues utilisent [Robolectric 4.14.1](https://github.com/robolectric/robolectric/tree/robolectric-4.14.1).

Dérivé non officiel de [Piko](https://github.com/crimera/piko), GPL-3.0-or-later. Licences et mentions amont conservées. Aucune affiliation avec Piko, Morphe, Instagram ou Samsung. Aucun APK Instagram n’est distribué.
