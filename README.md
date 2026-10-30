<div align="center">

<img src=".github/assets/tessera-logo.svg" alt="Tessera logo" width="112" height="112">

# Tessera

**A Folia fork with fixes and performance work for large survival servers.**

English | [Русский](README.ru.md)

[![Build](https://img.shields.io/github/actions/workflow/status/denfry/tessera/release.yml?branch=main&label=build)](https://github.com/denfry/tessera/actions/workflows/release.yml)
[![Release](https://img.shields.io/github/v/release/denfry/tessera?include_prereleases&sort=semver)](https://github.com/denfry/tessera/releases)
[![License](https://img.shields.io/badge/license-GPL--3.0-blue)](PATCHES-LICENSE)
[![Java 25](https://img.shields.io/badge/Java-25-orange)](https://adoptium.net/)
[![Minecraft 26.3](https://img.shields.io/badge/Minecraft-26.3-62b47a)](https://minecraft.net/)
[![Upstream: Folia](https://img.shields.io/badge/upstream-PaperMC%2FFolia-2f81f7)](https://github.com/PaperMC/Folia)

[Website](https://denfry.github.io/tessera/) · [Download](https://github.com/denfry/tessera/releases) · [Patches](PATCHES.md) · [Plugins](PLUGINS.md)

</div>

Tessera is a fork of [Folia](https://github.com/PaperMC/Folia) (regionised multithreading on top of
[Paper](https://github.com/PaperMC/Paper)) with bug fixes, performance work and a few features for
large survival servers.

> [!NOTE]
> Early stage, still in testing; not production-ready yet. What is planned next is in [BACKLOG.md](BACKLOG.md).

## Highlights

- **Scoreboards** — the scoreboard is thread safe: per-player boards, `Player#setScoreboard`, teams and
  objectives work from any thread, and so do `/team` and `/scoreboard`.
- **Teleport events** — `PlayerTeleportEvent`, `EntityTeleportEvent` and portal events fire for async
  teleports, portals and ender pearls.
- **Worlds on the fly** — `Bukkit.createWorld` and `unloadWorld` work while the server is running.
- **Fixes** — ender pearls and stasis chambers, MiniHUD debug subscriptions, dragons away from 0,0,
  villagers in portals, region ownership in mob AI, autosave of maps and new players, network hardening.

The full list, with upstream issues, is in [PATCHES.md](PATCHES.md).

## Why Tessera

Folia splits the world into independently ticked regions, which lets a single server use many cores.
Upstream moves carefully, and some fixes that matter on a busy survival server take time to land.
Tessera carries those changes as small, documented patches on top of Folia, so each one can be
reviewed, dropped or sent upstream on its own.

## Goals

- Track upstream Folia closely; every Tessera change is a separate, documented patch.
- Bug fixes (dupes, crashes, region-ownership violations) that upstream has not taken yet.
- Optimisations that keep vanilla behaviour unless a config option says otherwise.
- Nothing that silently breaks plugins written for the Folia API.

## Plugins

By default Tessera runs only plugins that declare `folia-supported: true`. Paper's API already ships the
Folia schedulers (`getRegionScheduler()`, `getGlobalRegionScheduler()`, `getAsyncScheduler()`,
`Entity#getScheduler()`), so a plugin written against them runs unchanged on Paper, Leaf and Tessera.

Plugins without the flag can be loaded in compatibility mode: list them under `compat.plugins` in
`config/tessera.yml` (or use `"*"`). Their `BukkitScheduler` tasks then run on the global region thread.
Such a task can read and change blocks and entities in loaded chunks: the regions it touches are paused
until it finishes (see [COMPAT.md](COMPAT.md)). Plugins marked as Folia supported are not affected.

## Download

Builds are published on the [Releases](https://github.com/denfry/tessera/releases) page. Every push
to `main` is also built by the [Release workflow](https://github.com/denfry/tessera/actions/workflows/release.yml);
the paperclip jar is attached to each run as an artifact.

Run it like any Paper server jar (Java 25 required):

```bash
java -Xms4G -Xmx4G -jar server.jar --nogui   # server.jar = the downloaded *-paperclip-*.jar
```

The console log style is set with `-Dtessera.log.style=<style>` or the `TESSERA_LOG_STYLE` environment variable:
`pretty` (default, `12:34:56 INFO  [world 12,-4] [Plugin] message`, with the region the line came from) or `classic` (the Paper format, `[12:34:56 INFO]: [Plugin] message`).
Stack traces in `pretty` are shortened (reflection and netty frames folded, plugin frames marked with the jar name); `logs/latest.log` keeps the Paper format and full traces in every style.
Color follows `-Dterminal.ansi`; without it, `NO_COLOR=1` turns color off and `FORCE_COLOR=1` turns it on when the
console is not a TTY (Pterodactyl containers are detected automatically).

## Building

Requires Git and JDK 25 (Gradle downloads one if missing).

```bash
./gradlew applyAllPatches
./gradlew createPaperclipJar   # separate run: the task exists only after patching
```

The jar ends up in `folia-server/build/libs/*-paperclip-*.jar`.

## Working on patches

Layout is inherited from Folia so upstream merges stay cheap:

- `folia-server/minecraft-patches/` — patches to Minecraft sources (`features/` = per-feature).
- `folia-server/paper-patches/` — patches to Paper server sources.
- `folia-api/paper-patches/` — patches to the API.

Tessera patches go after the upstream Folia patches in each directory; paperweight numbers them in
order on every rebuild. Workflow:
edit sources under `folia-server/src/minecraft` or `paper-server`, commit there, then rebuild the
patch files with `./rb.sh` (`rb.bat` on Windows).

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow and patch conventions.

## Tessera patches

Every change Tessera makes on top of Folia is listed in [PATCHES.md](PATCHES.md), with the area it
touches and a link to the matching upstream issue or PR where there is one.

Third-party plugins checked on Tessera, and how well they work, are listed in [PLUGINS.md](PLUGINS.md).

## Upstream relationship

Tessera tracks [PaperMC/Folia](https://github.com/PaperMC/Folia) and merges its version branches
regularly. Almost all of the work in this repository belongs to the Folia and Paper teams, and in
particular to [Spottedleaf](https://github.com/Spottedleaf), who designed and wrote Folia's region
threading. If a bug reproduces on stock Folia, please report it [upstream](https://github.com/PaperMC/Folia/issues).

Updating upstream:

```bash
git fetch upstream
git merge upstream/ver/<version>
./gradlew applyAllPatches   # fix conflicts, then rebuild patches
```

## Reporting issues

- Bugs, crashes and performance problems: [open an issue](https://github.com/denfry/tessera/issues/new/choose)
  and include the full `/version` output.
- Bugs that also happen on stock Folia: report them to [PaperMC/Folia](https://github.com/PaperMC/Folia/issues).
- Dupes, crash exploits and other security problems: report privately, see [SECURITY.md](SECURITY.md).

## License

Patches are licensed under the terms in [PATCHES-LICENSE](PATCHES-LICENSE), same as Folia.
Minecraft sources are not distributed; they are decompiled locally during the build.
