# PatchInsta 4.1.10

- Étend le preset Plein écran propre à l’écran interne, avec mémoire indépendante par écran. Le correctif de cadre de la 4.1.9 externe, apprécié par l’utilisateur, est conservé ; vidéo centrée sans étirement et dégradé natif sur toute la largeur.
- Remplace le bouton textuel par une icône plein écran de 48 dp. Tap bref : bascule temporaire du preset complet ; appui long : menu Cadrage Fold. Défauts initiaux : propre sur l’écran externe, Instagram complet sur l’interne. Deux réglages permettent de choisir ces défauts indépendamment ; les choix déjà enregistrés sont conservés.
- Conserve l’état réel de l’activité entre les sorties et réouvertures du lecteur pour réactiver le nettoyage après l’accueil ou les MP. Pliage, orientation et pause/restauration restent sans rechargement automatique.
- Déplace la jauge native au bas du vrai viewport. Seeking horizontal natif, retour des swipes verticaux au lecteur et priorité aux commentaires ; les pixels découpés des vidéos voisines ne bloquent plus la jauge.
- Masque la barre latérale interne reconnue en mode propre et place la légende au-dessus de la jauge. La découpe suit la première ligne entière, même lorsque Instagram déplace son texte vers le haut.
- Validation automatique et application au véritable APKM Instagram 439 documentées dans VALIDATION-4.1.10.md. Les résultats physiques et leurs limites sont consignés séparément.

Dans Morphe, actualiser la source PatchInsta existante, repatcher l’APKM original Instagram 439.0.0.37.89 avec Adaptive Fold Reels et la sélection habituelle, puis installer par-dessus avec le même package Clone et la même clé de signature.
