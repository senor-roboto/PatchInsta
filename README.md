# PatchInsta

Patch Piko expérimental pour les Réels Instagram sur Galaxy Fold.

## Télécharger le fichier pour Morphe

**Compilation réussie le 7 septembre 2026.**

[Télécharger le ZIP contenant piko-fold-reels-experimental.mpp](https://github.com/senor-roboto/PatchInsta/actions/runs/34107582526/artifacts/10013107938)

Le dépôt est privé : connecte-toi à ton compte GitHub pour télécharger. Décompresse le ZIP, puis ouvre le fichier `.mpp` avec Morphe. Le fichier `.patch` présent dans le dépôt contient les sources, pas le bundle à installer.

1. Ajouter le `.mpp` comme source locale dans Morphe.
2. Choisir Instagram et fournir l’APKM original **439.0.0.37.89 arm64-v8a**.
3. Dans la source **Piko + Adaptive Fold Reels (unofficial)**, cocher **Adaptive Fold Reels (experimental)** et conserver **Add settings** et ses dépendances.
4. Pour garder Instagram officiel, utiliser le patch Instagram **Clone** de Piko (par exemple `com.instagram.foldreels` / `Instagram Fold`).
5. Patcher et installer le résultat.

[Guide français complet](GUIDE-FR.md)

## Validation

[Compilation validée](https://github.com/senor-roboto/PatchInsta/actions/runs/34107582526), depuis le commit `3917a8aba15a404d16a57c4d028fdff21b530970` : compilation Android/Kotlin réussie, 33 assertions de politique et 15 clés de mappings vérifiées. La correction évite de créer la fenêtre Android avant l’initialisation d’Instagram.

Le rendu et l’application du bundle sur ton APKM restent à tester. Ce patch active des options natives de recadrage sur les fenêtres étroites et de disposition pour pliables sur les fenêtres larges ; il ne garantit pas encore la disparition de toutes les bandes noires ou le déplacement des boutons.

Empreinte SHA-256 du **ZIP GitHub Actions**, fournie par GitHub et concordante avec le journal de compilation :

`5d466ea60a4d24b264272fae4337d5c2957b521489b57582b4ddd658f43d1d55`

L’empreinte du `.mpp` est dans `SHA256SUMS.txt` à l’intérieur du ZIP.

## Reconstruire

Les sources restent dans ce dépôt. Le téléchargement ci-dessus expire le **21 septembre 2026** ; conserver le fichier téléchargé ou relancer [Build experimental Fold Reels](https://github.com/senor-roboto/PatchInsta/actions/workflows/build-fold-reels.yml) avec **Run workflow**. Une modification du patch sur `main` lance aussi la compilation.

Basé sur Piko `50744aa07bb41c4e1f942a06614ef4e6f2e3610c`, sous GPL-3.0-or-later. Modification non officielle. Voir LICENSE et NOTICE.
