# Tessera patches

Changes Tessera carries on top of [Folia](https://github.com/PaperMC/Folia). Upstream Folia and Paper
patches are not listed here.

| Patch | Area | Description | Upstream ref |
|-------|------|-------------|--------------|
| [0012-Fix-ender-pearl-teleport-and-stasis-behaviour](folia-server/minecraft-patches/features/0012-Fix-ender-pearl-teleport-and-stasis-behaviour.patch) | entities, teleport | Pearls survive dimension change, stasis chambers work, damage event reports the pearl as damager | [#421](https://github.com/PaperMC/Folia/issues/421), [#438](https://github.com/PaperMC/Folia/issues/438) |
| [0013-Disable-debug-subscriptions](folia-server/minecraft-patches/features/0013-Disable-debug-subscriptions.patch) | region threading | Debug subscriptions (MiniHUD) no longer crash the server through a global map | [#472](https://github.com/PaperMC/Folia/issues/472), [#432](https://github.com/PaperMC/Folia/issues/432) |
| [0014-Respect-world-spawn-when-spawnRadius-is-0](folia-server/minecraft-patches/features/0014-Respect-world-spawn-when-spawnRadius-is-0.patch) | gameplay | `spawnRadius 0` spawns exactly at the world spawn | [#401](https://github.com/PaperMC/Folia/issues/401) |
| [0015-Autosave-maps-from-the-server-global-data-storage](folia-server/minecraft-patches/features/0015-Autosave-maps-from-the-server-global-data-storage.patch) | saving | Map data is autosaved again from the global tick | [#505](https://github.com/PaperMC/Folia/issues/505) |
| [0016-Validate-region-ownership-in-AI-behaviours](folia-server/minecraft-patches/features/0016-Validate-region-ownership-in-AI-behaviours.patch) | entities, region threading | AI sensors and behaviours skip entities and blocks owned by another region | [#523](https://github.com/PaperMC/Folia/pull/523), [#525](https://github.com/PaperMC/Folia/pull/525), [#526](https://github.com/PaperMC/Folia/pull/526), [#527](https://github.com/PaperMC/Folia/pull/527), [#495](https://github.com/PaperMC/Folia/pull/495) |
| [0017-Do-not-serialise-village-distance-lookups-between-re](folia-server/minecraft-patches/features/0017-Do-not-serialise-village-distance-lookups-between-re.patch) | perf | Village distance lookups use a read/write lock instead of one world-wide monitor | [#530](https://github.com/PaperMC/Folia/issues/530) |
| [0007-Make-the-player-visibility-map-thread-safe](folia-server/paper-patches/features/0007-Make-the-player-visibility-map-thread-safe.patch) | API | `hidePlayer`/`showPlayer` state is safe across regions | [#406](https://github.com/PaperMC/Folia/issues/406) |
| [0008-Make-the-mob-goal-type-cache-thread-safe](folia-server/paper-patches/features/0008-Make-the-mob-goal-type-cache-thread-safe.patch) | API | Mob goal API no longer races on its type cache | [#522](https://github.com/PaperMC/Folia/pull/522) |

## Numbering

Tessera patches come after the upstream patches in each directory. Paperweight assigns the
numbers on every rebuild, so a number can shift after an upstream merge; the patch name stays.

## Where the files live

| Directory | What it patches |
|-----------|-----------------|
| `folia-server/minecraft-patches/features/` | Minecraft server sources (`folia-server/src/minecraft/java`) |
| `folia-server/paper-patches/features/` | Paper server sources (`paper-server`) |
| `folia-api/paper-patches/features/` | Paper API sources (`paper-api`) |

## Columns

- **Patch** — file name without the directory, linked to the file.
- **Area** — the subsystem touched: `region threading`, `chunk system`, `entities`, `inventory`,
  `teleport`, `scheduler`, `API`, `config`, `perf`, and so on.
- **Description** — one line: what changes for a server owner or plugin author.
- **Upstream ref** — `PaperMC/Folia#NNN` (or a Paper issue/PR) if the patch ports or addresses
  something upstream; `—` if it is Tessera-only.
