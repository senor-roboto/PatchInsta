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

## Ajustements après la première passe physique du 3 octobre

Le cycle direct de pliage et réouverture a conservé la vidéo, sa frame et la pause, avec retour des deux profils. Ce cas avait encore une TextureView ; il ne valide pas la transition rare sans décodeur. Les options Suivre et Suivi par persistent après cold start ; Suivre réapparaît après désactivation. Le retour du texte Suivi par sur un même média reste à vérifier.

Le haut du viewport était à y110 et l’action bar native à y132,5 : la marge ajoutée de 8 dp déplaçait également son ShapeDrawable de contraste. L’action bar reconnue est maintenant alignée sur le haut sûr du viewport, en conservant son fond et son espacement interne natifs. Un test de rasterisation vérifie le contraste au premier pixel utile, le bouton et la restitution de l’animation native.

Un swipe descendant de 116 px depuis la jauge à y2294 jusqu’à y2410 a activé le mode Samsung à une main. Son extrémité entrait dans la zone des gestes système ; un point de départ sûr ne suffisait pas. La marge réserve désormais 48 dp de déplacement descendant sous la zone tactile de 48 dp, avec les insets obligatoires. Cela ne prétend pas neutraliser les gestes traversant volontairement la zone système. La préférence Samsung reste activée. Retest physique indispensable.

Le diagnostic porte désormais la version 4.1.11 et rapporte aussi la présence de la jauge native et la géométrie de sa zone tactile. Sur un autre média après cold start, la jauge était absente même en disposition native : ce cas n’est pas une preuve de disparition causée par le recadrage.

Cette révision déclare 179 scénarios Android. Les captures de la première passe concernent l’ancien APK ; CI, nouveau MPP, nouvel APK et validation ciblée de ces ajustements restent requis. Aucun artefact privé du téléphone n’est inclus dans le kit.

## Reprise scroll stable — source 5c0cba13

Nouvelle demande utilisateur enregistrée dans le plan racine. Publication toujours bloquée : les 179 tests de l'ancien candidat ne valident pas ces nouvelles corrections. Téléphone actuellement autorisé uniquement fermé, écran externe.

Causes de calcul établies en source : seuil de restauration des scrubbers à 45 % ; limite metadata tirée d'une barre déjà déplacée puis déplacement ajouté de nouveau ; déplacement du gradient monté ajouté deux fois ; proxy tactile demandant un layout par frame ; possibilité de UP distant sans MOVE traité comme tap. Corrections : toutes les barres préparées, réservation commune stationnaire, gradient corrigé, translation du proxy et contrôle du UP. Cible 48 dp + trajet descendant 48 dp protégés par les insets Android, barre fine centrée plus bas dans cette zone.

Pipeline natif : mesure ciblée du ViewPager2 Reels selon la hauteur de viewport, avant premier dessin via pre-draw annulé seulement pendant sa mesure native, garde borné en cas de hook manquant. Aucun adapter, moteur de scroll ou animation remplacé. Reconnaissance de son RecyclerView interne obfusqué par parent ViewPager2. Réparation de montage de voisin tardif au dispatchDraw via signature structurelle ; aucun délai de 400 ms nécessaire pour ce cas.

PC : 305 policy/géométrie, 13 mappings, 24 gardes distribution réussis. Nouvelle suite attendue : 189 scénarios Android ; CI pas encore exécutée. Tests nouveaux couvrent mesure réelle synthétique, premier dessin retardé jusqu'au layout natif, mêmes transforms/clips aux fractions 10/30/50/70/90 et retour dans les deux sens, voisinage, autres pagers/photos, resize et restauration, limite metadata stable, gradient monté stable, montage tardif et UP distant.

Limites : origine du rectangle sombre central encore non prouvée, notamment piste foreground clips_pause_and_mute_component/X.01Qh. Aucun résultat visuel/physique annoncé pour ce nouveau code. CI/APK et vrais gestes externes à faire ; gates intérieurs/paysage et poster-only restent ouverts. L'ancien APK9fe8 reste installé Lab, temporaire externe clean testé puis rendu natif initial restauré.

### Itération suivante — pause native et pivot frais

CI37138442265 sur f80434fd : 187/189 scénarios passent, deux jauges fraîches décalées horizontalement. Cause : lecture du pivot implicite avant évaluation de la matrice Android ; corrigé en évaluant getMatrix avant la capture et en fixant explicitement le pivot de la jauge. Aucun test affaibli.

Fond de pause natif 439 : clips_pause_and_mute_component, deux rôles pause/mute et foreground X.01Qh. Le type a été vérifié dans le base.apk original : ColorDrawable sans draw personnalisé. Remappage ciblé du draw et dirty bounds de ce foreground vers la zone vidéo de sa carte, conservant instance native, callback, alpha/couleur/animations et positions des contrôles. Ce rôle a des anciennes dimensions observées ; son attribution au rectangle intérieur signalé reste à confirmer physiquement. Cinq tests raster/restauration/couleur/native-rebind/stabilité ajoutés ; suite attendue194.

Pour les essais externes, enregistrement géométrique opt-in uniquement Lab via broadcast protégé android.permission.DUMP (shell), tampon borné de1200 états distincts, dump sur thread secondaire. Inactif par défaut, aucun receiver dans Piko normal. Aucun texte/compte/média enregistré. Permet de comparer les transforms locaux et clips réellement appliqués pendant les swipes, en complément du screenrecord privé. Vérification physique de ce nouveau candidat encore entièrement à faire.
