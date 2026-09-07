# Piko — Réels adaptés au Fold, v3 expérimentale

Le fichier à importer dans Morphe est **`piko-fold-reels-v3.mpp`**. Le bundle contient Piko complet, avec notre modification non officielle. Il cible **Instagram 439.0.0.37.89, arm64-v8a, versionCode 384510827**, à partir de son **APKM original**. Base Piko 3.9.0, commit `50744aa07bb41c4e1f942a06614ef4e6f2e3610c`.

## Pourquoi cette révision

Les essais v2 montrent que demander le recadrage par les paramètres internes d’Instagram ne suffit pas : le lecteur peut garder sa disposition et ses limites de crop. La recréation ajoutée en v2 peut également changer de Réel. La v3 supprime ce mécanisme, y compris lorsque son ancien interrupteur était resté activé.

La v3 recherche la surface Android du lecteur de Réels connu de Piko, puis en change l’échelle et la position. Elle garde ses proportions, ne remplace pas le lecteur, ne change pas sa source et ne déclenche aucune navigation. Les réglages natifs de disposition restent stables entre les écrans pour éviter les bascules de paramètres mis en cache.

## Commandes

- **Bouton sur la vidéo** : un toucher sur **Remplir** agrandit la vidéo ; **Entière** restaure sa présentation native. Le libellé indique l’action proposée. Cela remet aussi le zoom supplémentaire à 100 %.
- **Appui long sur ce bouton** : ouvre **Cadrage Fold**, avec le zoom de 100 à 250 %, les options et le diagnostic. Le même menu reste accessible par **⋯ → Cadrage Fold**.
- **Profils indépendants** : le choix de cadrage et le zoom sont mémorisés séparément pour les écrans externe et interne. Le menu indique le profil qu’il modifie.

| Réglage initial | Écran externe | Écran interne |
| --- | --- | --- |
| Cadrage | Remplissage par agrandissement uniforme | Présentation native, vidéo entière |
| Barres Android | Masquées pendant les Réels | Conservées |
| Commandes Instagram | Conservées ; mode allégé en option | Conservées |
| Pliage, rotation, changement de cadrage | Aucun rechargement demandé par le patch | Aucun rechargement demandé par le patch |

**Commandes allégées sur écran externe** masque les boutons reconnus sans masquer volontairement les commentaires. La barre Instagram est également masquée si son identité et sa position correspondent ; sa zone peut alors être utilisée par la vidéo. Les boutons non reconnus restent présents. Ce mode est désactivé par défaut : l’activer depuis l’appui long pour essayer le plein écran plus dégagé, et le désactiver pour retrouver les commandes.

Les barres système peuvent être révélées par un balayage depuis un bord. Elles sont restaurées en quittant les Réels, en passant sur le grand écran ou pendant la saisie. L’option se désactive également depuis le menu.

Le cadrage prend effet au prochain passage de rendu, sans attendre un nouveau Réel. Le zoom manuel peut aider lorsque des bandes font partie des pixels de la vidéo, au prix d’une coupe plus importante. Le mode Entière remet les transformations du patch à leur état précédent.

## Installer la mise à jour avec Morphe

