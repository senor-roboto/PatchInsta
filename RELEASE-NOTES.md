# 4.1.5

- Corrige le second refus de patchage observé sur Instagram 439.0.0.37.89 après la 4.1.4 : le garde échouait avant la vérification détaillée des opcodes.
- `RoundedCornerFrameLayout.dispatchDraw` peut désormais conserver les métadonnées/blocs `try/catch` de R8 tant que son chemin normal reste exactement `super.dispatchDraw(Canvas)` → chargement du helper → appel avec le même `Canvas` → premier `return-void`.
- Aucun travail supplémentaire n’est toléré avant ce premier retour ; les contrôles de registres, types et `Canvas.drawPath(Path, Paint)` restent inchangés.
- Les messages d’échec incluent maintenant `tryBlocks` et les opcodes observés, afin qu’une éventuelle troisième variante soit immédiatement exploitable.
- Le bundle distribue les deux hotfixes source appliqués au patch principal et conserve les mêmes gates de build/MPP/Morphe.
- Cette version corrige la compatibilité de patchage. Le résultat visuel du retrait du cadre natif doit encore être confirmé sur le Galaxy Z Fold 8 réel.

Mettre à jour la même source Morphe, repatcher l’APKM original 439.0.0.37.89 arm64-v8a et installer avec le même package et la même signature.
