# Piko — Réels adaptés au Fold, version 2 expérimentale

**Le fichier à utiliser dans Morphe est `piko-fold-reels-v2.mpp`, produit par GitHub Actions dans PatchInsta.** Télécharger uniquement le résultat de la dernière compilation réussie. Le rendu sur le Galaxy Z Fold8 reste à valider.

Le code est une modification non officielle de [Piko](https://github.com/crimera/piko), basée exactement sur le commit `50744aa07bb41c4e1f942a06614ef4e6f2e3610c`, version Piko 3.9.0. La cible héritée est **Instagram 439.0.0.37.89, arm64-v8a, versionCode 384510827**, au format APKM original. Les identifiants internes ont été vérifiés dans les sources de cette révision ; leur effet visuel reste à confirmer sur l’application.

## Ce que la v2 change

Le premier essai sur le Fold a confirmé que le recadrage fonctionne au démarrage sur l’écran externe. Les boutons se placent correctement sur l’écran interne après une rotation, mais la fermeture laisse parfois le cadrage précédent. Cela suggère une disposition mise en cache et un problème de synchronisation ; ce diagnostic reste à confirmer par le second essai.

La v1 pouvait aussi retourner les valeurs natives pendant la pause qui accompagne un pliage. La v2 conserve le dernier format valide et le relit avant les demandes de réglages provenant du fil principal d’Instagram.

| Fenêtre | Comportement demandé |
| --- | --- |
| Petite fenêtre : petit côté inférieur à 600 dp | Recadrage natif, indépendamment de la rotation. |
| Grande fenêtre : petit côté supérieur ou égal à 600 dp | Disposition native pour pliables, sans recadrage dynamique par défaut. |
| Transition stable petite ↔ grande, avec un lecteur de Réels visible | Recréation de l’écran Instagram après 450 ms de stabilisation. |
| Rotation dans le même format, premier démarrage ou absence de lecteur visible | Pas de recréation automatique demandée. |

Le but est que le nouveau lecteur et ses boutons soient construits avec les mêmes réglages. La v2 ne déplace pas arbitrairement les boutons : elle conserve la disposition native qui s’est montrée correcte après rotation lors de ton essai.

**La recréation peut interrompre la lecture, recommencer le Réel ou revenir au fil.** La conservation du Réel dépend de la restauration d’état d’Instagram. Il ne s’agit pas d’un arrêt du processus ni d’une rotation simulée. La recréation est limitée au lecteur visible, différée si l’activité est en pause, et ne se répète pas sur la même instance. Elle est aussi différée lorsqu’un champ de texte détient le focus. Un interrupteur permet de la désactiver.

## Cadrage depuis le Réel

Ouvrir **⋯ → Cadrage Fold** pour choisir **Vidéo entière sur écran interne** ou **Recadrer sur écran interne**. Le choix est conservé et le lecteur est actualisé. La même fenêtre contient **Actualiser le lecteur**, utile pour retester un affichage bloqué.

Le choix pour l’écran interne reste indépendant de celui de l’écran externe. Il est basé sur la taille de fenêtre : en partage d’écran, la petite fenêtre utilise le mode compact.

Les seuils numériques et limites de recadrage du moteur Instagram restent en place. La v2 ne garantit pas encore la suppression de toutes les bandes noires, notamment celles intégrées à la vidéo, ni le bon placement des commandes dans toutes les variantes du lecteur. L’effet du recadrage sur grand écran doit être testé.

## 1. Récupérer le fichier `.mpp`

Le dépôt [PatchInsta](https://github.com/senor-roboto/PatchInsta) contient déjà les sources et le workflow. Il est privé : se connecter au compte GitHub qui en est propriétaire.

1. Ouvrir [GitHub Actions](https://github.com/senor-roboto/PatchInsta/actions/workflows/build-fold-reels.yml).
2. Choisir la dernière compilation **réussie** correspondant au patch actuel.
3. Dans **Artifacts**, télécharger **piko-fold-reels-v2**, puis décompresser le ZIP.
4. Récupérer `piko-fold-reels-v2.mpp`. Le fichier `.patch` du dépôt contient les sources et ne doit pas être importé dans Morphe.

Le workflow se lance lors des changements du patch sur `main`. Pour reconstruire manuellement, choisir **Run workflow**. Aucun identifiant Instagram et aucun APKM ne sont nécessaires à la compilation des patches.

La compilation récupère une révision Piko fixe et exécute `./gradlew buildAndroid`, la tâche indiquée par le [modèle officiel Morphe](https://github.com/MorpheApp/morphe-patches-template). Les artefacts sont conservés 14 jours. Si un artefact a expiré, relancer le workflow. Le fichier `SHA256SUMS.txt` permet de vérifier le téléchargement.

## 2. Installer avec Morphe sur le Fold

1. Installer Morphe Manager depuis ses [releases officielles](https://github.com/MorpheApp/morphe-manager/releases/latest).
2. Copier le `.mpp` produit à l’étape précédente sur le téléphone. Depuis le gestionnaire de fichiers, l’ouvrir avec Morphe et ajouter la source locale. Morphe annonce la prise en charge de [l’ouverture directe des fichiers `.mpp`](https://morphe.software/changelog).
3. Sélectionner la source **Piko + Adaptive Fold Reels v2 (unofficial)**, puis Instagram. Le paquet officiel Piko seul ne contient pas cette modification.
4. Fournir l’**APKM original d’Instagram 439.0.0.37.89 pour arm64-v8a**, obtenu via le téléchargement proposé par Morphe/APKMirror. Ne pas fusionner les splits et ne pas prendre un APK déjà modifié. [Piko demande l’APKM original](https://github.com/crimera/piko#%EF%B8%8F-usage).
5. Dans la sélection des patches de cette source, cocher **Adaptive Fold Reels (experimental)** et garder sa dépendance **Add settings**. Le patch expérimental est volontairement décoché par défaut. Choisir les autres patches Piko selon tes besoins, sans tout cocher.
6. Pour essayer sans remplacer Instagram officiel, sélectionner le patch Instagram **Clone** de Piko, avec par exemple le nom `Instagram Fold` et le package `com.instagram.foldreels`. Utiliser ce patch précis, comme l’indique Piko, plutôt que le patch universel « Change package name ». Conserver le même package et la même clé de signature Morphe pour les futures mises à jour du clone.
7. Lancer le patching, puis installer le résultat et autoriser Morphe à installer des applications si Android le demande. Aucun accès root n’est requis pour l’installation du clone. Se reconnecter dans le clone.

Ce `.mpp` contient le bundle Piko modifié complet : sélectionner ses patches dans cette seule source pour cet essai, afin d’éviter un doublon avec les mêmes patches de la source officielle.

## 3. Réglages et retour arrière

Dans **réglages Piko → Divers**, quatre interrupteurs sont disponibles :

- **Réels adaptés au Fold (expérimental)** : interrupteur général.
- **Recadrer les Réels en petite fenêtre** : activé par défaut.
- **Recadrer les Réels en grande fenêtre** : désactivé par défaut ; également accessible depuis **⋯ → Cadrage Fold**.
- **Actualiser les Réels au changement de format** : activé par défaut. Le désactiver pour garder uniquement les réglages natifs, sans recréation automatique.

Redémarrer Instagram après modification de l’interrupteur général. Après un changement de cadrage depuis Divers, utiliser **⋯ → Cadrage Fold → Actualiser le lecteur** ou redémarrer Instagram. Le choix depuis le menu du Réel lance déjà cette actualisation.

Pour mettre à jour le clone existant, conserver **le même package Clone et la même clé de signature Morphe**. Repartir de l’APKM original et sélectionner les patches de la **source v2 uniquement**. Désélectionner les sources Piko officielle et Fold v1 pour cette opération : ce bundle contient déjà Piko complet.

Pour revenir en arrière, désactiver l’actualisation automatique et/ou le patch dans Divers. Le premier bundle reste disponible dans l’historique des compilations. Aucun fichier APK Instagram n’est distribué dans ce dépôt.

## Validation et prochaine étape

Vérifié ici : compilation JVM de la politique de sélection ; **59 assertions de politique et de transitions réussies** ; correspondance des **15 clés exactes** avec les mappings Piko ; validité XML des libellés français et anglais ; contrôle du diff source. La compilation Android se fait dans GitHub Actions : son statut fait foi pour chaque révision. **Une compilation réussie ne valide pas encore le patching de ton APKM ni le rendu sur appareil.**

Pour valider sur appareil : démarrer fermé, lire un Réel, ouvrir en portrait sans rotation, puis refermer. Vérifier le crop externe et la position des boutons internes. Tester ensuite la rotation, le menu Cadrage Fold, un second pliage et le partage d’écran. Noter si la recréation conserve le Réel, le recommence ou revient au fil. Signaler également si le menu Cadrage Fold est absent ou si aucun rafraîchissement ne se produit.

Si les bandes persistent ou si les boutons restent mal placés, fournir l’APKM exact utilisé, une capture sur chaque écran et, si possible, un court enregistrement du pliage. Ces éléments permettront d’identifier les conteneurs vidéo et les commandes réellement utilisés par cette version. Un recadrage forcé ou un déplacement précis des boutons nécessite cette analyse supplémentaire ; le présent prototype ne prétend pas la remplacer.

## Fichiers et licence

Le fichier `.patch` contient les modifications Kotlin/Java, les deux traductions, les tests et le nom distinct du bundle. Le workflow de compilation est fourni séparément dans le même kit. Aucun binaire Instagram n’est distribué.

Dérivé non officiel de Piko, sous GPL-3.0-or-later, avec conservation de `LICENSE` et du `NOTICE` amont. Aucune affiliation revendiquée avec Piko, Morphe, Instagram ou Samsung.
