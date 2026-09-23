# PatchInsta 4.1.8 candidate

This is a prerelease candidate; stable Morphe remains 4.1.7.


- Corrige le rejet de la référence valide à ViewGroup dans le dispatch arrondi d'Instagram 439.
- Corrige ensuite la recherche de méthode fondée sur une égalité String/ImmutableMethodParameter : remplacement par identité validée, caches virtuels synchronisés.
- 60 patches appliqués à l'APKM original 439.0.0.37.89, avec Fold et Clone ; APK reconstruit, 14 bibliothèques natives préservées, aucun patch en échec.
- Les 27 instructions natives du dispatch sont conservées ; garde de 5 instructions, registres et handlers vérifiés dans l'APK produit.
- CI shared-source evidence: 22 bytecode checks and 136 Android scenarios passed. A generic API 35 emulator installed and started an isolated test-signed clone APK; no real Fold/Reels visual or Samsung rendering validation is claimed.

### Candidate validation

The 4.1.8 candidate keeps the scoped Fold Reels runtime changes and adds the Litho border audit/guard path. Local reconstruction applied 60/60 selected patches to Instagram 439 with Clone; static DEX and packaging checks passed. A generic API 35 emulator installed and started the signed test APK. Real Fold/Reels visual border removal, Samsung compositor behavior and physical-device validation remain unverified.

Dans Morphe, actualiser la même source PatchInsta, repatcher l'APKM original avec Adaptive Fold Reels et les patches habituels, puis installer par-dessus avec le même package Clone et la même clé de signature. Un ancien MPP RC importé localement doit être désélectionné pour cette opération.
