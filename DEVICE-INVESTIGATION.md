# Défaut cover encore ouvert après 4.1.2

## Conclusion de la comparaison sur appareil

HEAD audité : `75ba8f78651714509e49298f2f0c6d931a46b8e7`. Source compilée : `5bbdd8de6f767ebf0d72d43648287cc12b27c22b`. Le patch local est identique au blob distant `a5b3039d04da78ec707ffef9f561f8682f9deca6`.

Les captures fournies après publication constituent un échec du critère visuel principal : **la 4.1.2 n’a pas démontré la disparition de l’ancienne card sur le vrai Fold 8**. La validation technique du bundle reste valable, mais elle ne valide pas l’attribution des objets de rendu d’Instagram.

Sur la paire de captures cover du même Réel, 972 × 1536, les repères persistants sont les suivants (lecture visuelle corroborée par les discontinuités de luminance ; incertitude de quelques pixels liée à la compression et au contenu en mouvement) :

| Élément visible | Première capture de la paire | Seconde capture de la paire | Conclusion |
|---|---|---|---|
| Limite gauche de la card | x ≈ 124–126 | x ≈ 123–125 | Pas de déplacement utile |
| Limite droite | x ≈ 845–847 | x ≈ 846–848 | Pas de déplacement utile |
| Limite supérieure | y ≈ 98 | y ≈ 98 | Ancien retrait conservé |
| Limite basse / progression | y ≈ 1382 | y ≈ 1382 | Ancienne largeur/hauteur conservées |
| Ligne horizontale plus basse | y ≈ 1396 | y ≈ 1396 | Persistante |
| Bandeau et chip | mêmes retraits apparents | mêmes retraits apparents | Pas d’amélioration visible établie |

Le rectangle mesure environ 722 × 1284, proche de 9:16. **Ce rapport ne permet pas d’identifier sa View ou son drawable.** Les versions ne sont pas inscrites dans les fichiers ; l’attribution 4.1.1/4.1.2 repose sur le retour utilisateur. Le Réel se trouve à deux instants différents : une différence globale de pixels ou un score SSIM ne mesurerait pas l’amélioration de l’interface.

L’autre capture cover montre un bloc de contexte social distinct sous la caption et une disposition basse qui reste liée à l’ancien cadre. La capture interne montre également un contour fin ; elle ne justifie pas d’appliquer un nettoyage cover à l’écran interne. Aucun texte, identifiant de compte ou média n’est reproduit dans ce dossier.

## Ce qui est réellement identifié, et ce qui ne l’est pas

| Objet recherché | Objet natif exact connu ? | Preuve actuellement disponible |
|---|---|---|
| Traits gauche/droite et rectangle fantôme | Non | Pixels et mêmes repères dans les deux captures |
| Trait supérieur | Non | Discontinuité près de y=98 |
| Trait bas et barre de progression | Non | Deux limites distinctes ; il faut conserver la progression native si elle est interactive |
| Top scrim | Non | Son aspect est visible, aucun ID/classe associé |
| Bottom scrim éventuel | Non | Un changement de contraste ne prouve pas l’existence d’une vue séparée |
| Fonds / overlays des metadata | Non | Présentation et contexte social visibles, aucune hiérarchie jointe |

Le seul point d’entrée natif précisément connu dans le patch reste `instagram.features.clips.viewer.ui.ClipsSwipeRefreshLayout`, ciblé par les hooks. Ce nom **n’identifie pas** les objets qui dessinent les traits.

## Résultat de la relecture du code

