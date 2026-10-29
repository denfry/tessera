Tessera
=======

Fork of [Folia](https://github.com/PaperMC/Folia) (regionised multithreading on top of
[Paper](https://github.com/PaperMC/Paper)) with bug fixes, performance work and a few
features for large survival servers. Built for the [Politernal](https://politernal.ru) network.

> Early stage. Not production-ready yet: for now this is a stock Folia build.

## Goals

- Track upstream Folia closely; every Tessera change is a separate, documented patch.
- Bug fixes (dupes, crashes, region-ownership violations) that upstream has not taken yet.
- Optimisations that keep vanilla behaviour unless a config option says otherwise.
- Nothing that silently breaks plugins written for the Folia API.

## Plugins

Tessera runs only plugins that declare `folia-supported: true`. Paper's API already ships the
Folia schedulers (`getRegionScheduler()`, `getGlobalRegionScheduler()`, `getAsyncScheduler()`,
`Entity#getScheduler()`), so a plugin written against them runs unchanged on Paper, Leaf and Tessera.

## Building

Requires Git and JDK 25 (Gradle downloads one if missing).

```bash
./gradlew applyAllPatches
./gradlew createMojmapPaperclipJar   # separate run: the task exists only after patching; folia-server/build/libs/*-paperclip-*.jar
```

## Working on patches

Layout is inherited from Folia so upstream merges stay cheap:

- `folia-server/minecraft-patches/` — patches to Minecraft sources (`features/` = per-feature).
- `folia-server/paper-patches/` — patches to Paper server sources.
- `folia-api/paper-patches/` — patches to the API.

Tessera patches start at `1000-` so they never collide with upstream numbering. Workflow:
edit sources under `folia-server/src/minecraft` or `paper-server`, commit there, then run
`./gradlew rebuildAllServerPatches` (see `rb.sh`).

Updating upstream:

```bash
git fetch upstream
git merge upstream/ver/<version>
./gradlew applyAllPatches   # fix conflicts, then rebuild patches
```

## License

Patches are licensed under the terms in [PATCHES-LICENSE](PATCHES-LICENSE), same as Folia.
Minecraft sources are not distributed; they are decompiled locally during the build.
