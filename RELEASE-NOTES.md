# 4.1.3

- Traite le masque de coins et le stroke dessinés après les enfants par `RoundedCornerFrameLayout`, en plus des backgrounds/foregrounds : contrôle strict du bytecode natif lors du patchage ; suppression limitée aux wrappers de players réellement transformés en cover.
- Restauration sans écriture des Paint/radii/helpers natifs, avec invalidation des display lists à l’entrée et à la sortie ; players, enfants et listeners restent natifs.
- Scrims : hauteur de fondu native, ancrage haut/bas et largeur du viewport ; suivi des remplacements et modifications de couleurs natives. Reconnaissance explicite du `ClipsViewerActionBar` observé.
- Diagnostic figé avant les dialogues (corrige le relevé `not-presentable` après cold start), chemins players prioritaires, vues nulles/GONE omises, identités d’instances, compteurs d’exécution et export `.txt`.
- Metadata : refuse les branches social context/facepile et l’identité déduite seulement d’un avatar générique et d’un texte cliquable. Les structures incertaines restent natives.
- Gates attendus : 113 scénarios Android, 5 tests du garde bytecode, 305 assertions JVM, 13 mappings FR/EN et 14 tests de distribution ; build et chargement réels du MPP. Aucun résultat pixel Samsung ni patchage de l’APKM 439 revendiqué sans preuve.


Mettre à jour la même source Morphe, repatcher l’APKM original compatible et installer avec le même package et la même signature.
