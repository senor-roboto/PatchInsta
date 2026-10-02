# Candidat PatchInsta 4.1.11

Statut : source candidate, aucune validation physique ni publication.

Base Piko `3.10.0-dev.9`, commit `9813ccd2eb36146b804e6eb0309286089761c9ba`, cible inchangée Instagram `439.0.0.37.89` / arm64 / `384510827`. Cette base est une préversion ; les changements amont de navigation et de préférences nécessitent aussi la validation du candidat complet.

## Changements à vérifier

- Dégradé social natif reconnu : limite latérale élargie malgré sa hauteur supérieure à l’ancien seuil.
- Jauge dans tous les profils remplis : marge aux gestes système, transmission complète au pager des gestes verticaux depuis la zone déplacée ; seeking horizontal conservé.
- Aperçu en pause après changement d’écran : seules les images Instagram sous le parent vidéo identifié et à côté du conteneur vidéo natif sont cadrées. Photos, carrousels et avatars exclus.
- Nouveau profil intérieur rempli avec navigation ; choix antérieurs et profils personnalisés conservés.
- Métadonnées complètes déplacées au-dessus de la jauge en mode rempli, sans compactage du texte ni changement des écouteurs natifs.
- Icône sans fond, cible tactile 48 dp et descriptions maintenues ; raccourci masqué sans cible de cadrage vérifiée.
- Réglage « Masquer Suivre » fourni par Piko ; réglage « Masquer Suivi par » ciblant le renderer natif du texte. Avatars d’amis ayant aimé distincts et conservés.

## Contrôles locaux

- 305 contrôles Java de policy et géométrie réussis.
- 13 mappings exacts et ressources FR/EN vérifiés.
- 24 tests des garde-fous de distribution réussis.
- Application du diff vérifiée sur une copie vierge de la base dev.9.
- 177 scénarios Android déclarés, dont nouveaux cas aperçu, gestes et préférences. Exécution en CI requise : le plugin Morphe ne se résout pas localement.

## Validation restante

Build et suite Android, vérification du bundle, application de la sélection complète à l’APKM original, identité du clone, signature, absence de classes dupliquées et bibliothèques natives conservées. Ensuite une seule passe physique regroupée : deux écrans, pause et pliage/dépliage, commentaires, jauge horizontale/verticale, gestes système, options de visibilité et retour aux profils enregistrés.

La disparition des commentaires en rotation reste non corrigée et d’origine incertaine. Le patch ne recrée pas l’activité lors des changements d’écran ou d’orientation, et ses flags de disposition restent identiques aux deux écrans. Il ne tente pas de rouvrir une feuille native sans son contexte. Ce point doit être isolé et observé sur le candidat ; aucune promesse de correction à ce stade.

Le recadrage marqué des vidéos verticales en paysage est le compromis du remplissage. Le profil Instagram complet et le menu de cadrage restent disponibles. Aucun déplacement arbitraire des commandes, aucune donnée privée ajoutée au kit.

La publication et la fusion restent interdites avant validation physique convaincante. La CI candidate produit uniquement des artefacts.
