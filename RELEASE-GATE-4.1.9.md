# PatchInsta 4.1.9 release gate

The build workflow only creates a 30-day candidate artifact. It does not create a GitHub release or modify `patches-bundle.json`. The published 4.1.8 feed therefore remains the current stable source until a 4.1.9 candidate passes real Fold testing and is promoted explicitly.

After the candidate build succeeds, install that artifact in the isolated test clone and complete the physical-device checks in the project validation plan. Keep screenshots locally and record their SHA-256 digests; do not upload account or Reel images to a public host. Start the **Promote physically validated PatchInsta 4.1.9** workflow on `main`, enter the candidate workflow run ID and the MPP SHA-256 from `SHA256SUMS.txt`, and provide a JSON attestation matching this schema:

```json
{
  "schema": "patchinsta-device-validation/v1",
  "version": "4.1.9",
  "candidate_run_id": "1234567890",
  "source_commit": "40-character-candidate-commit-sha",
  "mpp_sha256": "64-character-lowercase-sha256",
  "attested_by": "tester",
  "tested_at": "2026-09-23T15:00:00+02:00",
  "device": {
    "model": "Samsung Galaxy Z Fold",
    "android_version": "Android version",
    "one_ui_version": "One UI version"
  },
  "instagram": {"version": "Instagram version"},
  "scenarios": {"cold_starts": 10, "swipes": 30, "fold_cycles": 5},
  "checks": {
    "external_screen_visual_pass": true,
    "internal_screen_native_pass": true,
    "no_media_border": true,
    "gradient_full_width_bottom": true,
    "author_and_caption_readable": true,
    "comments_work": true,
    "scrubber_seeks_correctly": true,
    "no_crashes": true
  },
  "screenshot_sha256": ["64-character-lowercase-sha256"]
}
```

The workflow verifies that the run metadata, candidate commit, attestation, and MPP digest all identify the same build. It refuses other versions, changed bytes, failed or missing checks, insufficient scenario counts, and candidates whose source commit is not on current `main`. The attestation stays with the promotion run artifact and is not published in the public release, which contains only a concise validation note and the MPP digest. The MPP digest entered in the workflow is the digest that is verified and published.

The attestation is a human record, not a machine observation of the phone. The tester must inspect the screenshots and complete the interactions on the physical Fold before submitting it. Do not promote on the basis of compilation or emulator results alone.

