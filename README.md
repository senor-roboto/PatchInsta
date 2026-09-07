# PatchInsta — Fold Reels v2

Version expérimentale **3.9.0-foldreels.2**, basée sur Piko 3.9.0 et Instagram **439.0.0.37.89 arm64-v8a**.

**Compilation Android réussie le 7 septembre 2026.**

[Télécharger le ZIP contenant piko-fold-reels-v2.mpp](https://github.com/senor-roboto/PatchInsta/actions/runs/34134993071/artifacts/10023719558)

Se connecter à GitHub pour accéder à cet artefact du dépôt privé, puis décompresser le ZIP.

## Pourquoi cette version

Le premier essai sur le Fold a confirmé le crop sur l’écran externe au démarrage. Après ouverture, rotation puis fermeture, le lecteur conservait parfois le cadrage et le placement des boutons du format précédent.

La v1 remettait aussi la géométrie à « inconnue » pendant une pause, et changeait les flags sans reconstruire les vues existantes. Le comportement observé est compatible avec ces défauts et avec des décisions de mise en page mises en cache ; la contribution exacte de chacun reste à confirmer sur appareil.

## Changements

- Conservation du dernier format connu pendant les pauses/transitions, avec lecture du format actuel avant les requêtes de flags effectuées sur le fil principal.
- Classement sur le petit côté de la fenêtre : une rotation seule ne change plus le mode compact/grand écran.
- Recréation de l’écran Instagram après une transition stable de format, uniquement lorsqu’un lecteur de Réels identifié est visible. Délai de stabilisation de 450 ms, activité au premier plan, pas de répétition sur la même instance, report pendant la saisie dans un champ de texte.
- Menu **⋯ → Cadrage Fold** : vidéo entière ou recadrage sur écran interne, plus une commande **Actualiser le lecteur**. Ce choix est indépendant du crop externe.
- Interrupteurs dans **Piko → Divers**, dont un pour désactiver l’actualisation automatique.

La recréation peut recommencer le Réel ou revenir au fil, selon la restauration d’état d’Instagram. Les limites de crop du lecteur natif restent applicables. Les boutons restent gérés par Instagram : cette version vise à reconstruire la disposition correcte dès le pliage, sans déplacement arbitraire des commandes.

## Installer

Télécharger le dernier artefact **piko-fold-reels-v2** depuis [GitHub Actions](https://github.com/senor-roboto/PatchInsta/actions/workflows/build-fold-reels.yml), puis extraire **piko-fold-reels-v2.mpp**.

1. Ajouter ce `.mpp` dans Morphe.
2. Repartir de l’APKM original Instagram **439.0.0.37.89 arm64-v8a**.
3. Sélectionner les patches de **Piko + Adaptive Fold Reels v2 (unofficial)** uniquement. Désélectionner les sources Piko officielle et Fold v1 pour cette opération.
4. Cocher **Adaptive Fold Reels (experimental)**, garder ses dépendances et les autres patches souhaités de cette source.
5. Pour mettre à jour le clone actuel, garder le même package Clone et la même clé de signature Morphe. Patcher puis installer.

[Guide complet](GUIDE-FR.md)

## Essai à effectuer

Démarrer fermé → ouvrir un Réel → déplier en portrait sans rotation → refermer. Vérifier à chaque étape le crop, la position des boutons et si le même Réel est conservé. Tester ensuite la rotation et **⋯ → Cadrage Fold**. Signaler si le menu manque, si le retour au fil est gênant ou si le cadrage reste bloqué.

[Compilation réussie](https://github.com/senor-roboto/PatchInsta/actions/runs/34134993071) depuis le commit `93e048dfb09d80e54a7cbbbb7e432759763b0c36` : Kotlin/Android compilés, 59 assertions de politique/transitions et 15 clés de mappings vérifiées. Cela ne remplace pas la validation sur le téléphone.

SHA-256 du ZIP GitHub Actions, concordant entre son API et le journal : `79a342803bbb382c8799a02d897f00d3340981a2c675617d7c9184acae6949cf`. Le SHA-256 du `.mpp` est inclus dans `SHA256SUMS.txt`.

Les artefacts expirent après 14 jours ; le workflow peut être relancé. Le code reste dans ce dépôt. Le premier bundle est conservé dans l’historique des compilations.

Modification non officielle de Piko, GPL-3.0-or-later. Voir LICENSE et NOTICE.
