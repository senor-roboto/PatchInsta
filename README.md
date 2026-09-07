# PatchInsta — Adaptive Fold Reels v3

Modification expérimentale non officielle de Piko pour Instagram **439.0.0.37.89 / arm64**, destinée aux deux écrans du Galaxy Z Fold.

La v3 remplace le crop demandé par paramètres natifs par un cadrage direct de la surface vidéo existante. Elle ajoute un bouton de cadrage sur le lecteur, un zoom mémorisé par écran, le masquage des barres Android sur écran externe et un mode optionnel de commandes allégées.

**Aucun rechargement automatique au pliage ni au changement de cadrage.** L’ancien réglage v2 n’est plus utilisé. Un rechargement manuel reste disponible avec confirmation explicite.

Télécharger l’artefact **piko-fold-reels-v3** dans la dernière [compilation réussie](https://github.com/senor-roboto/PatchInsta/actions/workflows/build-fold-reels.yml). Extraire `piko-fold-reels-v3.mpp`, puis l’ouvrir avec Morphe. Sélectionner uniquement la source **Piko + Adaptive Fold Reels v3 (unofficial)** et cocher **Adaptive Fold Reels (experimental)**. Garder le même package Clone et la même clé de signature pour mettre à jour l’installation existante.

Voir le [guide français](GUIDE-FR.md) pour les options, l’installation et le test. Les sources complètes de notre modification figurent dans [piko-fold-reels.patch](piko-fold-reels.patch), à appliquer au commit Piko `50744aa07bb41c4e1f942a06614ef4e6f2e3610c` ; le workflow le fait automatiquement.

128 assertions JVM et 13 correspondances de paramètres natifs contrôlées. La compilation ne valide pas le rendu sur appareil. Les contrôles inconnus restent visibles ; le menu fournit un diagnostic structurel copiable pour analyser les variantes du lecteur.

Piko 3.9.0 modifié, version du bundle `3.9.0-foldreels.3`. GPL-3.0-or-later, avec conservation de `LICENSE` et `NOTICE`. Aucune affiliation avec les projets d’origine.
