# PatchInsta 4.1.2 — géométrie du contraste plein écran

## Point de départ et preuves

HEAD réellement relu : `9b3046e807d53ed412b07c52e82d41c62b706c1d`, dernière Release 4.1.1. Le blob du patch local et distant correspondait : `99b8f258e976f74e1b0544214721b1abd6bd1120`. Piko reste épinglé à `50744aa07bb41c4e1f942a06614ef4e6f2e3610c`. Aucune reconstruction du projet depuis zéro.

Les deux nouvelles captures, dont celle annotée, montrent une vidéo étendue et des discontinuités de contraste aux anciennes limites centrées. À la résolution fournie de 972 × 1536, elles sont approximativement à x=115/855, y=103/1416, avec une autre transition horizontale vers y=1430. Ces coordonnées sont des observations visuelles, pas des IDs de vues. Aucun texte, compte, média ni copie des captures n’est publié ici.

**Attribution des traits : non démontrée pour l’appareil.** Il n’y a ni diagnostic de hiérarchie 4.1.1 joint ni APKM disponible dans cet environnement. Il serait incorrect d’affirmer qu’un trait donné est un `GradientDrawable`, un foreground ou une ombre Samsung. Le code confirme plusieurs mécanismes capables de laisser cette géométrie visible ; les tests reproduisent ces mécanismes indépendamment de la capture.

## Causes confirmées dans la 4.1.1

1. `FoldReels.render()` élargissait le viewer au `getGlobalVisibleRect(android.R.id.content)`. Ce rectangle appartient au contenu visible et peut conserver des insets/layouts natifs. Masquer les barres système ne garantit pas sa coïncidence avec le rectangle de la fenêtre. Le code n’avait pas de repère explicite de fenêtre pour le dessin full-bleed. Sa frontière de clipping s’arrêtait aussi avant ce contenu : augmenter un target ne débloquait pas cette dernière frontière.
2. `FoldReelsScrim` n’acceptait que les gradients supérieurs, limités à 45 % de la hauteur du viewer. Aucun traitement symétrique n’ancrant un gradient inférieur au bord bas n’existait.
3. `FoldReelsCardChrome.withoutBorder()` conservait les gradients des composites, mais ceux-ci continuaient à être dessinés aux dimensions de leur ancienne card. Retirer un stroke ne suffit donc pas : le changement de luminance au bord du gradient peut encore dessiner un rectangle. Les grandes décorations étaient exclues du Scrim par son seuil de hauteur.
4. Scrim inspectait essentiellement les backgrounds, et les `ImageView` sans background, alors que le contraste peut être un foreground. CardChrome n’inspectait pas `ImageView.getDrawable()` pour les feuilles décoratives correspondantes. Ces absences sont vérifiables ; leur présence exacte dans le layout Samsung reste à relever.
5. Les gradients de calques frères n’utilisaient pas la portée de présentation ajoutée en 4.1.1. Leur association à la page pouvait donc différer de celle du player pendant un swipe. Le wrapper de background ne publiait pas non plus de région d’invalidation étendue.

Les limites haut/bas du rendu observé sont compatibles avec ces anciens rectangles de dessin/clipping. La hauteur exacte de chaque limite sur le Fold n’est pas attribuée à une vue faute de dump ; cette distinction reste explicite dans ce rapport.

## Architecture retenue

Le renderer vidéo, ses ancrages, son précadrage multi-surface et ses listeners ne sont pas réécrits. Aucun changement des MobileConfig ni nouvelle recréation d’Activity.

`FoldReelsViewport` calcule à chaque frame trois repères globaux : fenêtre attachée et mesurée, contenu Android, viewer natif. Il en déduit le viewport visuel et l’intersection interactive. La fenêtre vient du DecorView de l’Activity, jamais des dimensions physiques du Display : le calcul respecte une fenêtre réduite ou déplacée. En cover crop immersif, le dessin peut remonter au sommet de cette fenêtre. Son bas n’englobe les onglets Instagram que lorsqu’ils sont effectivement masqués. Sans immersion, le contenu reste la limite d’extension ; en fit/interne, le viewer reste la référence.

Controls et Metadata reçoivent séparément le viewport visuel pour le déplacement des pages et le rectangle interactif pour le placement des vues natives. Un footer peut rester au-dessus du bord physique lorsque le viewer s’y arrête : sa hitbox reste utilisable. Le contraste non interactif peut, lui, descendre au bord de la fenêtre. Le header conserve son espace tactile ; ce sont ses pixels de background qui s’étendent.

Scrim généralise le traitement existant aux gradients haut, bas et de pleine card, aux backgrounds/foregrounds/images et aux portées de présentation des pages. Les feuilles décoratives simples gardent la transformation légère existante. Les conteneurs interactifs ne sont pas agrandis : un wrapper dessine une copie privée du drawable dans le rectangle global transformé en coordonnées locales. Il reste dans la couche native, avant/après les enfants selon son rôle initial. **Aucun overlay sombre supplémentaire n’est ajouté.** Les couleurs, l’orientation et les couches de contraste sont conservées. Les bords/arrondis des composites inspectables sont adaptés avec le réglage de nettoyage de card.

