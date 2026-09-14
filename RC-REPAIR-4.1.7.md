> Mise à jour du 14 septembre : l'APKM original a été joint à nouveau. Les 60 patches et la reconstruction de l'APK ont réussi. Voir `APK-VALIDATION-4.1.7.json`. Les mentions de blocage ci-dessous décrivent l'étape précédente, désormais résolue.

# Correction du candidat aacfbab — remplacement de méthode

Base exacte : `aacfbab503e7ecd55cdd8fa634d65af98965ad2c`,
MPP SHA-256 `4196525bf8db1ab225f66e933f01dd563cd16f9b5c8fee6e18cd1efd448441da`.

## Cause prouvée

Le `javap -c -l -p` du MPP RC associe la ligne Kotlin 140 à l'adresse JVM 846.
Ce bloc teste le résultat du `single` sur `rounded.methods` puis construit
`NoSuchElementException` à 851. Le prédicat compare le nom (764–777), les listes
`parameterTypes` (780–793), puis le retour (796–809). L'installation du garde
s'était déjà terminée à 702. La trace n'est donc pas celle du matcher.

Une reproduction locale avec les classes de Morphe Patcher **1.14.0-dev.1** donne :

```
originalParameter=java.lang.String
replacementParameter=com.android.tools.smali.dexlib2.immutable.ImmutableMethodParameter
rawListEquals=false
```

`MutableMethod` conserve la représentation des types de son entrée. La méthode
issue du DEX utilise des chaînes ; `ImmutableMethod.getParameterTypes()` expose
ses paramètres, qui sont des CharSequence. L'égalité de listes depuis les chaînes
échoue malgré les mêmes descripteurs. Les premiers tests vérifiaient la construction
du garde mais pas sa réinsertion dans une vraie collection MutableClass issue d'un DEX.

## Correction

`replaceRoundedCardEntryBypass` conserve `plan.method` par identité. Il construit
la nouvelle méthode avant mutation, vérifie la déclaration par descripteurs textuels,
puis remplace exactement cette référence. Les collections `methods` et `virtualMethods`
sont synchronisées : Morphe peut avoir déjà initialisé son cache des méthodes virtuelles.
Une incohérence est rejetée avec diagnostic avant mutation ; une erreur d'insertion
restaure les collections et est propagée. Aucun catch-and-ignore, nouveau fingerprint,
changement du matcher natif, ni désactivation de Fold.

`AdaptiveFoldReelsPatch` utilise ce commit unique. `AuditFoldApk` exerce désormais
ce même chemin MutableClass, au lieu de reconstruire indépendamment une classe immutable.

Deux tests ajoutés : DEX → MutableClass → reproduction du prédicat RC invalide →
remplacement avec cache virtualMethods déjà lu → écriture/relecture du DEX ;
rejet d'un cache incohérent sans modifier la méthode originale. Le cas original 439
et les 19 autres tests du RC sont conservés : total 22.

## Limite de cette reprise

Les APK/APKM précédemment fournis ne sont plus présents dans l'espace de travail
restauré du 14 septembre. Le précédent essai local sur l'original atteignait exactement
la même seconde exception que le test appareil. Cette reprise ne peut pas prétendre
avoir terminé les 60 patches tant que l'original n'est pas joint à nouveau.
Aucune validation ART, installation, lancement ou pixel Samsung n'est revendiquée.
La source stable Morphe reste inchangée ; le nouveau bundle reste un candidat.

## Résultats exécutés

- CI `34807087967`, commit `ca8c246` : compilation réelle, 22 tests bytecode,
  113 scénarios Android, 305 checks JVM, 13 mappings/XML, 14 tests distribution,
  chargement du bundle et quatre prototypes des hooks compilés : succès.
- MPP téléchargé depuis la release candidate, SHA-256
  `42ab063e3a7ee4a6bc0b1cbb9bb4302a99f38cb7a2a0d9e56faa2ea00e650850`.
- Reproduction locale avec Java 21 et Morphe Patcher 1.14.0-dev.1 :
  `identityReplacementAndDexRoundtrip=PASS` après reproduction de l'ancien prédicat.
- Commande CLI `list-patches --patches PatchInsta-4.1.7.mpp -f com.instagram.android` :
  succès, Fold et Clone présents.
- `git apply --check` du patch cumulatif sur Piko épinglé ; diff de réparation
  applicable au RC exact, empreinte du source RC vérifiée.
- Aucune exécution actuelle des 60 patches : l'APKM original manque dans cette reprise.
  Cette absence ne constitue ni une réussite de patchage, ni un nouvel échec du patch.

Candidat : https://github.com/senor-roboto/PatchInsta/releases/tag/v4.1.7-rc-ca8c246
CI : https://github.com/senor-roboto/PatchInsta/actions/runs/34807087967
Diff complet des changements de code du kit : `PatchInsta-RC-aacfbab-repair.diff`.
