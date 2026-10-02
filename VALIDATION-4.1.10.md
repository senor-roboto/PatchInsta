# Fold Reels 4.1.10 validation

## Scope and established reference

The user reports that 4.1.9 is perfect on the physical Fold external display. This is the reference to preserve, not a physical validation of 4.1.10. The new release applies the same complete Clean Fullscreen preset to the internal display, with separate preferences. The native presentation remains the initial internal default and can be restored on either display.

The existing verified native border guard is preserved. Its runtime lease now follows the active screen profile and actual activity presentation state. The same native gradient, author, caption, comment action and video renderer are reused; no video stretching or additional dark overlay is introduced.

## Defects addressed

- The last viewer detach disposed its activity tracker. Re-entering Reels in that already-resumed activity could create a tracker without the resume callback, preventing the border lease. The tracker now retains known lifecycle state until activity destruction, while disposing/reinstalling view observers on detach/attach. A known pause still prevents presentation, including after a stale focus event.
- Short tapping the shortcut previously changed framing alone. The 48 dp fullscreen icon now toggles complete clean/native presets for the active screen; long press retains the menu. Its accessible description identifies the next preset and does not claim recognition when the viewer/window is unknown.
- The native scrubber remained inside the old media rectangle. The exact VideoScrubberSeekBar resource is transformed to the true viewport with an isolated narrow touch proxy. Native horizontal seeking gets the full event stream; vertical drags cancel seeking and return the complete stream to the pager. Native sheets retain priority. Clipped pixels of an enlarged neighbouring TextureView must not be treated as a visible obstruction: the regression tests caught that production defect and it was fixed before final build.

The first physical inner-display session additionally identified the exact `ls_vertical_nav_bar_stub` host: clean mode now hides/restores only this verified left navigation branch without relayout. Caption geometry is constrained above the moved scrubber to avoid overlapping its gesture area. Instagram also translates its native caption scroll host above its parent origin; clipping only the line bottom left a 12-pixel strip. The measured first-line top and bottom now define the clip, including negative offsets, and native descendant clipping is leased/restored without changing their translations. Regression scenarios cover full-line geometry, native clicks, repeated frames and native offset changes.

Initial defaults remain Clean Fullscreen outside and Full Instagram inside. Previously saved/custom choices remain intact. Short tapping changes only an in-memory presentation override; a screen change restores saved defaults. Two advanced settings explicitly save a default preset independently for each screen. Four additional preference/lifecycle scenarios cover persistence, temporary changes and fold round trips.

## Automated checks completed

Candidate commit `229300566ca1affa927e5e2bdcf0e96b2bd2be12`, [Actions run 37019425034](https://github.com/senor-roboto/PatchInsta/actions/runs/37019425034):

- 167 Android scenarios pass, none skipped. These include 9 native progress scenarios, 26 lifecycle scenarios, 10 preference scenarios, 18 Litho scenarios, independent inner/outer presets, icon semantics, restoration, fold/orientation, sheets and seeking/swipe arbitration.
- 22 native bytecode guard tests, 305 policy/geometry checks and 13 mappings/XML checks pass.
- The cumulative source patch applies to pinned Piko `50744aa07bb41c4e1f942a06614ef4e6f2e3610c`; the real compiled MPP is loaded by Morphe and the release kit checksums and ZIP are verified.
- Exact MPP SHA-256: `57bc649d7e8aa06aae88ead012f4778911aeca0764dce02d1294a921e922ee23`.
- The publication guards additionally pass 24 local tests, including rejection of mismatched 4.1.10 evidence and of reuse for an unauthorized future release.

## Local APK and physical validation

The exact candidate MPP was applied to the original Instagram 439 APKM. All 60 patches succeeded; original classes were retained without duplicates, 14 native libraries stayed byte-identical, the injected native border guard was verified, and signature plus 16 KiB ZIP alignment checks passed. The isolated Lab APK SHA-256 is `f68591d355b79716508171c06c20066221f262d62d83b4bc6893a2a39509eebc`. The same APK starts in the Android 15 emulator without a crash; this is a startup check, not a signed-in Reels test.

On 2 October 2026 the user authenticated the isolated Lab on the physical SM_F971B, Android 17 / One UI 9.0. The exact APK was tested by ADB on both physical screens: 10 complete stop/start sequences, 30 slow/fast swipes and one physical open → closed → open round trip. Observed video Reels showed readable captions and no old card border in clean mode. The inner left navigation was hidden. Native comments opened/closed, horizontal seeking advanced the media, and a vertical drag from the scrubber changed Reel. Clean outside and Full Instagram inside returned on cold launch. Both independent default selectors were inspected; saving the inner Full Instagram choice preserved the external Clean choice while cancelling only the temporary inner toggle. No Lab crash was detected. The original screen timeout was restored and both daily Instagram packages were untouched.

These are targeted physical checks. The formal five-fold-cycle protocol was not completed, and native caption expansion/every action variant were not comprehensively exercised on hardware. Static posts/carousels retain native layout, including their native card, when no video renderer is recognized; this release does not broaden the renderer contract to image-only content. No universal visual pass or guarantee for all Instagram content is claimed. The existing user-authorized publication path records `physical_device_validation: pending_user_test`, with actual physical results separately in `validation/release-4.1.10.json`. Private captures remain local; only their digests are recorded.

The publication workflow promotes only the exact checked candidate, verifies source ancestry and immutable assets, tags the current publication commit and advances the same stable Morphe feed after download verification. It is bounded to this authorized release transition, with explicit manual retries. No Instagram APK, account data, screenshot or signing key is uploaded.
