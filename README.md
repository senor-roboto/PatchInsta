# PatchInsta

**Adaptive Fold Reels**, dérivé non officiel de **Piko 3.9.0**, pour adapter les Réels Instagram aux deux écrans du Galaxy Z Fold. Bundle **4.1.2** ; le nom de la source et celui du patch restent identiques lors des prochaines mises à jour.

Cible : **Instagram 439.0.0.37.89**, APKM original, **arm64-v8a / versionCode 384510827**. Aucun APK Instagram n’est distribué.

## Ajouter PatchInsta à Morphe

[Ajouter la source avec Morphe](https://morphe.software/add-source?github=senor-roboto%2FPatchInsta), ou coller cette URL dans l’ajout de **source distante** de Morphe :

```text
https://github.com/senor-roboto/PatchInsta
```

[JSON de la source](https://raw.githubusercontent.com/senor-roboto/PatchInsta/main/patches-bundle.json) · [Dernière Release](https://github.com/senor-roboto/PatchInsta/releases/latest) · [Guide français](GUIDE-FR.md) · [Analyse et limites](ENGINEERING-4.1.2.md)

Le dépôt est désormais public. Si PatchInsta est déjà ajouté dans Morphe, **actualiser cette même source vers 4.1.2**, repatcher l’APKM original et installer par-dessus. Aucun nouvel import de source n’est nécessaire.

## Première installation / migration depuis la v4 locale

1. Sauvegarder/exporter la **clé de signature (keystore) Morphe** et noter le package du clone déjà installé.
2. Ajouter la source distante une fois. Pour cette opération Instagram, sélectionner ses patchs uniquement : PatchInsta inclut déjà Piko. Désélectionner les anciennes sources locales Fold et Piko officiel pour éviter les doublons.
3. Choisir l’APKM original compatible, puis **Adaptive Fold Reels** et les patchs Piko habituels, dont **Add settings**. Le patch Fold est optionnel, à cocher explicitement.
4. Garder **exactement le même package Clone et la même clé de signature** ; patcher, puis installer par-dessus le clone actuel. Ne pas le désinstaller.
5. Dans un Réel, faire un appui long sur **Entière / Remplir**, puis choisir **Plein écran propre** sur l’écran externe. Les anciens réglages explicitement enregistrés sont conservés/migrés ; ce preset applique tous les nouveaux choix.

## Présentation

| Profil | Écran externe, « Plein écran propre » | Écran interne, défaut |
|---|---|---|
| Vidéo | Remplissage/crop live | Vidéo native entière |
| Barres Android / onglets Instagram | Masqués pendant les Réels | Conservés |
| Actions | Commentaire seul et compteur associé | Toutes |
| Auteur et caption | Vues natives compactes, y compris les calques frères et les comptes déjà suivis | Présentation complète |
| Décor et dégradé | Décor reconnu adapté ; gradients natifs haut/bas redessinés dans la fenêtre | État natif restauré |

**Instagram complet** restaure la présentation native du cover. **Personnaliser** donne accès aux trois modes d’actions, trois modes de métadonnées et aux options indépendantes. Le cadrage, le zoom et le raccourci sont mémorisés par écran. Aucun changement de mode, pliage ou swipe ne demande un rechargement automatique du lecteur.

Le bloc interactif reste à l’intérieur des limites tactiles du viewer. Une variante dont ces limites s’arrêtent au-dessus des anciens onglets peut donc conserver un retrait en bas ; le patch privilégie des boutons fonctionnels. Le bandeau partagé reconnu reste ancré au viewport et le raccourci se place en dessous. Un décor ou une structure non reconnus restent natifs. Le diagnostic explique les détections sans copier de contenu utilisateur.

## Mises à jour suivantes

Actualiser **la même source PatchInsta** dans Morphe, puis repatcher l’APKM compatible et installer par-dessus. Ne pas importer un nouveau `.mpp` à chaque version. Le gestionnaire peut signaler la nouvelle source puis proposer de repatcher l’application suivie ; cela ne met pas automatiquement l’APK installé à jour.

Le package et la signature doivent rester identiques. Réinstaller Morphe sans restaurer son keystore peut rendre impossible l’installation par-dessus. Conserver aussi le package choisi par le patch Clone.

## Téléchargement manuel durable

[PatchInsta-4.1.2.mpp](https://github.com/senor-roboto/PatchInsta/releases/download/v4.1.2/PatchInsta-4.1.2.mpp) · [PatchInsta-4.1.2.zip](https://github.com/senor-roboto/PatchInsta/releases/download/v4.1.2/PatchInsta-4.1.2.zip) · [SHA-256](https://github.com/senor-roboto/PatchInsta/releases/download/v4.1.2/SHA256SUMS.txt)

Les fichiers de Release sont durables. Les artefacts Actions servent uniquement au transfert et au diagnostic de CI.

## Sources, compilation et vérification

Appliquer `piko-fold-reels.patch` à [Piko au commit épinglé](https://github.com/crimera/piko/tree/50744aa07bb41c4e1f942a06614ef4e6f2e3610c). Java 17, Android SDK et accès Maven Morphe nécessaires. La [CI](https://github.com/senor-roboto/PatchInsta/actions/workflows/build-fold-reels.yml) vérifie l’application du diff, les tests, les 13 mappings et les ressources FR/EN, compile le `.mpp`, le charge avec Morphe, puis vérifie le ZIP et les téléchargements de Release. Aucune publication si un de ces contrôles échoue.

`release.json`, le manifeste compilé et le JSON Morphe doivent porter la même version. Pour publier ensuite, augmenter la version dans `release.json` et dans le patch de `gradle.properties`, ajouter une entrée **Instagram** au [CHANGELOG](CHANGELOG.md), puis pousser sur `main`. Le workflow publie les assets avant le feed, sans force-push. Il ne remplace jamais un binaire déjà publié sous la même version.

Les tests Android simulent des vues et gestes ; ils ne décodent pas les vidéos Instagram ni le compositeur Samsung. Le nouvel APK doit encore être essayé sur l’appareil.

GPL-3.0-or-later. [LICENSE](LICENSE) et [NOTICE](NOTICE) amont conservés. Aucune affiliation à Piko, Morphe, Meta ou Samsung.