CardChrome laisse les composites de contraste à cet unique propriétaire : les deux composants ne se superposent pas des wrappers. Il continue à traiter les décorations arrondies simples et les feuilles correspondantes non interactives, avec prise en charge de l’image d’une ImageView. Aucune suppression générale de drawables inconnus, aucun recours à des champs privés ou au texte des vues.

Le clipping est ouvert, sous bail par frame, jusqu’à la frontière visuelle incluse. Les LayoutParams, insets listeners et dimensions des conteneurs ne sont pas changés pour gagner des pixels. Les propriétés reviennent lors du retour au profil natif, de l’arrêt de présentation, du détachement ou d’une erreur. Les remplacements de drawable/translation natifs sont respectés. Les ombres des grandes cards de contraste reconnues sont elles aussi temporaires. Les drawables originaux, leurs bounds et ConstantStates ne sont pas modifiés.

Chaque décoration conserve l’ancre du player associé et l’espacement normalisé sur la hauteur visuelle. Un composite de card occupe la page visuelle entière ; les scrims d’extrémité gardent leur transition vers la zone utile. Le dessin est borné à cette page, afin que deux scrims de Réels adjacents ne se superposent pas pendant un swipe.

## Diagnostic et protection des données

Le diagnostic décrit maintenant les espaces fenêtre/contenu/viewer/visuel/interactif, les sources et targets des scrims, leur ancre, les background/foreground/image, les bounds/dirty bounds et couches publiques de drawable. Il ajoute les ancêtres du viewer et les racines de leurs frères sans parcourir les sous-arbres des autres onglets.

Il ne lit pas les textes, usernames, captions, URLs, tags, descriptions d’accessibilité ni pixels des médias. La largeur du stroke n’étant pas exposée par l’API 29, elle est indiquée comme indisponible ; aucun champ privé n’est inspecté. Les contrôles de dessin emploient des couleurs/formes synthétiques.

## Fichiers principaux

- `FoldReelsViewport.java` (nouveau) : repères de géométrie.
- `FoldReels.java`, `FoldReelsControls.java`, `FoldReelsMetadata.java` : passage explicite des espaces, invariants interactifs.
- `FoldReelsScrim.java`, `FoldReelsContrast.java` (nouveau), `FoldReelsCardChrome.java` : dessin natif, rôle haut/bas/composite, propriétaire unique.
- `FoldReelsClipping.java`, `FoldReelsDiagnostics.java` : frontière visuelle et preuves structurelles.
- Tests `FoldReelsViewportTest`, `FoldReelsDrawingTest` (nouveaux), Lifecycle/Presentation/Update adaptés.
- `release.json`, `gradle.properties`, gate `scripts/bundle.py`, documentation et description du feed mis à jour. L’identité et l’URL Morphe restent identiques.

## Gates et résultat de publication

Avant publication, la CI exige 98 scénarios Android : runtime 14, lifecycle 19, présentation 23, scrim 5, préférences 4, régressions 4.1.1 13, viewport 16, dessin 4. Aucun test ignoré ou en échec n’est accepté. Les 305 assertions JVM, 13 mappings et XML FR/EN ainsi que les 14 tests de distribution restent exigés.

Les tests nouveaux couvrent : contenu en retrait, fenêtre redimensionnée/déplacée, fallback sans fenêtre, barres visibles, mode interne/fit, scrim bas, foreground de card, déplacement/rediscovery de pages adjacentes, calque frère, changement natif de drawable, détachement, choix de nettoyage, conservation des clics/couches, bordure ImageView et frontière de clipping. La suite de dessin utilise Canvas/Skia de Robolectric pour vérifier le dessin hors de l’ancien cadre, la conservation d’un bouton vert natif, l’absence de jointure de card dans la fixture, les pages adjacentes et l’invalidation/copie privée.

La CI compile réellement le `.mpp`, charge les patchs avec Morphe, vérifie le manifeste et l’extension DEX puis le ZIP et les checksums. La publication n’a lieu qu’après réussite, sur la source existante ; les assets sont téléchargés et vérifiés à nouveau, puis l’URL anonyme stable et le MPP sont relus.

**Statut au commit de préparation : en attente de CI et de publication.** Les preuves et URLs exactes seront consignées après exécution. Les tests locaux JVM/mappings/distribution sont verts ; aucun build Android local n’est revendiqué.

## Vérification matérielle restante

Robolectric ne valide ni les pixels Samsung/HWUI exacts, ni la structure obfusquée d’Instagram 439, ni son décodeur. Après mise à jour, vérifier le cold start, les extrémités de gradient et le rectangle pendant plusieurs swipes, les commentaires/caption/avatar/Suivre, puis fold/unfold et les deux orientations internes. Aucun refresh ne doit être nécessaire pour ces changements.

Si un trait reste visible, copier « Diagnostic du lecteur » depuis le menu Cadrage Fold avec le profil cover actif et joindre le texte structurel et une capture correspondante. Cela permettra une attribution de vue/drawable vérifiable, au lieu d’ajouter un filtre de suppression fondé sur l’apparence seule.

Références primaires : [Android View](https://developer.android.com/reference/android/view/View), [Drawable et dirty bounds](https://developer.android.com/reference/android/graphics/drawable/Drawable), [ViewOverlay et son ordre de dessin](https://developer.android.com/reference/android/view/ViewOverlay), [template Morphe](https://github.com/MorpheApp/morphe-patches-template). Ces contrats n’établissent pas l’identité des objets dans les captures Instagram.
