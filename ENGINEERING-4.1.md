# Compte rendu technique — PatchInsta 4.1.0

## Référence et portée

Cahier des charges : `PROMPT_GPT6_PATCHINSTA.md`, lu intégralement, puis complément sur le scrim supérieur et le bloc auteur. Les captures sont des observations matérielles fournies par l’utilisateur ; les validations décrites ici sont celles du code et des tests. Aucun APKM, dump structurel du lecteur réel ni appareil Samsung n’est disponible dans cet environnement.

**A — HEAD initial audité :** `3cf4b75e5fbc668469ac81df88320dedadbf84d1`. Audit de son historique récent, de son diff complet, des 14 scénarios Android, des 253 assertions JVM initiales, de la CI, du README et du guide. Lors de la reprise demandée, `main` était à `59c76b30ebf69ed77b1b40f056c3f62538531eb6` : aucune remise à zéro.

Amont conservé : Piko **3.9.0**, `50744aa07bb41c4e1f942a06614ef4e6f2e3610c`. Instagram **439.0.0.37.89**, `com.instagram.android`, APKM arm64-v8a, versionCode **384510827**. Les mappings et le correctif de notification existants restent en place.

## Actions, card, dégradé et métadonnées

**B — Actions visibles : hypothèse confirmée dans le code.** `FoldReelsControls` reconnaissait structurellement un rail comportant plusieurs catégories dont le commentaire, tandis que `FoldReelsChrome` exigeait des préfixes et noms de boutons plus stricts pour les masquer. Un rail pouvait donc être déplacé sans être nettoyé. Les noms exacts de la variante Samsung photographiée ne sont pas déductibles des captures : cette partie demande un diagnostic du vrai lecteur.

**C — Propriétaire unique.** Controls assure désormais découverte, catégories, modes `ALL / COMMENT_ONLY / NONE`, positionnement, routage tactile et restauration. Une fois le rail qualifié, COMMENT_ONLY protège la branche commentaire et son compteur associé, et masque ses frères, y compris anonymes. Les descendants identifiés priment sur un parent trompeusement nommé « share ». Aucun nettoyage générique de l’Activity. `INVISIBLE` évite le relayout ; les états natifs VISIBLE/INVISIBLE/GONE sont restaurés. Un geste actif est annulé avant de masquer son contrôle.

**D — Origine exacte de la card : non établie sur appareil.** Les captures montrent un contour aux anciennes dimensions mais ne donnent ni classe de drawable ni hiérarchie. La v4 ouvrait déjà des clips, mais ne neutralisait pas les formes arrondies et foregrounds de wrappers. Il serait injustifié d’affirmer qu’un flag two-pane ou un drawable particulier est la cause matérielle démontrée.

**E — CardChrome conservateur.** Il inspecte uniquement les wrappers de dimensions compatibles sur le chemin d’une surface connue vers sa page. Il mémorise et neutralise les décorations arrondies inspectables, puis restaure background, foreground et élévation possédés. Les clips restent sous leur propriétaire partagé. L’outlineProvider et l’alpha ne sont pas modifiés. Un drawable composite comprenant un gradient ou une couche inconnue n’est pas supprimé. Si Instagram remplace une propriété entre-temps, la nouvelle valeur native est préservée.

**Complément visuel — Scrim.** Le HEAD de reprise ne repositionnait aucun scrim. Le nouveau composant identifie une feuille décorative supérieure par sa forme de gradient sombre vers transparent, ou par un identifiant structurel supérieur explicite avec drawable. Il conserve le drawable, étend la largeur et le haut vers le viewport réel et conserve sa limite inférieure. Les pages préchargées reçoivent le même décalage normalisé que leurs players. Il ne transforme ni le header interactif ni ses textes. Un gradient inclus dans le background d’un header complexe reste natif : le déplacer sans déplacer les contrôles demanderait une preuve structurelle supplémentaire. Tests dédiés : bord supérieur réel, largeur, 200 frames, voisins pendant le swipe, restauration, détachement et exclusion des contrôles.

**F — Métadonnées.** L’implémentation de reprise limitait encore la caption à sa largeur native et laissait une ligne d’identité trop large à sa position originale. Elle réutilise maintenant trois rôles natifs identifiés — avatar, nom, Suivre — et une caption native. La ligne est dimensionnée depuis l’espace entre la marge gauche de 12 dp et le rail, puis ses rôles sont repositionnés sans reparenting et sans copie de texte. Le nom et la caption utilisent une ligne et l’ellipsis ; les lignes secondaires de l’identité peuvent être masquées. FULL restitue dimensions, translations et contraintes typographiques ; HIDDEN masque les groupes reconnus. Une structure ambiguë reste native.

