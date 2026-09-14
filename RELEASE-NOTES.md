# PatchInsta 4.1.7

- Corrige le rejet de la référence valide à ViewGroup dans le dispatch arrondi d'Instagram 439.
- Corrige ensuite la recherche de méthode fondée sur une égalité String/ImmutableMethodParameter : remplacement par identité validée, caches virtuels synchronisés.
- 60 patches appliqués à l'APKM original 439.0.0.37.89, avec Fold et Clone ; APK reconstruit, 14 bibliothèques natives préservées, aucun patch en échec.
- Les 27 instructions natives du dispatch sont conservées ; garde de 5 instructions, registres et handlers vérifiés dans l'APK produit.
- 22 tests bytecode, 113 scénarios Android et gates existants verts. Aucun lancement ART ni rendu Samsung n'est revendiqué.

Dans Morphe, actualiser la même source PatchInsta, repatcher l'APKM original avec Adaptive Fold Reels et les patches habituels, puis installer par-dessus avec le même package Clone et la même clé de signature. Un ancien MPP RC importé localement doit être désélectionné pour cette opération.
