# PatchInsta 4.1.9

- Cible le cadre résiduel identifié dans le diagnostic Fold : BorderColorDrawable Litho sur le parent du média. La neutralisation reste limitée au lecteur compact transformé et aux réglages de nettoyage de l'écran externe.
- Reconnaît le bloc auteur Litho et adapte séparément le dégradé inférieur, en préservant les contrôles natifs.
- Mesure la première ligne de légende et ses offsets natifs ; conserve la présentation native si la mesure est ambiguë.
- 141 scénarios Android, 22 contrôles bytecode, 305 contrôles de géométrie et 13 contrôles de mappings passent. Les 60 patches s'appliquent au véritable APKM Instagram 439 ; l'APK de laboratoire démarre dans l'émulateur sans crash relevé.
- Publication demandée par l'utilisateur pour tester via sa source Morphe existante. Le rendu visuel sur le Fold reste à confirmer ; aucun test physique réussi n'est revendiqué.

Dans Morphe, actualiser la source PatchInsta existante, repatcher l'APKM original Instagram 439.0.0.37.89 avec Adaptive Fold Reels et la sélection habituelle, puis installer par-dessus avec le même package Clone et la même clé de signature. Ne pas désinstaller l'application quotidienne.