La caption réserve sa hauteur tactile réellement mesurée pendant le premier relayout, pour ne pas intercepter le clic de l’avatar. La largeur tient compte d’un rail placé dans un wrapper intermédiaire de la même page. Avatar, nom et Suivre restent les vues et listeners Instagram. Leur routage partage le mécanisme déjà testé du commentaire, avec remise du swipe au pager et priorité des panneaux natifs.

**Limite volontaire de placement :** le bloc interactif reste dans le viewer tactile. Si Instagram laisse ce viewer moins haut que la vidéo agrandie sous les anciens onglets, la ligne n’atteint pas le bas physique de l’écran. Étendre arbitrairement le pager ou déplacer des boutons hors de sa frontière tactile compromettrait les priorités de stabilité et d’interaction ; cette version conserve ce retrait et le documente.

**G — UX.** Deux presets cover : Plein écran propre et Instagram complet. Personnaliser expose les trois modes d’actions et de métadonnées, le déplacement, les barres, le décor et le raccourci. Options avancées : zoom, détection, diagnostic, expérience native et rechargement manuel doublement confirmé. Le raccourci conserve une zone de 48 dp. Les anciens choix enregistrés sont migrés ; le preset propre applique tous les nouveaux défauts. Les options cover et inner restent indépendantes.

**H — Expérience sans two-pane.** Variante isolée, figée au lancement du processus : `111584::9`, `::25`, `::27` à false sur les deux écrans. `::10`, `::11`, `::12` et les autres décisions v4 restent inchangés. Les tests de politique comparent chaque clé et chaque profil. L’effet sur la vraie card, les commentaires et le Fold n’a pas été mesuré ; aucune conclusion matérielle favorable n’est revendiquée. La politique v4 demeure donc le défaut. Le choix expérimental prend effet au prochain lancement complet manuel, sans recréation automatique.

## Démarrage et lifecycle

**I — Cause confirmée dans le code.** L’installation enregistrait les callbacks Application sans rattraper l’Activity déjà créée/résumée. `addViewer()` pouvait créer un tracker avec un viewer mais sans observateurs ni activation. Le render exigeait `resumed` et la bonne Activity foreground. L’absence de chip était un symptôme de ce pipeline inactif.

État possible avant correction : `resumed=false`, `observersAttached=false`, foreground absent, un viewer enregistré, WindowKind encore UNKNOWN ou non capturé pour l’Activity, content/chip absents. Le rendu n’atteignait pas la création du raccourci.

**J — Pourquoi un pliage pouvait réparer.** Les callbacks ultérieurs de pause/reprise ou une recréation native pouvaient enfin activer le tracker. Le `onConfigurationChanged()` v4 seul ne créait ni les observateurs ni un état resumed : le code ne permet pas d’attribuer la réparation à ce callback seul sans trace du téléphone.

**K — Bootstrap.** Un viewer attaché peut initialiser les préférences depuis l’Application, créer ses observateurs une fois, capturer immédiatement la configuration et demander un rendu. Tant que l’état resumed est inconnu, le focus et une fenêtre visible permettent le démarrage. Une pause connue reste prioritaire, même avec un focus résiduel. Détachement, destruction, retour arrière, saisie et remplacement du content restaurent les modifications et nettoient les références. Les trackers, viewers, pages et contrôles sont conservés par références faibles. Le changement de cadrage ne modifie ni média, ni position du pager, ni Activity.

Le diagnostic précise raison d’inactivité, resumed connu/inconnu, focus, visibilité, observateurs, WindowKind, content, chip, viewport, surfaces et erreurs par composant. Il n’extrait aucun texte utilisateur, tag, identifiant de média ou URL.

## Tests et livraison

**L / M — Couverture vérifiée :** 60 scénarios Android (14 régressions v4, 14 lifecycle, 23 présentation, 5 scrim, 4 préférences), 305 assertions JVM géométrie/politique, 13 mappings exacts et XML FR/EN, 6 tests des garde-fous de distribution. Zéro test Android ignoré accepté. Le chargement du `.mpp` réel utilise le loader Morphe et vérifie le nom du patch et la cible Instagram.

Les tests de lifecycle utilisent le vrai watcher/presenter, des vues attachées et une Activity créée/résumée avant son installation. Focus et visibilité de fenêtre sont des entrées contrôlées de simulation : Robolectric API 29 signalait GONE malgré une fenêtre déclarée visible. La protection de production est conservée et un scénario vérifie explicitement ce refus. Le compositeur et le décodeur Samsung ne sont pas simulés.

Les nouveaux tests ont trouvé et permis de corriger le chevauchement tactile initial de la caption et la réservation incorrecte de largeur lorsque le rail était dans un wrapper intermédiaire. Les 14 régressions v4 sont conservées. Le rapport JSON publié donne les résultats de la révision compilée ; il ne prétend pas à un test APK ou matériel.

