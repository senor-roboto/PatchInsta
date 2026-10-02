# Fold Reels 4.1.9 validation

Status: candidate only. Physical rendering has not yet been validated; the Morphe feed still serves 4.1.8.

## Cause established by the supplied Fold diagnostic

The rounded-wrapper hook is already running (`drawCalls=20`, `suppressed=20`) while the thin rectangle remains visible. A separate Litho mount on the direct parent of `clips_media_component` contains `X.07td -> X.08Nt`. Its state has four 1 px widths, four `0x26ffffff` colors, 17 px corner radii and a STROKE Paint. Its global bounds coincide with the old media rectangle, one pixel around the media host. The original Instagram 439 DEX identifies `X.08Nt` as BorderColorDrawable and confirms that every draw restores Paint color and stroke width from state. Changing alpha alone would therefore be ineffective.

The candidate inserts a guard at that drawable's draw entry. Runtime suppression requires the verified media-ring host, a transformed player in the active compact viewer, and the cover crop/card settings. The guard restores native drawing on exit and on other displays. It does not suppress the generic mounted wrapper, which also owns gradients, avatars and touch backgrounds.

The author and caption use named Litho hosts. The avatar detector now accepts the exact profile-picture host under the author role. The bottom gradient has its own mount and is extended separately; the interactive native scrubber is retained. The header and bottom navigation already have independent cover preferences. Inner preferences are preserved.

## Caption correction during review

The previous 20 dp caption clip was a guess. The supplied hierarchy shows scroll padding of 11 px plus a text drawable beginning 17 px lower, before the actual first line. The revised implementation measures the existing Android Layout's first line and includes those offsets. It accesses geometry only, never caption text, and retains native layout when the measurement is ambiguous. The pinned original TextDrawable draws at `bounds.top + A01` using the Layout in `A0B`; these public fields were checked in the original APK.

## Checks actually completed

- Candidate build at commit `3a95df1119f859e651e5e255960b452a514fc061`: 138 Android scenarios, 22 bytecode checks, 305 policy/geometry checks, 13 mappings/XML checks and 19 distribution tests passed.
- That MPP (`8a28748ce53da2b681d7ba7bcae9d39082d6df7d2340c58b71e61152e7b453bb`) applied all 60 selected patches to the original Instagram 439.0.0.37.89 APKM, including Clone with the isolated lab package.
- The signed lab APK has no duplicate classes and retains every original class and all 14 native libraries. ZIP, 16 KB alignment and signature checks pass.
- The strengthened static verifier confirms all 303 original BorderColorDrawable instructions are preserved after the five-instruction guard, including registers, native branch operands and exception regions. It also verifies the rounded-wrapper guard and all five Fold hook prototypes.
- The measured-caption revision adds three targeted scenarios and requires a fresh build and APK application before physical validation. Earlier successful APK checks do not validate that revision.

## Remaining release gate

Use the separate lab app on the physical Fold. Compare the same paused Reel and settings; verify the old media rectangle disappears, proportional cover crop, readable low metadata, comment interaction, double tap, native seek behavior, swipes and restoration. Preserve local screenshots and diagnostic evidence. Compilation and static APK checks alone are not proof of the Samsung result. Promotion must satisfy [the release gate](RELEASE-GATE-4.1.9.md) before changing the existing Morphe feed.
