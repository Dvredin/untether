# Dvredin 0.35.5rc15 snapshot: verification and limitations

## Distribution and source

This is a prerelease snapshot for laptop-hosted Codex use through a private Telegram bot, from a phone or Telegram Desktop.

- Tag: `dvredin-v0.35.5rc15-1`.
- Upstream base: `96de98e4d27f3eda6ec939a4ae1dcde16728ab97` (`0.35.5rc15`).
- Wheel: `untether-0.35.5rc15-py3-none-any.whl`.
- SHA-256: `0246b9eb9ef838819bfada532233cc3062de023d1dcd13420baf48c7a8f414d9`.
- Python requirement: 3.12+.

The release reuses the exact existing wheel, rather than silently rebuilding a different package under the same version. All **159 runtime Python files** match this snapshot's `src/untether/` byte-for-byte, with no missing or extra Python modules. A fresh build from the public tree also succeeds; its README metadata differs from the original wheel because the fork-specific installation links were added later.

The public branch is based directly on the public upstream base and exports runtime code, tests and relevant public documentation. It does not publish the private integration branch or its operational history. Licence and upstream attribution are preserved.

Included customisations: Telegram reply/quote context, native Codex photo input including continuation, optional local Telegram Bot API file handling, and preservation of Codex conversation bindings after provider errors. The install handoff uses ordinary public Bot API defaults; a local Bot API deployment is not required.

## Verification for this publication

| Check | Observed result |
|---|---|
| Wheel SHA-256 and source equivalence | Exact checksum above; all 159 Python files equal |
| Clean isolated Python 3.12 tool installation | Installation, `--version`, `--help`, package imports and Markdown rendering passed |
| Installed-wheel regressions, with fresh dependency resolution | 90 passed: reply context, image/continue options, provider-failure continuity, run options and Telegram client API |
| Complete source suite, Python 3.14 with the project lockfile | 5,055 passed, 88 skipped, 5 failed on the first run; coverage 87.02% |
| Affected-test recheck | All 5 initial failures passed after restoring the non-secret `USER` variable omitted by the isolated test environment; no source/test changes |
| Ruff format and lint, lockfile check, Bandit | Passed |
| Source/wheel build; original-wheel metadata/content checks | Passed |
| Installation handoff shell examples | All 5 shell blocks pass `bash -n` |
| Publication privacy checks | No private deployment markers or forbidden runtime/credential material in the export; scanner hits in changed test files are exact inherited upstream lines |

The five first-run failures were in `tests/test_attestation_marker.py`: the upstream shell helper uses `set -u` and references `USER`. The rerun supplies only the missing non-secret variable and retains the isolated HOME. This is a resolved test-environment issue, not a suppressed test or a runtime code fix. Tests requiring unavailable agent CLIs are skipped, not claimed as live engine validation.

Earlier deployments of this source observed upstream Claude live-session cancellation flakiness. The current run did not reproduce it. This snapshot's installation handoff targets Codex and does not claim all supported engines are production-verified.

## Boundaries

No installation on another user's laptop or phone-originated Telegram round trip was performed as part of publishing this artifact. Those are required acceptance steps in [the local-agent installation handoff](install-agent.md), including a real phone request, conversation continuation and a service-environment recheck. A package install and an active service alone are not completion.

No credentials, bot tokens, personal configurations or conversation state are bundled. No model/provider route, running bridge or existing user configuration is changed by publication. Voice transcription and local Bot API hosting remain separately configured optional features.

Use the pinned asset and checksum. Generic PyPI installation/upgrading can replace this fork with upstream code; do not use it to update this snapshot.
