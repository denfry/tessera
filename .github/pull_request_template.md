## What this changes

<!-- What goes wrong without this change, and how the patch fixes it. -->

## Patches

<!-- List added/changed patch files, e.g. folia-server/minecraft-patches/features/1000-Fix-something.patch -->

## Checklist

- [ ] One logical change per patch; no unrelated edits mixed in.
- [ ] Patch files rebuilt (`./rb.sh`) and `./gradlew applyAllPatches` works from a clean checkout.
- [ ] Tessera patches use the `1000-` prefix and have a descriptive header (subject + explanation).
- [ ] Built with `./gradlew createPaperclipJar` and tested on a running server (describe below).
- [ ] Vanilla behaviour kept, or the change is behind a config option that is off by default.
- [ ] Folia API compatibility kept; plugins built for Folia still work.
- [ ] Upstream reference added in the patch header (`Upstream: PaperMC/Folia#NNN`) if this ports or addresses an upstream issue/PR; original author credited.
- [ ] [PATCHES.md](https://github.com/denfry/tessera/blob/main/PATCHES.md) updated.

## How it was tested

<!-- Steps, server setup, before/after results, spark profiles for performance changes. -->
