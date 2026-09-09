PatchInsta 4.1.2 corrige la géométrie des décorations reconnues en cover fullscreen après les retours de la 4.1.1.

- La vidéo et le contraste utilisent les limites de la fenêtre, même si le contenu Android conserve d’anciens insets. Les vues interactives gardent leur espace natif sûr.
- Les scrims inférieurs sont pris en charge, ainsi que les gradients de grande card et les foregrounds. Les composites de contraste suivent le viewport complet au lieu de perdre seulement leur stroke.
- Chaque décoration suit la même page et le même déplacement que son player pendant le swipe. Les dessins restent dans leur couche native, sans ajouter de rectangle sombre ni reparenting des commandes.
- Dessin privé et réversible, contrôle du clipping jusqu’à la fenêtre, restauration au changement de profil/détachement/remplacement natif. Diagnostic structurel enrichi pour identifier les variantes restantes.

Aucun changement de player, de listeners natifs, de flags MobileConfig par défaut, de cold-start hook ni de politique de rechargement.

**Morphe :** actualiser la source PatchInsta existante vers **4.1.2**, repatcher l’APKM original **439.0.0.37.89 / arm64-v8a / 384510827**, puis installer par-dessus avec le même package Clone et le même keystore. Mettre à jour le bundle seul ne modifie pas l’APK installé.

Gates de publication : 98 scénarios Android dont 4 tests de dessin Canvas/Skia, 305 assertions JVM, 13 mappings FR/EN et 14 tests de distribution ; compilation réelle du MPP, chargement Morphe, contrôle du ZIP et des téléchargements publics par SHA-256.

**Limite de preuve :** les captures montrent l’ancienne géométrie, mais n’identifient pas les classes/drawables natifs qui dessinent chaque trait. Les défauts de code corrigés et les tests synthétiques ne prouvent pas que tous les traits Samsung ont disparu. Aucun test matériel ni patching local de l’APKM propriétaire n’est revendiqué. Les décorations inconnues restent natives et sont décrites dans le diagnostic.

Consulter GUIDE-FR.md et ENGINEERING-4.1.2.md dans le dépôt, puis build-info.json / test-results.json dans cette Release.