- La 4.1.2 corrige les coordonnées pour les objets que son détecteur reconnaît ; elle n’instrumente pas l’Instagram réel pour prouver que ces objets sont les auteurs des traits. Le renderer reconnaît au moins un player pour afficher l’action « Entière », mais cela ne prouve rien sur `card`, `scrim` ou `metadata`.
- `FoldReelsContrast` accepte des formes publiques inspectables bien déterminées. Un drawable personnalisé, un dessin dans `onDraw`/`dispatchDraw`, une décoration de liste ou un ViewGroup frère non parcouru peuvent ne pas être couverts. Leur présence sur le Fold reste à démontrer ; ce ne sont pas des causes attribuées aux captures.
- CardChrome/Scrim enregistrent un état appliqué et savent le restaurer. Le diagnostic actuel n’est qu’un instantané : il ne constitue pas une trace avant/après le dessin d’Instagram et ne permet pas, seul, de prouver qu’une propriété n’a jamais été réécrite entre deux phases.
- **Point de prudence pour le diagnostic :** il est ouvert depuis un dialogue de réglages. Celui-ci peut retirer le focus et modifier les barres système. Si l’installation est tardive et que le lifecycle est encore inconnu, la perte de focus peut aussi arrêter la présentation et vider ses candidats. Un relevé avec `not-presentable`, `active=false` ou des compteurs nuls ne sera pas interprété automatiquement comme un échec de détection sur le Réel plein écran. Il faudra alors capturer avant ouverture du dialogue avec une instrumentation dédiée.
- La 4.1.2 redimensionne verticalement certains gradients (`sy` ou scale du drawable). Elle conserve les couleurs et orientations mais **ne garantit pas une distance de falloff native inchangée**. Les tests de bord/extension existants ne vérifient pas ce nouveau critère. La prochaine correction devra distinguer ancrage d’un scrim et changement de son profil, après identification du dessin natif.
- Metadata reconnaît encore une identité sans Suivre lorsqu’un avatar/profile et un texte cliquable corroborent la structure. Cela ne suffit pas à exclure toutes les variantes de contexte social. Les extras ne sont masqués que dans la branche d’identité reconnue ; les branches sociales/audio séparées ne sont pas automatiquement classées. Il faut leurs vrais IDs/parents avant d’en faire une suppression ciblée.

**Pourquoi la 4.1.2 paraît inchangée : non déterminé sur appareil.** Les causes possibles proposées par l’utilisateur ne sont pas encore départagées. Affirmer « mauvais viewport », « mauvais drawable » ou « Instagram écrase les propriétés » comme cause racine serait prématuré.

## Donnée nécessaire pour poursuivre sans une nouvelle correction à l’aveugle

La 4.1.2 installée possède déjà un export structurel : appui long sur **Entière / Remplir** → **Diagnostic du lecteur** → **Copier**. Envoyer le texte complet, de préférence en fichier texte. L’export n’inclut pas les captions, noms de compte, médias, tags ni descriptions d’accessibilité.

Premier relevé : écran externe, mode Plein écran propre, sur un Réel où le rectangle est visible, sans recharger le lecteur. Deuxième relevé : fermer les dialogues, faire un swipe normal, rouvrir le diagnostic. Conserver les en-têtes `tracker`, `profile`, `spaces`, `renderer`, `card`, `scrim`, `header`, `metadata`, `failures` et la hiérarchie.

Ce relevé doit d’abord permettre de relier les limites à des objets concrets et de savoir si les détecteurs ont des candidats. Si les compteurs sont effacés par le dialogue, si la hiérarchie est tronquée avant les vues concernées, ou si un dessin personnalisé est impliqué, préparer ensuite une instrumentation avant dialogue / avant-après dessin, ciblée sur les classes observées. Ne pas demander à l’utilisateur d’installer d’emblée un autre bundle expérimental alors que l’export existant peut déjà révéler les vues manquantes.

L’attribution d’une bordure pourra nécessiter un essai A/B réversible sur **un slot identifié** (background, foreground ou drawable), avec même Réel et même mode. Aucun essai automatique qui masque des parents ou change de média n’est autorisé par cette stratégie. Les pages adjacentes doivent être suivies par instance/ancre ; les mutateurs doivent indiquer leur état attendu, l’état observé et les remplacements natifs, puis la restauration au détachement/fold.

## État du dépôt et de la distribution

La [CI 4.1.2](https://github.com/senor-roboto/PatchInsta/actions/runs/34317648473) a réussi : 98 scénarios Android, 305 assertions JVM, 13 mappings/XML FR/EN, 14 tests de distribution. Le vrai MPP a été compilé et chargé par Morphe (133 patchs), puis les assets et l’accès anonyme vérifiés. [Preuves techniques](VERIFICATION-4.1.2.json).

**Aucune nouvelle version publiée pour cette investigation. Aucun changement fonctionnel appliqué sur la base de ces seules captures.** Seuls le constat, les limites de preuve et le statut de validation sont corrigés dans la documentation. Il n’y a pas de nouveaux tests de code pour cette étape documentaire.

La source Morphe continue de servir 4.1.2. Un nouveau correctif ne sera proposé à la publication qu’après identification suffisamment précise des objets natifs, justification du changement visible attendu, tests d’invariants, compilation et chargement du MPP. Le résultat pixel sur Samsung et les transitions réelles restent à vérifier sur le Fold 8.
