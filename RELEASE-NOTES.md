# 4.1.4

- Corrige le refus de patchage 4.1.3 sur Instagram 439.0.0.37.89 lorsque D8/R8 encode `RoundedCornerFrameLayout.dispatchDraw` avec les variantes d’instructions `/range` ou du padding `nop`.
- Le garde reste strict : il exige toujours `super.dispatchDraw(Canvas)`, le chargement du helper natif, l’appel du helper avec le même `Canvas`, puis `return-void`; aucun bypass aveugle n’est accepté.
- Les registres, le type du helper et son contrat de dessin `Canvas.drawPath(Path, Paint)` restent vérifiés avant injection.
- Le message d’échec inclut désormais les opcodes observés si la forme réelle diffère encore, afin d’obtenir un diagnostic exploitable au lieu d’un refus générique.
- Deux tests bytecode supplémentaires couvrent `invoke-super/range` et le padding `nop`; le bundle de distribution inclut explicitement le hotfix appliqué en plus du patch source principal.
- Cette version corrige d’abord la compatibilité du patchage. Le résultat visuel du retrait du cadre natif doit toujours être validé sur le Galaxy Z Fold 8 réel.

Mettre à jour la même source Morphe, repatcher l’APKM original 439.0.0.37.89 arm64-v8a et installer avec le même package et la même signature.
