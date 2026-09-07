# Piko — Réels adaptés au Fold, prototype expérimental

**Le fichier à utiliser dans Morphe est `piko-fold-reels-experimental.mpp`, produit par GitHub Actions dans PatchInsta.** Télécharger uniquement le résultat de la dernière compilation réussie. Le rendu sur le Galaxy Z Fold8 reste à valider.

Le code est une modification non officielle de [Piko](https://github.com/crimera/piko), basée exactement sur le commit `50744aa07bb41c4e1f942a06614ef4e6f2e3610c`, version Piko 3.9.0. La cible héritée est **Instagram 439.0.0.37.89, arm64-v8a, versionCode 384510827**, au format APKM original. Les identifiants internes ont été vérifiés dans les sources de cette révision ; leur effet visuel reste à confirmer sur l’application.

## Comportement demandé par le patch

| Fenêtre Instagram | Options natives activées |
| --- | --- |
| Portrait et largeur inférieure à 600 dp, typiquement écran externe | Recadrage dynamique des Réels organiques, disposition à une colonne. |
| Largeur supérieure ou égale à 600 dp, typiquement écran interne | Recadrage dynamique désactivé ; disposition native pour pliables, options de pleine hauteur et de commentaires en deux panneaux. |
| Petite fenêtre en paysage | Recadrage dynamique et disposition en deux panneaux désactivés. |
| Dimensions indisponibles ou patch désactivé | Pas de remplacement de ces options par ce patch. |

Le choix dépend de la **fenêtre courante**, et non du nom du téléphone. Un écran intérieur en partage d’écran peut donc utiliser le mode étroit. Les dimensions physiques du Fold8 ne sont pas codées en dur. Les changements de configuration, le retour dans l’application et les changements de disposition actualisent le choix.

Cette approche conserve le lecteur, les boutons, les zones tactiles et les gestes natifs. Elle évite d’agrandir l’ensemble de l’interface avec la vidéo. Elle ne garantit cependant **ni un plein écran sans aucune bande noire, ni le déplacement des boutons dans les bandes noires** : les seuils numériques du moteur Instagram restent en place. Une bande intégrée aux pixels de la vidéo ne sera pas détectée. Le mode grand écran ne reconstruit pas une image déjà recadrée par un autre traitement Instagram. Les effets attendus des options natives sont déduits de leurs noms dans les mappings Piko ; ce ne sont pas des observations sur appareil.

## 1. Récupérer le fichier `.mpp`

Le dépôt [PatchInsta](https://github.com/senor-roboto/PatchInsta) contient déjà les sources et le workflow. Il est privé : se connecter au compte GitHub qui en est propriétaire.

1. Ouvrir [GitHub Actions](https://github.com/senor-roboto/PatchInsta/actions/workflows/build-fold-reels.yml).
2. Choisir la dernière compilation **réussie** correspondant au patch actuel.
3. Dans **Artifacts**, télécharger **piko-fold-reels-experimental**, puis décompresser le ZIP.
4. Récupérer `piko-fold-reels-experimental.mpp`. Le fichier `.patch` du dépôt contient les sources et ne doit pas être importé dans Morphe.

Le workflow se lance lors des changements du patch sur `main`. Pour reconstruire manuellement, choisir **Run workflow**. Aucun identifiant Instagram et aucun APKM ne sont nécessaires à la compilation des patches.

La compilation récupère une révision Piko fixe et exécute `./gradlew buildAndroid`, la tâche indiquée par le [modèle officiel Morphe](https://github.com/MorpheApp/morphe-patches-template). Les artefacts sont conservés 14 jours. Si un artefact a expiré, relancer le workflow. Le fichier `SHA256SUMS.txt` permet de vérifier le téléchargement.

## 2. Installer avec Morphe sur le Fold

1. Installer Morphe Manager depuis ses [releases officielles](https://github.com/MorpheApp/morphe-manager/releases/latest).
2. Copier le `.mpp` produit à l’étape précédente sur le téléphone. Depuis le gestionnaire de fichiers, l’ouvrir avec Morphe et ajouter la source locale. Morphe annonce la prise en charge de [l’ouverture directe des fichiers `.mpp`](https://morphe.software/changelog).
3. Sélectionner la source **Piko + Adaptive Fold Reels (unofficial)**, puis Instagram. Le paquet officiel Piko seul ne contient pas cette modification.
4. Fournir l’**APKM original d’Instagram 439.0.0.37.89 pour arm64-v8a**, obtenu via le téléchargement proposé par Morphe/APKMirror. Ne pas fusionner les splits et ne pas prendre un APK déjà modifié. [Piko demande l’APKM original](https://github.com/crimera/piko#%EF%B8%8F-usage).
5. Dans la sélection des patches de cette source, cocher **Adaptive Fold Reels (experimental)** et garder sa dépendance **Add settings**. Le patch expérimental est volontairement décoché par défaut. Choisir les autres patches Piko selon tes besoins, sans tout cocher.
6. Pour essayer sans remplacer Instagram officiel, sélectionner le patch Instagram **Clone** de Piko, avec par exemple le nom `Instagram Fold` et le package `com.instagram.foldreels`. Utiliser ce patch précis, comme l’indique Piko, plutôt que le patch universel « Change package name ». Conserver le même package et la même clé de signature Morphe pour les futures mises à jour du clone.
7. Lancer le patching, puis installer le résultat et autoriser Morphe à installer des applications si Android le demande. Aucun accès root n’est requis pour l’installation du clone. Se reconnecter dans le clone.

Ce `.mpp` contient le bundle Piko modifié complet : sélectionner ses patches dans cette seule source pour cet essai, afin d’éviter un doublon avec les mêmes patches de la source officielle.

## 3. Réglages et retour arrière

Dans **réglages Piko → Divers**, deux interrupteurs sont ajoutés :

- **Réels adaptés au Fold (expérimental)** : active l’ensemble du comportement.
- **Recadrer les Réels en portrait étroit** : demande le recadrage sur la petite fenêtre. Le désactiver désactive cette demande de recadrage ; cela ne déplace pas les boutons dans les bandes.

Les deux sont activés au premier lancement si le patch a été sélectionné. Redémarrer complètement Instagram après leur modification. S’ils sont absents, vérifier que le patch expérimental a bien été coché dans la source modifiée.

Si le pliage laisse l’ancienne disposition, quitter puis rouvrir le lecteur de Réels. Si nécessaire, forcer l’arrêt d’Instagram puis le relancer : certains choix peuvent être mis en cache dans le lecteur natif. Le patch ne redémarre pas automatiquement l’application pendant la lecture.

Pour revenir en arrière, désactiver le premier interrupteur puis redémarrer. Les éventuelles options définies par d’autres patches ou dans le menu développeur redeviennent prioritaires. Avec le clone, il est aussi possible de désinstaller uniquement `Instagram Fold` et de continuer à utiliser Instagram officiel.

## Validation et prochaine étape

Vérifié ici : compilation JVM de la politique de sélection ; **33 assertions réussies** ; correspondance des **15 clés exactes** avec les mappings Piko ; validité XML des libellés français et anglais ; contrôle du diff source. La compilation Android se fait dans GitHub Actions : son statut fait foi pour chaque révision. **Une compilation réussie ne valide pas encore le patching de ton APKM ni le rendu sur appareil.**

Pour valider sur appareil : lire le même Réel vertical sur les deux écrans, ouvrir les commentaires, plier/déplier pendant la lecture, faire pivoter le téléphone puis essayer le partage d’écran. Vérifier le cadrage, les sous-titres, les boutons, la barre de navigation et le défilement.

Si les bandes persistent ou si les boutons restent mal placés, fournir l’APKM exact utilisé, une capture sur chaque écran et, si possible, un court enregistrement du pliage. Ces éléments permettront d’identifier les conteneurs vidéo et les commandes réellement utilisés par cette version. Un recadrage forcé ou un déplacement précis des boutons nécessite cette analyse supplémentaire ; le présent prototype ne prétend pas la remplacer.

## Fichiers et licence

Le fichier `.patch` contient les modifications Kotlin/Java, les deux traductions, les tests et le nom distinct du bundle. Le workflow de compilation est fourni séparément dans le même kit. Aucun binaire Instagram n’est distribué.

Dérivé non officiel de Piko, sous GPL-3.0-or-later, avec conservation de `LICENSE` et du `NOTICE` amont. Aucune affiliation revendiquée avec Piko, Morphe, Instagram ou Samsung.
