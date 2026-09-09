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
