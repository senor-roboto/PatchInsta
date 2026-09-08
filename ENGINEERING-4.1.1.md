# PatchInsta 4.1.1 — correctifs après tests Fold

## Résultat publié

**Release 4.1.1 publiée ; [CI 34286382910 entièrement verte](https://github.com/senor-roboto/PatchInsta/actions/runs/34286382910).**

- Commit compilé : `ffd516f5afb2987c8eb79b08136574b825f18b21` ; feed : `524bd5e596cad8843f9ea4ac2d94a851b03e8bfb`.
- 77 scénarios Android, 305 assertions JVM, 13 mappings et 14 tests de distribution réussis ; aucun scénario Android ignoré.
- MPP réel compilé ; loader Morphe : 133 patchs chargés, cible Instagram vérifiée.
- 11 assets durables relus après upload ; ZIP et MPP cohérents ; **accès anonyme du feed stable et SHA-256 du MPP public vérifiés**.
- [MPP](https://github.com/senor-roboto/PatchInsta/releases/download/v4.1.1/PatchInsta-4.1.1.mpp) : `b8a8c1fb414c7017229af28a30bda0d7b1ef7054ac8964902085e440d2e0aee1` (6 809 703 octets).
- [ZIP](https://github.com/senor-roboto/PatchInsta/releases/download/v4.1.1/PatchInsta-4.1.1.zip) : `65110d14cd7907c6e951cce33b40a1f76c4c60dc1b77ad8c09da97c8ee7119d3` (6 592 459 octets).

[Relevé complet des vérifications et URLs](VERIFICATION-4.1.1.json) · [Guide de mise à jour](GUIDE-FR.md). Actualiser la source PatchInsta existante, repatcher l’APKM original puis installer par-dessus avec le même package Clone et la même clé ; aucune réimportation de source.

## Point de départ et observations

HEAD audité : `4179fde1606ce692f029c4679738876d38973c0c`, Release 4.1.0, source désormais publique. Reprise des sources cumulatives existantes, sans remplacement de l’amont Piko 3.9.0 épinglé. Cible Instagram inchangée : 439.0.0.37.89, arm64-v8a, versionCode 384510827. La spécification `PROMPT_GPT6_PATCHINSTA.md` et les derniers retours restent la référence.

Les trois captures 8314/8312/8310 et la vidéo 8316 ont été examinées. La vidéo dure 15,79 s, 1080 × 1708, cadence variable, environ 89,8 images/s. Elle montre le bandeau passant de sa position intérieure vers le haut, parfois coupé ; après le passage par les messages vers 8 s, il reprend sa position puis remonte de nouveau. La caption et l’identité conservent souvent le retrait du cadre natif, et un fin contour arrondi reste visible. Les cartes photo/carrousel sans surface vidéo affichent « Cadrage ? » : ce n’est pas une preuve d’un échec du crop d’un player vidéo.

Le démarrage incomplet est un retour utilisateur ; la vidéo commence après activation. Aucune hiérarchie native, APKM ni trace de démarrage n’est jointe. Il serait incorrect d’attribuer avec certitude le défaut matériel à une classe ou un drawable précis.

## Causes vérifiables et choix

1. Le constructeur est le seul point d’entrée visuel en 4.1.0. La résolution d’Activity utilise exclusivement le Context du viewer : une inflation avec Application/Context de thème sans Activity est ignorée. Un callback manqué ou un observateur remplacé n’a pas de point de rattrapage au dessin. La nouvelle entrée dans `dispatchDraw(Canvas)` du même viewer vérifie l’enregistrement et l’observateur ; elle ne rend à nouveau qu’au bootstrap. Elle n’effectue pas un scan d’Activity à chaque image. Les parents attachés et les fenêtres déjà connues permettent de résoudre le propriétaire. La route tactile et l’ouverture des réglages peuvent également réparer l’enregistrement.
2. Le renderer peut choisir un wrapper vidéo comme ancre de page. La découverte des métadonnées s’arrêtait à cette ancre alors que les vues d’auteur/caption pouvaient être dans un overlay frère. Une portée de présentation distincte remonte jusqu’avant le parent partagé par deux pages connues. **Le choix de l’ancre, le calcul du crop, l’espacement et le clipping de chaque vidéo restent inchangés.** Les textes et les boutons gardent leurs bindings natifs.
3. La ligne d’identité exigeait Suivre, ce qui excluait un compte déjà suivi. Le rôle Suivre est maintenant facultatif ; avatar + nom identifiés restent nécessaires. La recherche est limitée à la partie basse de la page pour ne pas prendre le bandeau comme une identité. Les captions TextView utilisent toujours une ligne avec ellipsis. Une vue spécialisée nommée comme caption/description est bornée à une ligne visible, sans lire ni recopier son texte. Son ellipsis natif n’est pas garanti.
4. Il n’existait aucun propriétaire du placement du bandeau partagé. `FoldReelsHeader` identifie un petit groupe supérieur hors des portées de pages et maintient sa position verticale globale. Il compense les translations locales/ancêtres et l’alpha natif, restaure leurs dernières valeurs à la sortie, sans reparenting ni annulation du player. Les autres onglets et les métadonnées de chaque page sont exclus. Le chip est sous sa zone tactile.
5. CardChrome s’arrêtait au chemin vidéo et rejetait tout composite contenant un gradient. Il accepte maintenant les feuilles décoratives non interactives de géométrie identique aux wrappers et les couches arrondies inspectables. Les composites sont clonés avant séparation ; le gradient et les ConstantStates natifs sont préservés. Les drawables arbitraires ne sont pas supprimés. Le scrim supérieur peut aussi être le background d’un groupe : son dessin est étendu vers le vrai viewport sans transformer les textes du groupe.

## Invariants, diagnostic et limites

Aucun changement des flags MobileConfig par défaut, des prefs existantes, de la source Morphe, du package cible ni de la clé de signature. Aucun scroll programmatique, rebind, changement de média ou recréation automatique. Le rechargement demeure une action manuelle doublement confirmée.

Le commentaire conserve son propriétaire et son routage. Les métadonnées emploient le même mécanisme pour les vues déplacées. Le bloc interactif reste dans les limites tactiles du viewer : il peut donc garder un retrait sous la dernière ligne si le viewer finit au-dessus du bord physique. Le header conserve sa présentation native horizontale ; la séparation du chip évite le chevauchement. Les cas non reconnus sont signalés par les compteurs du diagnostic et restent natifs.

Le diagnostic ajoute les bandes partagées détectées, leur maintien, les backgrounds de scrim et les calques décoratifs frères. Il ne lit pas les textes, usernames, captions, tags, labels d’accessibilité ou médias. Les identifiants de ressources sont utiles ; les fixtures de tests utilisent seulement des tags synthétiques comme adaptateur d’identifiants.

## Vérification et publication

Tests exigés avant publication : 77 scénarios Android (14 runtime, 18 lifecycle, 23 présentation, 5 scrim, 4 préférences, 13 régressions vidéo/overlays), 305 assertions géométrie/politique, 13 mappings et XML FR/EN, 14 tests de distribution. Les nouveaux scénarios couvrent Application Context, premier dessin sans constructeur, observateur perdu, vraie notification pre-draw, animations du header, clic natif, scrim du header, overlays frères, comptes suivis, caption spécialisée, séparation des pages et restauration du contour composite. Aucun scénario ignoré accepté.

Les premiers runs ont exposé le cas Android 10 où `GradientDrawable.getCornerRadii()` lève une exception pour une forme sans tableau de rayons : ce cas est maintenant traité comme un rectangle ordinaire. La suite de 77 scénarios et la compilation passent au run `34285200558`. Sa publication a révélé un second défaut de distribution : la collection REST publique ne contenait pas immédiatement le brouillon créé. Le publisher utilise désormais directement les identifiants REST de Release et d’assets. Le retargeting et la publication conservent explicitement `tag_name` : une mise à jour qui l’omettait a transformé le tag du brouillon en `untagged-*`, rendant les commandes CLI par tag inutilisables. Seul le brouillon vide correspondant créé par Actions est récupéré. Les transferts utilisent les endpoints officiels par ID, puis les octets téléchargés sont revérifiés. Référence : [API GitHub des assets](https://docs.github.com/en/rest/releases/assets).

La CI compile réellement le MPP, charge son patch avec le loader Morphe et vérifie la compatibilité annoncée. Cette opération ne remplace pas un patching de l’APKM ni une exécution sur Android 17/Samsung. L’extension est validée par des tests Android simulés.

Le workflow publie une nouvelle Release immuable, vérifie à nouveau les 11 fichiers téléchargés, puis avance **le même** `patches-bundle.json` sans force-push. Le contrôle anonyme attend de façon bornée la propagation du JSON sur son URL stable ; une mauvaise somme du MPP fait échouer la vérification. Aucune nouvelle URL de source n’est créée.

Les résultats de la compilation, la révision exacte, les hashes et les URLs sont enregistrés dans [VERIFICATION-4.1.1.json](VERIFICATION-4.1.1.json). La Release fournit `build-info.json`, `test-results.json` et `SHA256SUMS.txt` ; aucune validation physique nouvelle n’est revendiquée.
