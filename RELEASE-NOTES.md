PatchInsta 4.1.1 corrige les chemins de présentation signalés après les essais réels de la 4.1.0.

- Rattrapage au premier dessin du viewer et résolution du propriétaire de fenêtre quand le contexte d’inflation n’est pas une Activity.
- Bandeau partagé ancré au viewport pendant les swipes ; raccourci placé sous le bandeau ; dégradé de background étendu sans agrandir les textes.
- Métadonnées découvertes dans les overlays frères du wrapper vidéo, mode compact aussi sans bouton Suivre, caption native spécialisée bornée sans copie de texte.
- Bordures de calques décoratifs correspondants et composites nettoyées en conservant les gradients.

La vidéo, les pages préchargées et les gestes continuent d’utiliser le lecteur Instagram existant. Aucun rechargement automatique ni changement des MobileConfig v4 par défaut.

**Morphe :** actualiser la source PatchInsta déjà ajoutée vers **4.1.1**, repatcher l’APKM original **439.0.0.37.89 / arm64-v8a / 384510827**, puis installer par-dessus avec le même package Clone et le même keystore. Mettre à jour le bundle seul ne modifie pas l’APK déjà installé. Aucun nouvel import de source nécessaire.

La CI exige 77 scénarios Android, 305 assertions JVM, 13 mappings FR/EN et 9 tests de distribution, puis compile et charge le vrai MPP avec Morphe. Elle vérifie aussi les assets téléchargés, le ZIP, leurs SHA-256 et l’accès anonyme de la source publique.

Les scénarios Android reproduisent des hiérarchies et gestes ; ils ne constituent pas une exécution d’Instagram sur le Fold. Les captures et la vidéo ont été analysées, mais leur hiérarchie de vues n’est pas accessible. Les branches inconnues restent natives ; le diagnostic structurel permet de les identifier sans extraire de texte utilisateur.

Consulter GUIDE-FR.md, ENGINEERING-4.1.1.md dans le dépôt et build-info.json / test-results.json dans la Release.
