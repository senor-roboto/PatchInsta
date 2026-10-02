# Fold Reels 4.1.9 validation

Status: automated checks complete; publication requested by the user on 2026-10-02 for testing through the existing Morphe source. Physical Fold rendering remains unvalidated. The release records that limitation explicitly.

## Cause established by the supplied Fold diagnostic

The rounded-wrapper hook is already running (`drawCalls=20`, `suppressed=20`) while the thin rectangle remains visible. A separate Litho mount on the direct parent of `clips_media_component` contains `X.07td -> X.08Nt`. Its state has four 1 px widths, four `0x26ffffff` colors, 17 px corner radii and a STROKE Paint. Its global bounds coincide with the old media rectangle, one pixel around the media host. The original Instagram 439 DEX identifies `X.08Nt` as BorderColorDrawable and confirms that every draw restores Paint color and stroke width from state. Changing alpha alone would therefore be ineffective.

The candidate inserts a guard at that drawable's draw entry. Runtime suppression requires the verified media-ring host, a transformed player in the active compact viewer, and the cover crop/card settings. The guard restores native drawing on exit and on other displays. It does not suppress the generic mounted wrapper, which also owns gradients, avatars and touch backgrounds.

The author and caption use named Litho hosts. The avatar detector now accepts the exact profile-picture host under the author role. The bottom gradient has its own mount and is extended separately; the interactive native scrubber is retained. The header and bottom navigation already have independent cover preferences. Inner preferences are preserved.

## Caption correction during review

The previous 20 dp caption clip was a guess. The supplied hierarchy shows scroll padding of 11 px plus a text drawable beginning 17 px lower, before the actual first line. The revised implementation measures the existing Android Layout's first line and includes those offsets. It accesses geometry only, never caption text, and retains native layout when the measurement is ambiguous. The pinned original TextDrawable draws at `bounds.top + A01` using the Layout in `A0B`; these public fields were checked in the original APK.

## Checks actually completed

- Final measured-caption candidate at commit `b439b5e6d2e2e01627ea2bb0546383921f224c55`, [Actions run 37001703841](https://github.com/senor-roboto/PatchInsta/actions/runs/37001703841): 141 Android scenarios, 22 bytecode checks, 305 policy/geometry checks and 13 mappings/XML checks passed. The publication guards additionally pass locally and are rerun by the publication job.
- The exact MPP (`c65259d8f9891d8a9e38fcc47e4f37e06216e64df780c4a1526d422a14089308`) applied all 60 selected patches to the original Instagram 439.0.0.37.89 APKM, including Clone with the isolated lab package. Original APKM SHA-256: `1f20e342cc878225c141c83125ea46773ee8ea9491b8bd0469907de496097c0e`.
- The signed lab APK has no duplicate classes and retains every original class and all 14 native libraries. ZIP, 16 KB alignment and signature checks pass.
- The strengthened static verifier confirms all 303 original BorderColorDrawable instructions are preserved after the five-instruction guard, including registers, native branch operands and exception regions. It also verifies the rounded-wrapper guard and all five Fold hook prototypes.
- The final signed lab APK SHA-256 is `0d54c9c6c4fecf47ae6e295cb99615883d956885253eef53b41a4d6e1bd0c710`. It installed successfully and started to the signed-out login activity (`am start -W`: Status ok) in the isolated API 35 emulator. The crash buffer was empty and the process remained running. This was a startup check without a signed-in account or a Reel.
- Release documentation is refreshed to 4.1.9 before packaging, with deterministic ZIP checksums; the tested MPP, source patch and build evidence remain unchanged. CI's original build-info correctly records device/APK tests as not performed by CI; the subsequent local checks are recorded separately in [release evidence](validation/release-4.1.9.json).

## Remaining visual verification

The user explicitly replaced the previous physical-before-publication condition: publish after successful available automated checks, then test visually through the existing Morphe source. Publication requires that explicit request plus the exact candidate digest and passing APK/startup checks; it cannot label offline evidence as a physical pass. See [the release gate](RELEASE-GATE-4.1.9.md).

On the physical Fold, compare the same paused Reel and settings: old media rectangle, proportional cover crop, readable low metadata, comment interaction, double tap, native seek behavior, swipes and restoration. Compilation, static APK checks and emulator startup are not proof of the Samsung result. If the user's test fails, retain the diagnostic and stop speculative variants; investigate with a reproducible automated test and a small quota budget.
