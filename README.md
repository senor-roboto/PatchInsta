# PatchInsta — Adaptive Fold Reels v4

Modification expérimentale non officielle de Piko pour Instagram **439.0.0.37.89 / arm64**, destinée aux deux écrans du Galaxy Z Fold.

La v4 cadre les surfaces des Réels préchargés avant affichage, puis met à jour leurs transformations à chaque image. La découverte des vues est séparée du rendu. Chaque page possède sa propre découpe, avec un espacement adapté à la hauteur libérée par la navigation Instagram.

La colonne d’actions peut être rapprochée du bord tout en conservant ses interactions natives. Le masquage de la navigation Instagram est indépendant du mode minimal : les actions restent visibles par défaut. Le menu sur la vidéo conserve le cadrage et le zoom par écran.

**Aucun rechargement automatique au pliage ni au changement de cadrage.** Les flags natifs restent stables comme en v3. Le rechargement manuel demande une confirmation explicite.

Récupérer **piko-fold-reels-v4** dans la dernière [compilation réussie](https://github.com/senor-roboto/PatchInsta/actions/workflows/build-fold-reels.yml). Extraire `piko-fold-reels-v4.mpp`, puis l’ouvrir avec Morphe. Sélectionner **la source v4 uniquement** et cocher **Adaptive Fold Reels (experimental)**. Garder le même package Clone et la même clé de signature pour mettre à jour l’installation existante.

Voir le [guide français](GUIDE-FR.md) pour l’installation, les options et le test. Les modifications complètes figurent dans [piko-fold-reels.patch](piko-fold-reels.patch), à appliquer au commit Piko `50744aa07bb41c4e1f942a06614ef4e6f2e3610c` ; le workflow le fait automatiquement.

Le workflow vérifie 253 assertions JVM, 13 clés natives et 14 scénarios de vues Android, puis compile le bundle. Son statut fait foi pour la révision téléchargée. Ces tests ne remplacent ni le patching de l’APKM ni le rendu sur le Fold ; le menu fournit un diagnostic structurel copiable.

Piko 3.9.0 modifié, bundle `3.9.0-foldreels.4`. GPL-3.0-or-later, `LICENSE` et `NOTICE` conservés. Aucune affiliation avec les projets d’origine.
