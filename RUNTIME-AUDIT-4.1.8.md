# Fold runtime investigation — 4.1.8 work branch

Base: stable 4.1.7, main commit 42bba261e8fe2e67b720ed5495571adc21e3dff3.
This is work in progress, not a released visual fix. Stable Morphe remains 4.1.7.

## Evidence read before changes

Four device screenshots (8435, 8430, 8428, 8432) and both full diagnostic exports from 2026-09-14, 08:55:06 external / 08:54:38 internal. No account names, caption text, or screenshots are copied into this repository.

Both screenshots pairs show the thin rounded media rectangle while the video extends beyond it. External screenshots also show the Reels header and native-sized metadata; internal screenshots retain the tablet navigation and complete action rail.

| Observation | External | Internal |
| --- | --- | --- |
| Window profile | COMPACT, 444×701 dp | WIDE, 657×870 dp |
| Visual target | 0,0–1248,1972 | 181,110–1848,2406 |
| Media ComponentHost | 929×1654 | 1258×2238 |
| Direct parent ComponentHost | 931×1656 | 1260×2240 |
| Insets of media in parent | 1 px on all four sides | 1 px on all four sides |
| Mounted drawable on parent | X.07td, full parent bounds | X.07td, full parent bounds |
| Outline provider | X.0C30; elevation 0; outline clipping false | Same |
| Rounded native bypass | Enabled; 8 draws suppressed | Disabled; none suppressed |
| Metadata requested | COMPACT, zero identities/captions found | FULL |
| Actions | COMMENT_ONLY | ALL |

Internal crop=true is explicitly recorded in the supplied profile. This work does not overwrite that persisted choice or force crop on the internal display.

## Layer attribution and confidence

* **Video, confirmed:** native TextureView. External scale 1.340494 and bounds extending beyond the window establish that the renderer crop is operating.
* **Rounded media outline, strongly suspected but not proved:** the mounted drawable on the direct parent of clips_media_component. Its bounds surround the media by exactly one pixel on both profiles. X.07td also occurs on gradients, touch backgrounds, pause/mute buttons and reaction components; the obfuscated class name is not a border classifier.
* **Outline provider, not established as the visible painter:** clipToOutline=false and elevation=0 provide no evidence that this provider is painting the line. The new diagnostic reads its Outline geometry without replacing it.
* **Bottom progress line, confirmed native component:** VideoScrubberSeekBar#scrubber. It is interactive and is not removed as decoration.
* **Full-width bottom separator, independently identified:** #tab_bar_shadow remains visible next to the hidden #tab_bar. The fix pairs this exact sibling with a positively recognized bottom bar.
* **Header, confirmed:** ClipsViewerActionBar#clips_viewer_action_bar is a shared sibling of the viewer. Existing header code pins it; chrome tabs=true describes bottom navigation, not this header.
* **Top contrast:** a native GradientDrawable on the shared action bar. The external export records native alpha=0 and an extended target partly outside its local Canvas clip. Enlarging the viewport alone cannot establish that this draws visible full-bleed contrast.
* **Bottom contrast, confirmed host but unresolved contents:** #clips_bottom_legibility_gradient_component contains another mounted X.07td. Current background/foreground scanning does not inspect its mounted payload.
* **Metadata:** author info and caption are ViewGroups with mounted drawing, including #clips_author_username and #clips_caption_component. The old detector excludes ViewGroups as text roles. This explains zero candidates despite stable IDs in the export.

The rounded dispatch bypass demonstrably runs externally while the rectangle persists, and the same rectangle exists internally with the bypass disabled. Rewriting the dispatch matcher would not address the evidence.

## Implemented runtime changes

1. Recognize metadata from #clips_media_info_component and unique, named author/username/caption/follow roles. Do not promote its whole overlay into an author row.
2. Keep native Litho row dimensions and descendant offsets/listeners. Translate the complete row; leave a row native if it exceeds safe width. Compact the caption with a reversible clip, without pretending to reflow Litho text or synthesize an ellipsis.
3. Respect ancestor clip bounds in moved-control hit testing so an invisible caption remainder is not a synthetic touch target.
4. Add a separate cover-only Reels-header preference and clean/native preset behavior. Inner navigation remains independent.
5. Hide only the exact #tab_bar_shadow sibling paired with a validated hidden bottom bar; restore leases on exit/detach.
6. Add an export-only mounted-media audit. It follows the renderer's actual player paths, identifies equal-inset media parents, reports mounted instances, bounds, callbacks and states, and follows only Drawable/Paint-typed fields on application-owned drawable classes. It does not inspect Android private fields, strings, account text, bitmap pixels or arbitrary mount objects.

**No unknown Litho drawable is suppressed.** The new diagnostic is intended to establish the wrapped drawable/paint responsible for the contour before adding a scoped reversible rendering lease.

## Preserved source invariants

The source-patch sections for RoundedCardHook.kt, AdaptiveFoldReelsPatch.kt, RoundedCardHookTest.kt, FoldReelsRenderer.java, FoldReelsNativeDecoration.java and FoldReelsPolicy.java are identical to stable 4.1.7. No new bytecode matcher, reload, Activity recreation path or MobileConfig policy is introduced.

## Validation and release gate

Local policy/geometry: 305 checks passed. Resource/mapping validation: 13 exact mapping keys and FR/EN XML passed. Distribution guards: 14 tests passed.

The initial CI compiled the runtime and ran 126 Android tests: 125 passed, one new combined metadata-click scenario failed (expected 3 clicks, got 2). It is being diagnosed with separate assertions for author, follow and caption. No failed assertion is disabled.

An unavailable local execution environment and missing original APK/APKM currently prevent repeating the complete Instagram 439 patch/rebuild test and inspecting X.07td in its real DEX. A build or Robolectric pass is not a replacement for those gates or a Samsung pixel test.

Do not merge/release this work branch until the new tests pass and the original-APK gate has been rerun. Final visible contour removal remains blocked on concrete drawable evidence.

## Files

Runtime: FoldReelsMetadata.java, FoldReelsHeader.java, FoldReelsChrome.java, FoldReelsControls.java, FoldReelsPreferences.java, FoldReels.java, FoldReelsDiagnostics.java, new FoldReelsMountedAudit.java.
Tests: new FoldReelsLithoTest.java.
Resources: FR/EN header preference.
Distribution: cumulative piko-fold-reels.patch, release.json, scripts/bundle.py and work-branch CI trigger.
