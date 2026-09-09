# 4.1.5

- Corrige le second refus observé sur le vrai Instagram `439.0.0.37.89` après la 4.1.4 : le garde échouait avant même la vérification des opcodes, au niveau du contrat de méthode `dispatchDraw`.
- `RoundedCornerFrameLayout.dispatchDraw` peut maintenant conserver les blocs `try/catch` ajoutés par R8 tant que son chemin normal reste exactement vérifié : `super.dispatchDraw(Canvas)`, chargement du helper, appel avec le même `Canvas`, puis premier `return-void`.
- Le garde n’ignore jamais de travail supplémentaire avant ce premier retour. Seul du code de handler placé après le retour normal peut coexister avec le contrat attendu.
- Les diagnostics d’échec indiquent désormais le nombre de `tryBlocks` et les opcodes observés, afin que toute variante encore inconnue soit exploitable directement depuis Morphe.
- Les vérifications de registres, types, helper et `Canvas.drawPath(Path, Paint)` de la 4.1.4 restent intactes ; aucun bypass générique du dessin natif n’est ajouté.
- Cette version vise d’abord à rendre le patch applicable au véritable APK 439. Le retrait visuel du cadre et le rendu final doivent encore être validés sur le Galaxy Z Fold 8 réel.

# 4.1.4

- Corrige le refus de patchage de la 4.1.3 sur Instagram `439.0.0.37.89` lorsque D8/R8 encode le `dispatchDraw` du `RoundedCornerFrameLayout` avec des formes `/range` ou du padding `nop`.
- Le matcher reste sémantiquement strict : `super.dispatchDraw(Canvas)` doit être conservé, le helper natif doit être chargé depuis l’instance, appelé avec le même `Canvas`, puis retourner sans autre effet.
- Les appels du helper restent limités aux deux `Canvas.drawPath(Path, Paint)` attendus ; les registres et types sont toujours vérifiés avant injection.
- Les erreurs de forme ou de dataflow remontent maintenant les opcodes observés pour faciliter le diagnostic sur APK réel.
- Ajoute deux tests bytecode (variante `invoke-super/range` et padding `nop`) et distribue le hotfix source avec le bundle 4.1.4.
- Cette passe valide la compatibilité du patchage et ne revendique toujours pas un résultat pixel-perfect sur Fold sans test appareil.

# 4.1.3

- Traite le masque de coins et le stroke dessinés après les enfants par `RoundedCornerFrameLayout`, en plus des backgrounds/foregrounds : contrôle strict du bytecode natif lors du patchage ; suppression limitée aux wrappers de players réellement transformés en cover.
- Restauration sans écriture des Paint/radii/helpers natifs, avec invalidation des display lists à l’entrée et à la sortie ; players, enfants et listeners restent natifs.
- Scrims : hauteur de fondu native, ancrage haut/bas et largeur du viewport ; suivi des remplacements et modifications de couleurs natives. Reconnaissance explicite du `ClipsViewerActionBar` observé.
- Diagnostic figé avant les dialogues (corrige le relevé `not-presentable` après cold start), chemins players prioritaires, vues nulles/GONE omises, identités d’instances, compteurs d’exécution et export `.txt`.
- Metadata : refuse les branches social context/facepile et l’identité déduite seulement d’un avatar générique et d’un texte cliquable. Les structures incertaines restent natives.
- Gates attendus : 113 scénarios Android, 5 tests du garde bytecode, 305 assertions JVM, 13 mappings FR/EN et 14 tests de distribution ; build et chargement réels du MPP. Aucun résultat pixel Samsung ni patchage de l’APKM 439 revendiqué sans preuve.

# 4.1.2

* **Instagram:** Repère de dessin fondé sur la fenêtre en cover fullscreen, distinct du contenu Android et des limites tactiles natives.
* **Instagram:** Gradients natifs du haut, du bas et composites de card adaptés au viewport complet, avec le même déplacement que les pages vidéo pendant le swipe.
* **Instagram:** Dessin conservé dans ses couches natives ; frontières de clipping restaurées, aucune superposition sombre ajoutée au-dessus des commandes.
* **Instagram:** Décorations ImageView de géométrie correspondante couvertes ; diagnostic des bounds, foregrounds, couches et ancêtres enrichi sans texte utilisateur.
* **Instagram:** Cold start, player, gestes, profils et URL de source Morphe conservés ; nouveaux contrôles de géométrie et de rasterisation Android simulée.

# 4.1.1

* **Instagram:** Rattrapage du premier dessin et des contextes d’inflation sans Activity, sans recharger le lecteur.
* **Instagram:** Bandeau partagé maintenu au viewport pendant les swipes ; raccourci déplacé sous sa zone tactile et dégradé conservé jusqu’au bord supérieur.
* **Instagram:** Métadonnées des calques frères du player, comptes sans bouton Suivre et captions natives spécialisées pris en charge en mode compact.
* **Instagram:** Bordures arrondies de calques superposés et composites séparées du dégradé avec restauration native.
* **Instagram:** Source Morphe publique conservée ; téléchargement anonyme vérifié après propagation du feed.

# Changelog

## [4.1.0](https://github.com/senor-roboto/PatchInsta/releases/tag/v4.1.0) (2026-09-08)

### Features

* **Instagram:** Presets Plein écran propre et Instagram complet, modes d’actions et métadonnées indépendants par écran.
* **Instagram:** Commentaire seul depuis le rail natif ; avatar, nom, Suivre et caption compacts ; dégradé supérieur reconnu étendu au bord du viewport.
* **Instagram:** Source Morphe durable et versionnée, bundle compilé chargé par Morphe, ZIP et SHA-256 vérifiés.

### Bug Fixes

* **Instagram:** Initialisation depuis un viewer attaché après les callbacks lifecycle ; classification immédiate ; rattachements et chip idempotents.
* **Instagram:** Restauration des états natifs et protection du commentaire, des gradients et des interactions pendant les changements de présentation.
* **Instagram:** Conservation du renderer v4, du précadrage des pages adjacentes et de l’absence de rechargement automatique.

Base amont : Piko 3.9.0, commit 50744aa07bb41c4e1f942a06614ef4e6f2e3610c.
Version de distribution stable ; validation sur Galaxy Z Fold 8 encore nécessaire.
