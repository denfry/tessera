# Contributing to Tessera

Tessera is a small set of patches on top of [Folia](https://github.com/PaperMC/Folia). The rules
below keep that set easy to review and cheap to rebase when upstream moves.

## Setup

You need:

- **JDK 25** (Gradle downloads one through toolchains if it is missing).
- **Git**, with `user.name` and `user.email` configured — the patch tooling makes commits.
- On Windows, a shell that handles long paths and LF line endings (Git Bash or WSL work).

```bash
git clone https://github.com/denfry/tessera.git
cd tessera
./gradlew applyAllPatches
```

`applyAllPatches` decompiles Minecraft, sets up the Paper sources and applies all Folia and Tessera
patches. Afterwards these directories are separate Git repositories:

| Directory | Contents | Patches go to |
|-----------|----------|---------------|
| `folia-server/src/minecraft/java` | Minecraft server sources | `folia-server/minecraft-patches/features/` |
| `paper-server` | Paper server sources | `folia-server/paper-patches/features/` |
| `paper-api` | Paper API sources | `folia-api/paper-patches/features/` |

Build a runnable jar with `./gradlew createPaperclipJar` (run it separately, after patching).

## Making a change

1. Edit the sources in the nested repository (`folia-server/src/minecraft/java` or `paper-server`,
   or `paper-api` for API changes).
2. Commit inside that repository. **One commit = one patch = one logical change.**
   To amend an existing Tessera patch, commit a fixup and squash it into the original commit
   (`git commit --fixup <hash>` followed by an autosquash rebase).
3. Go back to the root and rebuild the patch files:

   ```bash
   ./rb.sh        # rb.bat on Windows
   ```

   `rb.sh` runs `rebuildPaperPatches`, `rebuildPaperServerPatches`, `rebuildServerPatches` and
   `rebuildMinecraftPatches`. You can run one of them alone if you touched only one repository.
4. Check `git status` in the root: only the patch files you meant to change should differ.
5. Add a row for the patch to [PATCHES.md](PATCHES.md).
6. Commit the patch files in the root repository and open a pull request.

To start over from the committed patch files, run `./gradlew applyAllPatches` (or `./patch.sh`).

## Patch rules

- **One change per patch.** Do not mix a bug fix with a refactor or an unrelated optimisation.
- **Ordering.** Tessera patches sit after all upstream patches. Paperweight renumbers the files on
  every rebuild, so after merging upstream rebase the Tessera commits on top and run `./rb.sh`.
- **Small diffs.** Touch as few upstream lines as possible; that is what keeps merges painless.
  Mark changed lines with a `// Tessera` comment (or `// Tessera start` / `// Tessera end` around
  blocks), following the Paper and Folia convention.
- **Vanilla behaviour by default.** Anything that changes gameplay must sit behind a config option
  that is off by default, unless it fixes a bug, dupe or exploit.
- **Folia API compatibility.** Plugins built for Folia must keep working. Do not remove or change
  the behaviour of public API; new API goes into a separate patch in `folia-api/paper-patches`.
- **Thread ownership.** Code that touches world, entity or chunk state must run on the thread that
  owns that region. Use the region/entity schedulers rather than synchronising around them.

## Patch header

The commit message becomes the patch header. Use this format:

```
Short imperative subject line (max ~72 chars)

What goes wrong without the patch and how the patch fixes it.
Mention any config option it adds and its default.

Upstream: PaperMC/Folia#NNN
```

- The subject becomes the file name, so keep it short and specific (`Fix item dupe on cross-region
  teleport`, not `Fixes`).
- Add `Upstream: PaperMC/Folia#NNN` (or the Paper issue/PR) when the patch ports or addresses
  something reported or proposed upstream.
- When porting someone else's work, keep them as the commit author (`git commit --author`) and
  say where it came from in the body.

## Testing

Before opening a pull request:

- `./gradlew applyAllPatches` works from a clean checkout with your patch files.
- `./gradlew build` passes (CI runs the same thing on pull requests).
- You ran the server built with `createPaperclipJar` and checked the change in game: reproduce the
  bug before, confirm it is gone after. Mention what you tested in the PR.
- For performance patches, attach [spark](https://spark.lucko.me/) profiles from before and after.
- Watch the console for region-ownership errors and watchdog warnings while testing.

## Upstream merges

```bash
git fetch upstream
git merge upstream/ver/<version>
./gradlew applyAllPatches   # fix conflicts in the nested repos, then ./rb.sh
```

If a Tessera patch has been merged upstream, drop it and remove its row from PATCHES.md.

## Reporting bugs and exploits

Bugs go to the [issue tracker](https://github.com/denfry/tessera/issues/new/choose). Dupes, crash
exploits and other security problems must be reported privately — see [SECURITY.md](SECURITY.md).

By contributing you agree that your patches are licensed under [PATCHES-LICENSE](PATCHES-LICENSE).
