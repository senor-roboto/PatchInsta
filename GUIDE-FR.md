# PatchInsta 4.1.0 — installation et utilisation

Bundle non officiel basé sur Piko 3.9.0 au commit `50744aa07bb41c4e1f942a06614ef4e6f2e3610c`. Cible inchangée : Instagram **439.0.0.37.89 / arm64-v8a / 384510827**, à partir de l’**APKM original non patché**.

## Installer une fois la source distante

Dans Morphe, ajouter une **source distante** :

```text
https://github.com/senor-roboto/PatchInsta
```

Ou ouvrir sur le téléphone [Ajouter PatchInsta à Morphe](https://morphe.software/add-source?github=senor-roboto%2FPatchInsta). Le lien `morphe.software/add-source` s’ouvre dans le navigateur ; dans le champ d’ajout manuel du gestionnaire, utiliser l’URL GitHub ci-dessus. Le [JSON direct](https://raw.githubusercontent.com/senor-roboto/PatchInsta/main/patches-bundle.json) est l’autre URL de source reconnue.

La source a besoin d’un dépôt **public**. Si le dépôt est encore privé, Morphe ne peut pas en télécharger le JSON et le bundle sans authentification. La Release reste téléchargeable après connexion à GitHub, mais son import local ne fournit pas les futures mises à jour distantes.

La nouvelle source s’appelle **PatchInsta (Piko, unofficial)**. Pour le premier passage depuis les bundles locaux v3/v4, recopier sa sélection de patchs Instagram vers cette source. Pour cette opération, sélectionner uniquement PatchInsta : elle comprend Piko, et les deux sources appliquées ensemble créeraient des doublons. Les anciennes sources ne sont plus nécessaires pour cet Instagram.

Cocher **Adaptive Fold Reels** (optionnel) avec **Add settings** et les autres patchs souhaités. Conserver le même package généré par **Clone** que celui de l’application actuelle.

**Avant de commencer, exporter/sauvegarder le keystore de signature Morphe.** Garder le même gestionnaire ou restaurer cette clé si le gestionnaire est réinstallé. Android exige le même package et une signature compatible pour installer par-dessus. Ne pas désinstaller Instagram pour une mise à jour ordinaire.

Patcher l’APKM compatible, puis installer l’APK produit par-dessus le clone existant. Le `.patch` du dépôt est un diff de sources ; le fichier importable manuellement est le `.mpp`.

## Choisir la présentation

Sur un Réel, toucher le bouton **Entière / Remplir** pour changer le cadrage du Réel courant, sans rafraîchir. Le texte indique l’action proposée. Cette action remet le zoom supplémentaire à 100 %.

Un **appui long** ouvre **Cadrage Fold**. Le même menu reste accessible par **⋯ → Cadrage Fold** et par les réglages **Piko → Divers**.

Sur l’écran externe :

- **Plein écran propre** : crop, barres Android et navigation Instagram masquées, commentaire seul, auteur et caption compacts, décor de card reconnu neutralisé, raccourci visible.
- **Instagram complet** : cadrage natif, navigation et actions visibles, métadonnées complètes, déplacement et nettoyage du décor désactivés.
- **Personnaliser** : actions Toutes / Commentaire seul / Aucune ; compte et légende complets / compacts / masqués ; déplacement du rail, raccourci, barres et décor indépendants.

Sur l’écran interne, la vidéo entière, les actions et les métadonnées complètes restent le défaut. Son crop, son zoom, ses actions et ses métadonnées ont des réglages indépendants.

Les anciens choix explicitement enregistrés sont conservés. En particulier, l’ancien mode minimal activé devient **Commentaire seul** ; désactivé explicitement, il devient **Toutes**. Choisir **Plein écran propre** une fois pour appliquer l’ensemble des nouveaux défauts cover.

Les vues natives de l’avatar, du nom et de Suivre sont réutilisées. La largeur est calculée à partir du rail commentaire, la caption occupe une ligne avec ellipsis. Le bloc reste dans la zone tactile du viewer : si celle-ci ne rejoint pas le bas physique de l’écran, un retrait inférieur peut rester. Le dégradé supérieur identifié est étendu au vrai bord du viewport sans déplacer les boutons du header. Une forme composite ou inconnue reste intacte pour préserver le contraste et les interactions.

## Options avancées

Le zoom sert notamment aux bandes intégrées aux pixels de la vidéo. **Détection des écrans** peut être forcée provisoirement si la densité ou le partage d’écran trompe la classification ; revenir ensuite à Automatique.

**Disposition native** permet un essai isolé « sans two-pane ». Ce choix n’agit qu’au prochain lancement complet manuel, sur les deux écrans, pour éviter des flags incohérents pendant un pliage. La politique v4 demeure le défaut ; l’effet matériel de cette expérience n’est pas validé. Aucun redémarrage n’est déclenché par le réglage.

**Recharger le lecteur…** est un dépannage manuel avec une seconde confirmation. Il peut perdre le Réel courant ; le cadrage normal et le pliage ne l’utilisent jamais. Un balayage depuis le bord peut révéler les barres système temporairement. Les composants restaurent leurs modifications hors du lecteur ou pendant la saisie.

## Mettre à jour ensuite

1. Actualiser la source **PatchInsta déjà présente**, ou suivre son indication de mise à jour.
2. Garder la sélection de cette source et choisir l’APKM original compatible.
3. Repatcher, puis installer par-dessus avec **le même package Clone et le même keystore**.

Aucune nouvelle importation de `.mpp` n’est nécessaire avec la source distante. Morphe ne modifie pas automatiquement l’APK installé : le repatching reste une étape utilisateur. Le badge de l’application dépend aussi de son suivi dans Morphe et de l’actualisation de la source.

## Tester sur le Fold et envoyer un diagnostic

Après installation, arrêter complètement Instagram puis le lancer téléphone fermé : entrer directement dans les Réels, sans déplier ni ouvrir le menu. Le raccourci et le cadrage doivent s’activer. Refaire ce test téléphone ouvert.

Tester ensuite quelques swipes lents puis rapides ; ouvrir les commentaires, les fermer, puis commencer un swipe depuis le commentaire. Tester aussi avatar, nom, Suivre et caption. Passer cover → inner → cover sur le même Réel, puis tourner l’écran interne et revenir. Ne pas utiliser le rechargement manuel pendant ce test.

Vérifier sur cover le dégradé jusqu’au bord supérieur, la caption sur une ligne, l’espace réservé au commentaire et l’absence de rectangle résiduel. Sur inner, vérifier le retour du décor et des métadonnées natives. Désactiver/réactiver les options pour vérifier la restauration.

En cas de défaut, ouvrir **Cadrage Fold → Options avancées → Diagnostic du lecteur → Copier**. Joindre ce texte et une capture courte. Le rapport inclut lifecycle, fenêtre, viewport, surfaces, rails, branches cachées, décor, scrim, largeur des métadonnées et raisons de repli. Il exclut textes, captions, usernames, identifiants de compte, URLs et identifiants de média. Rien n’est envoyé automatiquement.

Les tests CI portent sur des vues Android simulées, pas sur le décodeur Instagram, le tactile physique du Fold ou son compositeur. Aucun APKM Instagram n’a été fourni pour cette itération : le chargement du bundle est vérifié, mais son application à l’APKM exact reste à confirmer dans Morphe.

## Fichiers durables

[Release 4.1.0](https://github.com/senor-roboto/PatchInsta/releases/tag/v4.1.0) : `PatchInsta-4.1.0.mpp`, `PatchInsta-4.1.0.zip`, `SHA256SUMS.txt`, ce guide, licence, notice, changelog, sources et informations de compilation. Le ZIP contient le même `.mpp` que le fichier direct. Ses sommes internes vérifient les fichiers qu’il contient ; les sommes externes vérifient aussi le ZIP.

GPL-3.0-or-later ; les mentions Piko amont sont conservées. Aucun APK Instagram redistribué.
