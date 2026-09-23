# PatchInsta 4.1.8 release candidate

This document describes a development candidate for Instagram 439.0.0.37.89.

The candidate includes a narrowly scoped Litho border suppression path. It targets the verified rounded media decoration dispatch only while the active Fold Reels viewer owns the descendant view; native media playback, gestures, clipping and restoration remain covered by the existing test suite.

Evidence currently available:

- CI run 34937400357 passed on commit 10e774dc with 136 Android scenarios, 22 bytecode checks, policy/geometry checks, mapping checks and distribution checks.
- The candidate was installed and started on a generic API 35 Android emulator with an isolated test signature.
- The emulator reached Instagram's login screen without an immediate startup crash.

Validation still pending:

- CI for the current pull request head.
- Installation with the user's Morphe keystore and clone package.
- A real Fold Reels session and before/after pixel comparison of the inner contour.
- Physical Fold hinge posture and interaction validation.

This is a prerelease candidate only. It must not update the stable Morphe feed or be described as a confirmed visual fix until those device and Reels gates pass.
