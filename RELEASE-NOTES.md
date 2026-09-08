PatchInsta 4.1.0, dérivé non officiel de Piko 3.9.0, pour Instagram **439.0.0.37.89 / arm64-v8a / versionCode 384510827**.

- Démarrage du presenter depuis le viewer attaché, sans attendre un pliage.
- Presets **Plein écran propre** et **Instagram complet** ; commentaire seul ; métadonnées natives compactes.
- Dégradé supérieur reconnu étendu au bord du viewport ; décor de card reconnu neutralisé et réversible.
- Renderer v4 conservé : voisins précadrés, swipe, clipping et gestes ; aucun rechargement automatique.
- Source Morphe stable, ZIP, bundle direct, checksums et informations de compilation vérifiés.

[Ajouter à Morphe](https://morphe.software/add-source?github=senor-roboto%2FPatchInsta) — URL manuelle : `https://github.com/senor-roboto/PatchInsta`.

La source distante nécessite que ce dépôt soit **public**. Un accès GitHub authentifié aux fichiers privés ne suffit pas pour Morphe.

Cocher **Adaptive Fold Reels** avec les patchs de cette source uniquement. Repartir de l’APKM original, conserver le **même package Clone et le même keystore Morphe**, puis installer par-dessus. Dans le lecteur, appui long sur le raccourci → **Plein écran propre** pour appliquer tous les nouveaux choix.

Les tests CI et le chargement réel du bundle sont détaillés dans `build-info.json` et `test-results.json`. Pas de validation matérielle Samsung ni d’application à un APKM durant cette itération ; les détections inconnues restent natives. Le bloc interactif respecte les limites tactiles du viewer, ce qui peut laisser un retrait inférieur.

Consulter `GUIDE-FR.md`, `SHA256SUMS.txt` et le [compte rendu](https://github.com/senor-roboto/PatchInsta/blob/main/ENGINEERING-4.1.md).