**N — Fichiers.** Le diff cumulatif contient les composants FoldReels, Controls, Chrome, Renderer, Policy, Preferences, Visibility, Metadata, CardChrome, Scrim et Diagnostics, les tests Android/JVM, les ressources FR/EN, le menu Piko, l’identité/version du bundle et le vérificateur de chargement Kotlin. Le kit ajoute `release.json`, `scripts/bundle.py`, `scripts/publish.py`, `scripts/test_distribution.py`, la CI, ce rapport, README, guide, changelog et notes de release. Aucun remplacement global des sources amont.

**O — Historique d’intégration :** `59c76b3` (bootstrap/présentation), `7d9f76b` (scrim et métadonnées), `9c2bf51` (géométrie et tests), `a64b35b` (zones tactiles, lifecycle et chargement réel). Les derniers commits de livraison et la révision exacte du binaire sont traçables dans [l’historique](https://github.com/senor-roboto/PatchInsta/commits/main/) et `build-info.json`.

**P — Version :** 4.1.0 ; nom de source **PatchInsta (Piko, unofficial)** ; nom de patch **Adaptive Fold Reels**. Ce numéro est celui du dérivé distribué, pas une prétendue version Piko amont 4.1.

**Q / R — CI et preuves :** Les 60 scénarios, le build, le chargement des 133 patchs et la préparation des fichiers ont réussi dans le [run 34215073093](https://github.com/senor-roboto/PatchInsta/actions/runs/34215073093), avant correction de la récupération du brouillon de Release. Le run de publication définitif est enregistré dans les informations de compilation.  [workflow](https://github.com/senor-roboto/PatchInsta/actions/workflows/build-fold-reels.yml). `build-info.json` donne le run et le commit exacts ; `test-results.json` donne le décompte vérifié. La phase de build ne possède pas de droit d’écriture GitHub ; la phase de publication utilise le jeton normal du workflow après les tests. Elle relit les assets téléchargés, les compare aux sommes attendues, publie la Release puis avance le feed sans force-push. Un déplacement concurrent de main ou une version non incrémentée bloque une publication incohérente.

| Référence | Livrable / URL durable |
|---|---|
| S | [Release 4.1.0](https://github.com/senor-roboto/PatchInsta/releases/tag/v4.1.0) |
| T | [PatchInsta-4.1.0.zip](https://github.com/senor-roboto/PatchInsta/releases/download/v4.1.0/PatchInsta-4.1.0.zip) |
| U | [PatchInsta-4.1.0.mpp](https://github.com/senor-roboto/PatchInsta/releases/download/v4.1.0/PatchInsta-4.1.0.mpp) |
| V | [SHA256SUMS.txt](https://github.com/senor-roboto/PatchInsta/releases/download/v4.1.0/SHA256SUMS.txt) et hash du MPP dans build-info.json |
| W | [patches-bundle.json](https://raw.githubusercontent.com/senor-roboto/PatchInsta/main/patches-bundle.json) |
| X | `https://github.com/senor-roboto/PatchInsta` à ajouter comme source distante |
| Y | [Deep link officiel](https://morphe.software/add-source?github=senor-roboto%2FPatchInsta) |

**Z — Mise à jour.** Une migration initiale des sources locales v3/v4 vers la source distante est nécessaire. Ensuite, conserver le même endpoint et la même source ; actualiser le bundle, repatcher l’APKM original, installer par-dessus avec le même package Clone et le même keystore exporté. Morphe compare la version du bundle et utilise le changelog pour les applications suivies. Les entrées conventionnelles `**Instagram:**` sont conservées pour que la modification soit attribuée à Instagram. Le badge n’est pas une installation automatique de l’APK.

Format du feed vérifié dans les [sources officielles Manager](https://github.com/MorpheApp/morphe-manager/blob/main/app/src/main/java/app/morphe/manager/network/dto/MorpheAsset.kt) et le [template officiel](https://github.com/MorpheApp/morphe-patches-template) : version, created_at (LocalDateTime sans Z), description, download_url, signature_download_url nullable, page_url optionnel. Le lien GitHub est normalisé vers le JSON sur main. Cette itération utilise une seule branche stable ; pas de multiplication de sources v5/v6.

**AA — Limites et accès.** L’accès authentifié GitHub ne rend pas une source privée utilisable par Morphe. Le rapport de publication distingue explicitement le téléchargement authentifié et l’accès anonyme ; le dépôt doit être public pour le flux distant. La connexion GitHub de cette session ne fournit pas d’opération d’administration permettant de changer sa visibilité. Les assets et le feed sont préparés pour cette dernière condition.

Sur appareil restent à confirmer : rendu SurfaceView/TextureView Samsung à 80–120 Hz, identité de la card et des scrims composites, variantes obfusquées de métadonnées, exactitude des cibles tactiles matérielles, entrée/sortie des panneaux et conservation du Réel si Instagram ou Android décident eux-mêmes de recréer l’écran. Aucun rechargement automatique n’a été ajouté pour masquer ces limites.
