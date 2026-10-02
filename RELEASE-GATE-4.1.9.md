# PatchInsta 4.1.9 release gate

The build workflow only creates a 30-day candidate artifact. It does not publish a release or modify the Morphe feed.

On 2026-10-02 the user explicitly authorized publication after the available automated checks so they can test through their existing Morphe source. This replaces the earlier physical-before-publication condition for this delivery. The **Publish verified PatchInsta 4.1.9** workflow publishes the exact candidate from run 37001703841 once when this delivery is merged. Its push trigger requires the previous main commit to be exactly `d139821fb4303420c37aff6d22ed0cb99dbc2394` and the release evidence file to change; later main pushes cannot satisfy that predecessor guard. Explicit manual dispatch remains available for a failed one-time delivery. It requires [the authorized offline release record](validation/release-4.1.9.json): exact version/run/source/MPP identity, explicit user request, all 60 patches, preserved original classes/native libraries, verified guard/signature/alignment and emulator startup. Missing checks, another candidate or a false physical-pass claim are rejected. The release and feed explicitly say physical Fold rendering remains pending.

The tested MPP is unchanged. Current release documentation is refreshed separately and the ZIP/checksums regenerated deterministically. The release tag points to the publication commit on main; build-info retains the original tested candidate commit. GitHub refuses tagging an earlier commit with different workflows using the Actions token, so this avoids requesting broader credentials. The failed initial publication created no release or feed change; the narrowly scoped retry predecessor is `88555f1a9d9542395dbb18ae9777530fb1bab68b`. Durable release assets are downloaded and verified before advancing the feed; its unchanged anonymous URL and MPP download are then checked. Existing published assets cannot be replaced.

The physical attestation format below remains available for a later actual device validation; it must never be fabricated to authorize an offline release.

For an actual physical validation, complete the device checks and keep screenshots locally. The workflow's optional JSON input supports this schema:

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

The physical attestation is a human record, not a machine observation of the phone. The tester must inspect the screenshots and complete the interactions on the Fold before claiming a physical pass. The user-authorized offline publication uses its separate truthful schema.
