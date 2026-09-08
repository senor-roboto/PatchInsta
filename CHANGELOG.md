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
