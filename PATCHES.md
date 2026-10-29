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
| [0018-Ignore-chat-once-the-server-starts-shutting-down](folia-server/minecraft-patches/features/0018-Ignore-chat-once-the-server-starts-shutting-down.patch) | shutdown | Chat packets are dropped once regions start halting | [#461](https://github.com/PaperMC/Folia/pull/461) |
| [0019-Make-the-player-name-map-thread-safe](folia-server/minecraft-patches/features/0019-Make-the-player-name-map-thread-safe.patch) | region threading | `playersByName` is a ConcurrentHashMap, like `playersByUUID` | [#497](https://github.com/PaperMC/Folia/pull/497) |
| [0020-Autosave-players-that-were-never-saved](folia-server/minecraft-patches/features/0020-Autosave-players-that-were-never-saved.patch) | saving | Players are autosaved from join; the `now - Long.MIN_VALUE` overflow skipped them | [#459](https://github.com/PaperMC/Folia/pull/459) |
| [0021-Sync-ender-dragon-parts-before-registering-the-drago](folia-server/minecraft-patches/features/0021-Sync-ender-dragon-parts-before-registering-the-drago.patch) | entities | Dragon parts are moved to the dragon before registration, so dragons work outside 0,0 | [#427](https://github.com/PaperMC/Folia/issues/427), [#504](https://github.com/PaperMC/Folia/pull/504) |
| [0022-Do-not-read-the-destination-world-while-copying-a-vi](folia-server/minecraft-patches/features/0022-Do-not-read-the-destination-world-while-copying-a-vi.patch) | entities, teleport | Villagers no longer die with "World mismatch" in portals | [#431](https://github.com/PaperMC/Folia/issues/431) |
| [0023-Do-not-block-tick-threads-on-netty-during-protocol-s](folia-server/minecraft-patches/features/0023-Do-not-block-tick-threads-on-netty-during-protocol-s.patch) | network, security | Protocol switches do not park global/region threads on netty; repeated finish-configuration packets are ignored | [#454](https://github.com/PaperMC/Folia/issues/454), [#520](https://github.com/PaperMC/Folia/issues/520) |
| [0024-Let-plugins-clean-up-the-world-in-onDisable](folia-server/minecraft-patches/features/0024-Let-plugins-clean-up-the-world-in-onDisable.patch), [0009](folia-server/paper-patches/features/0009-Let-plugins-clean-up-the-world-in-onDisable.patch) | shutdown, scheduler, API | Region/entity/global tasks scheduled in `onDisable` run at once on the shutdown thread, owning the target region | [#353](https://github.com/PaperMC/Folia/issues/353) |
| [0025-Allow-worlds-to-be-unloaded-while-the-server-is-runn](folia-server/minecraft-patches/features/0025-Allow-worlds-to-be-unloaded-while-the-server-is-runn.patch), [0010](folia-server/paper-patches/features/0010-Implement-createWorld-and-unloadWorld.patch) | API, region threading | `Bukkit.createWorld` and `unloadWorld` work: on the global region, and `createWorld` also while plugins are enabled on startup. Unload takes the world's regions off the scheduler and saves it like on shutdown | [#134](https://github.com/PaperMC/Folia/issues/134) |
| [0026-Call-teleport-and-portal-events-for-async-teleports](folia-server/minecraft-patches/features/0026-Call-teleport-and-portal-events-for-async-teleports.patch), [api 0005](folia-api/paper-patches/features/0005-Document-teleport-event-threading.patch) | teleport, API | `PlayerTeleportEvent` / `EntityTeleportEvent` fire for every async teleport (`teleportAsync`, `/tp`, ender pearls, portals, gateways) on the origin region thread; cancel and `setTo` (also to another world) work. Portals also fire `EntityPortalReadyEvent` and `PlayerPortalEvent` / `EntityPortalEvent`, whose target and radii drive the portal search | [#490](https://github.com/PaperMC/Folia/issues/490), [#330](https://github.com/PaperMC/Folia/issues/330) |
| [0007-Make-the-player-visibility-map-thread-safe](folia-server/paper-patches/features/0007-Make-the-player-visibility-map-thread-safe.patch) | API | `hidePlayer`/`showPlayer` state is safe across regions | [#406](https://github.com/PaperMC/Folia/issues/406) |
| [0008-Make-the-mob-goal-type-cache-thread-safe](folia-server/paper-patches/features/0008-Make-the-mob-goal-type-cache-thread-safe.patch) | API | Mob goal API no longer races on its type cache | [#522](https://github.com/PaperMC/Folia/pull/522) |

Build branding: the server reports itself as **Tessera** (`Brand-Name`, `/version`). `Brand-Id` stays
`papermc:folia` so plugins that check for Folia keep working.

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