1. Se connecter à GitHub, ouvrir [les compilations de PatchInsta](https://github.com/senor-roboto/PatchInsta/actions/workflows/build-fold-reels.yml), puis la dernière compilation réussie de la **v3**.
2. Dans **Artifacts**, télécharger **piko-fold-reels-v3**, décompresser le ZIP et récupérer `piko-fold-reels-v3.mpp`. Le fichier `.patch` du dépôt contient les sources et ne s’importe pas dans Morphe.
3. Ouvrir le `.mpp` avec Morphe pour ajouter la source **Piko + Adaptive Fold Reels v3 (unofficial)**.
4. Repartir de l’APKM original **439.0.0.37.89 / arm64**, puis sélectionner **uniquement cette source v3** pour l’opération. Désélectionner les sources Piko officielle, Fold v1 et Fold v2 : leurs patches seraient appliqués en doublon.
5. Cocher **Adaptive Fold Reels (experimental)**, décoché par défaut, et conserver sa dépendance **Add settings**. Choisir les autres patches Piko habituels.
6. Pour mettre à jour ton clone existant, conserver **le même package Clone et la même clé de signature Morphe**. Patcher puis installer le résultat. Il n’est pas nécessaire de désinstaller le clone auparavant.
7. Ouvrir Instagram, puis un Réel. Si nécessaire, vérifier **réglages Piko → Divers → Réels adaptés au Fold**. Le réglage obsolète d’actualisation automatique de v2 a été retiré.

Le bundle contient aussi `SHA256SUMS.txt`, le présent guide, `LICENSE` et `NOTICE`. Les artefacts GitHub expirent après 14 jours ; **Run workflow** permet de les reconstruire.

## Test utile sur le Fold

Lire un Réel reconnaissable sur l’écran externe, ouvrir le téléphone sans tourner, toucher **Remplir**, puis **Entière**, et refermer. Vérifier que le patch ne fait plus passer au Réel suivant. Tester aussi un balayage vers le Réel suivant, la rotation et l’ouverture des commentaires avec le clavier.

Tester ensuite les **Commandes allégées**. Vérifier quelles commandes disparaissent, que les commentaires restent accessibles, et que la désactivation remet la navigation Instagram. Le contrôle de cadrage doit rester accessible.

## Limites et diagnostic

Les calculs de géométrie et de profil sont vérifiés par **128 assertions JVM**, et **13 clés natives** sont contrôlées contre les mappings Piko. Le XML français et anglais est vérifié. Le résultat de la compilation Android est visible dans GitHub Actions. **Ces contrôles ne remplacent pas le patching de l’APKM ni le test du rendu sur ton Fold.**

La surface est détectée au moment de la lecture, parmi les `TextureView` et `SurfaceView` du lecteur identifié. Aucun APKM n’était disponible pour analyser toutes les variantes Instagram. Une vidéo rendue autrement, une bande intégrée au fichier ou un panneau opaque différent peut encore limiter le résultat. Le mode Entière conserve la présentation native : il ne peut pas récupérer des pixels déjà coupés à la source. La transformation est prise en charge à partir d’Android 10 ; ton Android 17 entre dans cette plage.

Si **Cadrage ?** apparaît, toucher le bouton pour ouvrir les options. Si le crop ou une commande échoue, utiliser **Cadrage Fold → Diagnostic du lecteur → Copier**, puis joindre le texte et une capture de l’écran concerné. Le rapport contient des classes de vues, identifiants de ressources et dimensions ; il ne copie ni légendes, ni identifiants de Réels, ni données de compte. Il n’est envoyé nulle part automatiquement.

La détection automatique combine taille et proportions de la fenêtre. Si elle se trompe avec le zoom d’affichage ou le partage d’écran, **Détection des écrans** permet de forcer un profil pour vérifier le comportement. Revenir sur **Automatique** pour reprendre le changement de profil au pliage.

**Recharger le lecteur…** est uniquement un dépannage manuel avec une seconde confirmation indiquant qu’il peut changer le Réel. Le nouveau cadrage ne nécessite pas ce bouton. Le patch ne demande plus de recréation automatique ; Android ou Instagram peuvent néanmoins reconstruire eux-mêmes l’écran lors d’un changement de configuration.

## Sources techniques et licence

Le rendu s’appuie sur les propriétés de transformation des vues Android. La documentation distingue la [transformation interne d’une TextureView](https://developer.android.com/reference/android/view/TextureView#setTransform(android.graphics.Matrix)) de la taille de la vue, et décrit la synchronisation des [transformations de SurfaceView](https://developer.android.com/reference/android/view/SurfaceView). Le code modifie la vue de rendu et restaure ses propriétés ; il ne substitue ni surface ni moteur de lecture.

Dérivé non officiel de [Piko](https://github.com/crimera/piko), GPL-3.0-or-later. Les mentions et licences amont sont conservées. Aucune affiliation avec Piko, Morphe, Instagram ou Samsung. Aucun APK Instagram n’est distribué.
