# Tessera backlog

Bugs and features for Tessera. Each item can be handed to an implementer as is: it has context, where to look, what
counts as done and how to check. Finished items move to the "Done" section and to [PATCHES.md](PATCHES.md).

Priorities: **P0** first (a large server cannot do without it), **P1** visible to players or crashes the server, **P2** performance
and convenience, **P3** someday.

---

## How to take a task (read it in full before starting)

The workflow, code rules and test harness are in [AGENTS.md](AGENTS.md); patch rules and headers in
[CONTRIBUTING.md](CONTRIBUTING.md). For a task from this list:

1. **Reproduce first.** Check that the problem still happens on the current build. If it does not, write "Not
   reproducible on 26.3" with what was checked and move the item to "Done".
2. **Patches.** One patch per fix. Commit messages in the nested repositories are in English, Paper style: title, a "why"
   paragraph, then `Fixes PaperMC/Folia#N` and, if the code comes from someone else's PR, `Based on PaperMC/Folia#N (author)`.
3. **Testing.** Reproduce on the old build and confirm the fix on the new one with `tools/testserver.sh`, bots
   (`tools/joinbot.py`) and, where the Bukkit API is involved, a small test plugin. The log must have no new `ERROR` or
   exception. Say what needs a real client and was not checked.
4. **After.** A row in PATCHES.md, the item moves to "Done".
5. **Plugins.** Every third-party plugin run on Tessera is recorded in [PLUGINS.md](PLUGINS.md) (status, version,
   Tessera build, what is broken). Public plugins only.

---

## P0 — first

---

## P1 — visible to players

### T-019 Corruption of drawn maps — [#177](https://github.com/PaperMC/Folia/issues/177)
- **Why.** Affects ImageFrame on main.
- **Where.** `MapItemSavedData` (map data shared with the server after #505), `HoldingPlayer`, `MapItem#update`. The map
  is updated by several regions at once, `colors[]` and `dirty` are not synchronized.
- **Done when.** A map hanging in frames in different regions and held by players does not get corrupted. Access to `MapItemSavedData`
  is thread-safe or happens on a single owner.
- **Checked (2026-10-30).** The hypothesis about unsynchronized `colors[]`/`dirty` is outdated: all access to
  `MapItemSavedData`, `HoldingPlayer`, `CraftMapView` is under `synchronized`; `MapIndex` is atomic, `dirty` is volatile; maps
  are written only from the global tick (0015), writes are chained. No cause found in the code. Fresh lead from the issue
  (1.21.4): a locked map gets corrupted if you teleport without clicking it in the inventory. Needs a real client:
  cartography table → lock → teleport to another region/world → look at the map and the `data/map_N.dat` file.
  Also check: `ServerLevel#getMapData` calls `MapInitializeEvent` inside `ConcurrentHashMap.computeIfAbsent` —
  a plugin that touches another map in the handler (ImageFrame) may get `Recursive update`.

### T-025 Villagers detect their workstation incorrectly — [#127](https://github.com/PaperMC/Folia/issues/127)
- **Where.** `AssignProfessionFromJobSite`, `AcquirePoi`, `PoiManager` (adjacent to the already done AI and POI patches).

---

## P1 — crashes and hangs
- **Checked (2026-10-30).** Not reproducible: closed room, 8 unemployed villagers and 8 lecterns, player nearby
  (without a player villager AI barely ticks due to activation range — same on Paper). Tessera and Paper 26.3 (build 231) behave
  the same: all lecterns taken in ~8 s, not a single `LOSING_JOB` in 4 min. Not checked: day/night cycle, unloading and
  loading the farm chunks, villagers at a region border, a multi-hour run. If it comes up again, a world with the farm is needed.

### T-034 Hangs and spontaneous shutdown — [#447](https://github.com/PaperMC/Folia/issues/447), [#437](https://github.com/PaperMC/Folia/issues/437), [#196](https://github.com/PaperMC/Folia/issues/196)
- Few logs in the issues. Need watchdog dumps from live servers on Tessera.
- Watchdog improved (0053, in "Done"). Remaining: collect hang dumps from live servers and analyze them.

### T-035 End credits
Rest of the item about minor races (the rest is in "Done").
- **Not reproducible on 26.3.** "Hero of the Village" after a raid: Folia already applies the effect on the hero's thread ("Fix off
  region raid heroes"). Moonrise#130: the index in `ParallelSearchRadiusIteration` does not go past the table — load
  distance is capped at `MAX_VIEW_DISTANCE + 1` in the setters, the table is sized for `MAX_VIEW_DISTANCE + 3`.
- **What.** Folia currently does not show credits at all (`seenCredits = true`, TODO in `endPortalLogicAsync`): the player is
  moved straight to the overworld. Bring credits back: first respawn in the overworld (`respawn(..., alive = true)`), then
  `WIN_GAME`, a repeated `PERFORM_RESPAWN` after the credits does nothing.
- **Done when.** Checked with a real client: credits are shown once, after them the player is in the overworld, not in
  the End void.

---

## P2 — performance

### T-042 Asynchronous pathfinding
- Compute `PathNavigation` / `PathFinder` off the region thread from a block snapshot, apply the result in the tick.

### T-045 Portals linking the nether and the overworld on one thread — [#469](https://github.com/PaperMC/Folia/issues/469)
- Option: overworld and nether regions linked by a portal tick on one thread (farms and contraptions at portals). Discuss
  the design first.

## P3 — later

- **T-211** Minor races from the 2026-10-31 audit, none of them traced to a crash: `CraftPlayer#pluginWeakReferences` (static `WeakHashMap`
  behind `hidePlayer`, a missed `remove` leaves a player hidden; patch paper 0007 covers only the per-player map), the
  statistic API in `CraftPlayer` and `CraftOfflinePlayer` (no thread check, parallel offline updates overwrite each other),
  `RandomSequence` shared by regions rolling one loot table, `LivingEntity#getLastHurtByPlayer` and `getKiller()` returning a
  player of another region. `WorldBorder` is still marked "TODO make this shit thread-safe": `extent` is a plain field,
  ticked on the global thread and written by `CraftWorldBorder` from any thread, and a border shared by players in two regions
  ticks in both. Not traced: `CraftWorld#setSpawnLocation`, `setDifficulty`, `CraftDragonBattle`.
- **T-212** Commands still disabled in `Commands.java`: `bossbar`, `clone`, `data`, `datapack`, `function`, `item`, `loot`,
  `schedule`, `spectate`, `spreadplayers`, `tag`, `teammsg`, `tick`, `waypoint`. Boss bars (0031) and command
  storage (0032) are already thread-safe, so `bossbar` and `data storage` are the closest. Datapack `#tick` and `#load` functions (`getFunctions().tick()` is commented out in `MinecraftServer`), `/schedule`
  events and command blocks (`BaseCommandBlock#performCommand` returns `false`) do not run at all; design first.
- **T-214** `MinecraftServer#tickables` never run (`if (false)` in the tick), so the server GUI player list does not update
  ([#464](https://github.com/PaperMC/Folia/pull/464)).
- **T-054** JSON logs for Loki/ELK (deferred until there is Grafana/ELK): a `json` style in `TesseraLogStyle` (one JSON line per event
  to stdout) and `-Dtessera.log.json-file=true` → `logs/latest.json` with rotation like `latest.log`. ECS via `log4j-layout-template-json`;
  fields `@timestamp`, `log.level`, `log.logger`, `message` without `§`/ANSI, `process.thread.name`, `tessera.plugin`, context data from T-052
  (`tessera.region.*`, `tessera.global`), `error.type` / `error.message` / `error.stack_trace`. Done when `jq` and Promtail/Filebeat
  parse the logs without custom regex; document in README.
- **T-060** Automatic upstream Folia merge ([#468](https://github.com/PaperMC/Folia/issues/468)): a weekly workflow
  creates an `upstream-sync` branch, merges PaperMC/Folia, runs `applyAllPatches` and the build, and opens a PR.
- **T-061** Chunk API messages ([#96](https://github.com/PaperMC/Folia/issues/96)): clear errors when synchronous API
  is called from the wrong thread (which thread, which region, what to use instead).
- **T-062** Version check for Tessera: `/version` currently prints "Unknown version". Check against GitHub Releases of
  `denfry/tessera`.
- **T-063** CI: run `tools/joinbot.py` against the built jar in Actions (server, two bots, join and leave, shutdown without ERROR).
- **T-066** Teleport event edge cases (after T-002): for a portal, `PlayerTeleportEvent` gets an approximate exit (the portal is not found yet);
  with `canCreatePortal=false` and no portal the entity is placed at the search point instead of staying in place as on Paper; the rollback
  after a cancelled `PlayerMoveEvent` goes through `teleportAsync` and itself fires `PlayerTeleportEvent`, which can be cancelled.
- **T-064** World unload edge cases (after T-001): an entity or player whose async teleport into the world started before `unloadWorld`, and a join of a player saved in that world during the unload. Currently `unloadWorld` checks only players in the world and forbids new `teleportAsync` into it. While the world is saving, the global thread waits (0.1–1.4 s in tests). Reference: Canvas `unloadWorldAsync`: a counter of players entering the world (counted in `PrepareSpawnTask`, released on disconnect), unloading on a separate thread, entities teleporting into the world are returned to their origin.

---

## Directions — big features

Five directions that set Tessera apart from other Folia forks. Each is split into tasks that can be taken one at a time.
Order: A, then B (grows out of T-003), D, E. C is months of research, start it after A and B.

### A. Regular Bukkit plugins on Folia (T-100)

Currently a plugin without `folia-supported: true` does not load, and `Bukkit.getScheduler()` throws
`UnsupportedOperationException`. The goal is for most simple plugins to work without rewriting. Everything is enabled
by an option and only for listed plugins. Plugins written against the Folia API are not affected.

#### T-101 Compatibility mode: loading plugins without `folia-supported` — done
- **Where.** `SpigotPluginProviderFactory#build`, `PaperPluginProviderFactory#build`, `CraftMagicNumbers#checkSupported`.
- **What.** Config option `compat.plugins` (list of names or `*`), empty by default. Such a plugin loads with a
  warning in the log. There is `TesseraCompat.isCompat(Plugin)`, the other tasks build on it.
- **Done when.** Without the option, behaviour is unchanged. With the option EssentialsX loads, with one warning about the plugin in the log.

#### T-102 `BukkitScheduler` on top of Folia schedulers — done
- **Where.** `CraftScheduler` (`handle` throws `UnsupportedOperationException`), `CraftServer#getScheduler`.
- **What.** For plugins in compatibility mode, sync tasks (`runTask*`, `scheduleSync*`, `callSyncMethod`,
  `getMainThreadExecutor`, `BukkitRunnable`) go to `GlobalRegionScheduler`, async ones to `AsyncScheduler`.
  Task ids, `cancelTask`, `cancelTasks`, `isQueued`, `isCurrentlyRunning`, `getPendingTasks` work, tasks are cancelled when the plugin is disabled.
  For other plugins Folia behaviour is unchanged (exception).
- **Done when.** A test plugin without `folia-supported` with a timer, delayed, async and cancelled task and
  `callSyncMethod` works. Plugin tasks are removed in `onDisable`.

#### T-103 World and entity calls from the wrong thread — done (T-103a, T-103b, T-103c, T-103d, T-103e)
- **Why.** A T-102 task runs on the global thread, while `Block#setType`, `Entity#teleport`, inventories may only be touched
  on the region thread. Without this a plugin fails on its first world change.
- **Design: [COMPAT.md](COMPAT.md)** (region borrowing). Below are the original ideas that were dropped:
  - changes without a result (`setType`, `setHealth`, `addPotionEffect`) — run on the owner later;
  - synchronous `teleport` — via `teleportAsync`, return `true`;
  - reads (`getType`, `getLocation`) — allow stale reads where safe, otherwise an exception with a clear message;
  - the global thread waiting on a region is forbidden (deadlock).
- **Where.** `TickThread.ensureTickThread` checks in `CraftBlock`, `CraftEntity`, `CraftWorld`, `CraftInventory*`.
- **Done when.** The main EssentialsX commands work (`/tp`, `/home`, `/heal`, `/give`, `/spawn`).
- **T-103e.** Brigadier commands of a compatibility-mode plugin (Paper API or straight into the dispatcher, like Skript)
  run the same way as Bukkit commands in T-103b. Done.
- **Remaining.** `skript reload all` re-registers commands while the Paper Async Command Builder pool walks the tree
  (`Commands#fillUsableCommands` → `CommandNode#hashCode`): `ConcurrentModificationException`, the player gets the old
  command tree. Synchronize registration from compatibility mode with tree building, or resend the tree afterwards.

#### T-105 Cross-region operations
- `openInventory` of a container in a foreign region, teleport with passengers, `getNearbyEntities` at a region border,
  `World#getEntities` from a plugin task (per-region snapshot).

#### T-106 Run against real plugins
- Plugins from PLUGINS.md with status "needs Folia build": EssentialsX, LevelledMobs, InvSee++, FAWE, etc. For each,
  record the status in compatibility mode.

#### T-107 Paper fields and API missing in Folia
- `MinecraftServer.currentTick` restored (global region ticks). Done.
- Delay 0 in Folia schedulers from a compatibility-mode plugin means the next tick, as in `BukkitScheduler`
  (InvSee++ switches to the Folia API itself and passes 0). Done.
- Remaining: `MinecraftServer#execute` / `MCUtil.MAIN_EXECUTOR` (FAWE adds tickets through it), `Server#getTickTimes`
  and `getAverageTickTime` off the region thread (TabTPS shows MSPT 0 and `Long.MAX_VALUE`).

### B. Lag attribution (T-110)

Builds on T-003 (per-region report and MBean).

- **T-111 Plugin time per region.** Time of event handlers and scheduler tasks broken down by "region × plugin"
  (wrapper around `EventExecutor` and `Folia*Scheduler` tasks). Overhead: no more than a couple percent of MSPT.
- **T-112 Time per entity and block entity type in a region.** Summary from the existing Folia profiler without taking a full profile.
- **T-113 `/tessera lag`.** Heaviest regions, plugins and entity types with coordinates, click to teleport.
- **T-114 Export.** T-111 and T-112 numbers in the T-003 MBean (Prometheus via jmx_exporter).
- **T-115 Spike detector.** If a region tick exceeds a threshold, a short region profile is written to a file automatically.

### C. Horizontal scaling (T-120) — research

Folia regions are already isolated, the next step is spreading them across processes. This is months of work, design only until a prototype.

- **T-121 Design document.** Study MultiPaper: who owns a region, ownership handoff, shared storage, moving a player
  through the proxy (transfer packet 1.20.5+), what to do with entities on the border.
- **T-122 Prototype.** Two processes, one world, static split by coordinates, the player moves between nodes via Velocity.
- **T-123 Global state across nodes.** Time, weather, scoreboard, player list, chat.
- **T-124 Region migration between nodes by load.**

### D. World storage (T-130)

- **T-131 Region storage abstraction.** An interface over reading and writing region files in Moonrise, to plug in other formats.
- **T-132 Linear format.** Config option and a converter both ways.
- **T-133 Snapshots.** Live world backup, without stopping and without an MSPT spike.
- **T-134 Area rollback from a snapshot.** Online, on the region owner thread: unload chunks, replace, load.

### E. Event recording (T-140)

- **T-141 Region journal.** Ring buffer of incoming player packets, block changes, entity spawns and removals.
  Flushed to a file on command or when a region crashes.
- **T-142 Item tracing for dupe hunting.** Item appearance, merging, pickup and transfers between containers with
  stack id. A practical substitute for full replay.
- **T-143 Deterministic replay — research.** Vanilla is nondeterministic (RNG, task order across threads). Estimate
  what is needed: per-region RNG, recording all inputs. Report only.

---

## Done

| What | Issue / PR | Patch |
|---|---|---|
| Ender pearl: dimension change, stasis chambers, damager | #421, #438 | 0012 |
| Debug subscriptions (MiniHUD) crashed the server | #472, #432 | 0013 |
| `spawnRadius 0` | #401 | 0014 |
| Map autosave | #505 | 0015 |
| Region checks in AI | #523, #525, #526, #527, #495 | 0016 |
| Village POI without a shared lock | #530 | 0017 |
| Chat during shutdown | #461 | 0018 |
| `playersByName` is thread-safe | #497 | 0019 |
| Autosave of unsaved players | #459 | 0020 |
| Ender dragon parts | #427, #504 | 0021 |
| Villagers in portals ("World mismatch") | #431 | 0022 |
| Protocol switch does not block threads, finish_configuration spam | #454, #520 | 0023 |
| World cleanup from `onDisable` | #353 | 0024 / paper 0009 |
| Thread-safe hide/showPlayer | #406 | paper 0007 |
| Mob target type cache | #522 | paper 0008 |
| Tessera branding, GitHub Release for every build | — | build.gradle.kts.patch, release.yml |
| World loading and unloading (`createWorld` / `unloadWorld`), T-001 | #134 | 0025 / paper 0010 |
| `PlayerTeleportEvent` / `EntityTeleportEvent` and portal events for async teleports, T-002 | #490, #330 | 0026 / api 0005 |
| Thread-safe scoreboard: personal boards, teams, `/team`, `/scoreboard`, T-004 | #25 | 0027 / paper 0011 |
| `PlayerBucketEmptyEvent` result is per thread, T-027 | — | 0028 |
| Region report (`getRegionReport`, `getRegionReports`) and JMX `dev.tessera:type=Region`, T-003 | #299, #398 | 0029 / paper 0012 / api 0006 |
| Built-in spark for regions: region thread profile, TPS of the slowest region, T-037 | #299 | paper 0013 |
| Console log style choice (`pretty` / `classic`), T-050 | — | paper 0014 |
| `pretty` colors: level, plugin tag, `NO_COLOR` / `FORCE_COLOR`, Pterodactyl, T-051 | — | paper 0015 |
| Region in the `pretty` log line (`[world x,z]`, `[global]`, `[global > world x,z]` for borrowed), T-052 | — | paper 0016 |
| Short stack traces in `pretty`: folding reflection/netty/log4j/scheduler, plugin frames with the jar name, tail below the last plugin frame → `... N more`, T-053 | — | paper 0017 |
| With `max-players=N` exactly N players can join (previously N−1), T-036 | — | 0030 |
| Boss bars and `/data storage` are thread-safe (`ServerBossEvent`, `CustomBossEvents`, `CommandStorage`), T-035 | — | 0031, 0032 |
| `LevelStorageSource.resources` is a `ConcurrentHashMap`, T-035 | — | 0033 |
| Respawn anchor consumes a charge again, charged on the anchor's region, T-035 | — | 0034 |
| Treasure map to a target structure no longer crashes (`tryReference`), T-035 | — | 0035 |
| Advancement triggers for target block, curing a zombie villager and picking up a thrown item run on the player's thread, T-035 | — | 0036 |
| `getRespawnLocation()` with a point in another world or region returns the saved point instead of `World mismatch`. `setRespawnLocation` itself does not erase the point on 26.3: with `forced` it survives death and rejoin, without `forced` and without a bed/anchor it is reset, as on Paper, T-011 | #337 | paper 0018 / api 0007 |
| `PlayerRespawnEvent` / `PlayerPostRespawnEvent` are fired again (after death and when leaving the End), on the respawn point's region. A mounted player leaves the End to the world spawn, as in vanilla; the vehicle gets `EntityPortalEvent` (T-002), T-012 | #453 | 0037 |
| The fishing bobber is removed when the player moved to another world or region (previously it hung forever); `player.fishing` is cleared only on the player's thread, the rod can be cast again right away, T-014 | #435 | 0038 |
| `teleportAsync` with `TeleportFlag.Relative.VELOCITY_*` keeps velocity (with `VELOCITY_ROTATION` it rotates it), as on Paper: in its own region, in a foreign one and in another world; for players the flags go into the position packet. Without flags velocity is reset, as on Paper, which is the way to reset it. A listener that changes the destination in the teleport event resets velocity, T-015 | #441 | 0039 / paper 0019 |
| The first pearl into a new end gateway reaches the outer islands: a gateway in the End without an exit looks for it in advance when a player is near (32 blocks), and pearls and other entities (not players) that enter before the exit is found wait inside the gateway. A player who enters the gateway before the search finishes is still not teleported on the first try, T-016 | #51 | 0040 |
| Wither roses drop again if the wither skull went through a portal or into another region: the victim remembers the wither skull hit and, on death without a killer within 100 ticks, drops a rose. A wither in another region does not heal from the kill, damage of such a skull stays 5, T-018 | #388 | 0041 |
| The locator bar (`locator_bar`) works again: waypoints are tracked across regions, each player updates their links once per tick on their own thread, like vanilla on movement; checked with bots: track/update/untrack in own and foreign region, turning the rule off and on, T-020 | #370 | 0049 |
| BlockState from ItemMeta with coordinates 0,0,0 — not reproducible on 26.3: the state from `BlockStateMeta#getBlockState()` is not bound to a world (`isPlaced() == false`), inventory, `update()` and `setBlockState` work, `open()`/`close()` throw "must be placed", as on Paper; there is no thread check on 0,0,0 (chest, barrel, shulker, furnace, beehive), T-023 | #328 | — |
| Hoppers do not pick up items — not reproducible, behaviour matches Paper 26.3: picking up falling items across chunk and region borders (1533/1536 vs 1532/1536), hopper chains with comparators match item for item, the farm from the issue "leaks" the same way on 26.3 and on Paper. Locking the bottom hopper with a torch in a classic sorter was not checked separately, T-010 | #209 | — |
| Note blocks do not react to redstone and do not change pitch — not a Folia bug: this is the Paper setting `block-updates.disable-noteblock-updates: true` (and `disable-tripwire-updates` for tripwires), enabled by ItemsAdder/Oraxen/Nexo. With default settings on Tessera a note block plays from redstone (NotePlayEvent) and pulses an observer the same as on Paper 26.3; with the setting, the same symptoms as in the issue, T-013 | #470 | — |
| Compatibility mode: plugins without `folia-supported` and `BukkitScheduler`, T-101, T-102 | — | 0042 / paper 0020 |
| Region borrowing: compatibility-mode plugin tasks change blocks and entities, T-103a | — | 0043 / paper 0021 |
| Compatibility-mode plugin commands run on the global thread with region borrowing, T-103b | — | paper 0022 |
| Synchronous `teleport` for compatibility-mode plugins via `teleportAsync`, T-103c | — | paper 0023 |
| Synchronous chunk load for compatibility-mode plugins (PaperLib in EssentialsX), T-103d | — | 0044 |
| Brigadier commands for compatibility-mode plugins (Skript), T-103e | — | 0045 / paper 0024 |
| `MinecraftServer.currentTick` for plugins, T-107 | — | 0046 |
| Delay 0 in Folia schedulers from compatibility-mode plugins (InvSee++), T-107 | — | 0047 / paper 0025 |
| `/dialog show` / `/dialog clear` are back, the dialog is sent on the player's thread. Conversation API works: chat input during a conversation goes to the conversation on the player's thread (previously `UnsupportedOperationException` and broken chat), the `withTimeout` timeout runs on the conversing entity's scheduler rather than the Bukkit scheduler, T-021 | #434, #216 | 0048 / api 0008 |
| Extra nether portals — not reproducible on 26.3: 6 and 30 items into a new portal in one tick, two portals with 10 items each into the same nether area, and two players at once give exactly one portal on the other side (repeat search before creating, `existingTryAgain`), T-017 | #69 | — |
| A compatibility-mode plugin on a region thread sees only its own region's entities in `World#getEntities` / `getLivingEntities` / `getEntitiesByClass` (LevelledMobs in `PlayerTeleportEvent`), T-109 | — | paper 0026 |
| `/tessera compat` compatibility report: failed thread checks, synchronous teleports and world entity iteration by compatibility-mode plugins — plugin, API method, thread (global, region, other), count and first stack; `/tessera compat <plugin>`, `dump` to a file, `reset`, T-104 | — | paper 0027 |
| Entity interaction rejected before `PlayerInteractEntityEvent` (target in another region, beyond the world border, out of reach, not found) resends the player's inventory and the target's equipment: an allay no longer "takes" an item only client-side, T-022 | #502 | 0050 |
| `recipe_book_add` fails to encode — not reproducible on 26.3, and not Folia: in #303 the `minecraft:equippable` component of a plugin item failed with `null` instead of `Optional` (Paper 1.21.4). Now `CraftEquippableComponent` builds all `Optional`s via `ofNullable`/`empty`; plugin recipes (shaped and shapeless) with such an item as result and ingredient are sent via `/recipe give` without errors, T-024 | #303 | — |
| Block generation error — not reproducible on 26.3: 1024 chunks with one seed, generated one by one and all at once from four corners (different regions), without broken terrain or errors. Only features that write into a neighbouring chunk differ (andesite/diorite/granite patches, ores, icebergs): which overrides which depends on the neighbours' decoration order — two identical parallel runs and vanilla generation with a different load order differ the same way, T-026 | #61 | — |
| Management server (JSON-RPC) works: methods run on the global tick (previously all failed with `UnsupportedOperationException`), connections tick once per global tick, `players/kick` without removing the player from a foreign thread, `server/status` returns `started: true`. Checked status, players, difficulty, gamerules, allowlist, operators, system_message, save, view_distance, kick, stop, T-033 | #416 | 0051 |
| `teleportAsync` from `PlayerJoinEvent` no longer crashes the region: a player who is still joining is teleported on their next tick (another region, another world, same region), a direct `Entity#teleportAsync` call during join returns `false`, T-067 | — | 0052 / paper 0028 |
| On a region hang the watchdog prints the region's chunk, entity and player counts, the thread state, the lock it waits for and its owner, monitors per stack frame and held `Lock`s; the stack of the awaited lock's owner (up to 3 hops) and a `DEADLOCKED` mark. Checked on a deadlock between two regions (monitor + `ReentrantLock`), T-034 | #447, #437, #196 | 0053 |
| Entity with enough velocity to leave its region in one move is teleported on its next tick instead of failing the thread check and being discarded. Reproduced with a vex at 4995 blocks per tick, T-030 | #199 | 0057 |
| Creaking and its heart do not read each other across regions (only possible after a teleport): the creaking no longer dies, T-030 | #203 | 0056 |
| Allay does not read a liked note block in another region, pets do not load chunks to teleport to the owner. Precaution from reading the code: the allay case did not fail on the old build, T-030 | #203 | 0054, 0055 |
| Zombie reinforcements do not load chunks. Crash not reproducible on 26.3: 40 reinforcement rounds at the edge of the loaded area, no errors; foreign targets are dropped by `Mob#asValidTarget`, T-030 | #386 | 0058 |
| Not reproducible on 26.3 or already fixed, T-030: #334 (`BabyFollowAdult`, patch 0016), #152 (fishing hook, patch 0038), #327 (`PlayerList.remove` no longer ticks the player), #199 spectator path (Folia checks the camera). #381 and the log of #203: logs expired, the title of #381 points to a plugin calling `getEntities` off-region. `DragonFireball` needs no check: the gap between regions is wider than its search box | #334, #152, #327, #381 | — |
| Villager behaviours do not wait for POI data on the region thread: `PoiCompetitorScan`, `AssignProfessionFromJobSite`, `YieldJobSite` and `ValidateNearbyPoi` skip the tick when the POI chunk is not loaded and keep the memory. `performance.poi-searches-load-chunks` in `config/tessera.yml` (default `true`, vanilla) keeps the `AcquirePoi` search off the disk. Checked: 4 villagers took 4 lecterns in both modes, no errors. The stall itself was not measured, T-031 | #292 | 0059 / paper 0030 |
| Lock contention: no hot monitor found, no patch. JFR with thresholds of 1 ms, 50 idle bots in about 40 regions, 6 region threads, 2 minutes: 0.07 s in monitors on region threads, 2.7 s in `ThreadedTicketLevelPropagator.await`, 0.4 s in `ThreadedRegionizer` and the rest is the scheduler waiting for work. Not covered: bots do not build or fight and no plugins were loaded, so re-check on a live profile, T-032 | #291 | — |
| Compatibility-mode plugins can use the world in `onEnable`: the startup thread counts as the global tick and borrows regions until `RegionizedServer#init`. Multiverse-Core 5.8.2 loads its config and worlds, `mv tp` to the default and a second world works after a restart, T-108 | — | 0060 / paper 0031 |
| Light tick behind `performance.light-entities` (default `false`): marker and gravity-less armor stands run a full tick once a second, or every tick while burning, riding, carrying a passenger, in a portal or under an effect; viewers of these stands and of display entities are recomputed every `light-entity-tracker-interval` ticks (default 5). Display entities have no server physics to skip. 2000 entities near one bot, region MSPT off/on: marker 9.2/4.0, gravity-less stand 7.0/3.9, display about 3.9/3.5 (within noise), regular stand unchanged. Fire damage, effect expiry and viewer removal after a teleport match with the option off. Not tested: a real client (late appearance is at most interval - 1 ticks), equipment updates reaching a viewer, several viewers, portals, T-040 | — | 0061 / paper 0032 |
| Distant mob AI behind `performance.distant-mob-ai` (default `false`): mobs further than `distant-mob-ai-start-distance` (12) blocks from the nearest player choose goals, run sensors and start behaviours every distance²/256 ticks, at most `distant-mob-ai-max-interval` (20); `distant-mob-ai-exclude` lists entity types to skip. Running goals and behaviours, movement and memory timers tick every tick. With the default entity activation range the effect covers 12 to 32 blocks. 1000 cows and villagers 18 to 30 blocks from one bot, two alternating pairs of runs: median region MSPT 43.9 to 40.6 and 35.7 to 30.7, 8 to 14% lower, mobs moved as far, no errors. Target, hurt and exclude paths were not driven separately; farms and client behaviour were not checked, T-043 | — | 0063 / paper 0034 |
| Region merge radius is configurable: `threaded-regions.merge-radius` in `config/paper-global.yml` (default 1, as before, clamped to 1..16, read at startup) next to `grid-exponent`, both documented in REGION_LOGIC.md. Two bots 2000 blocks apart: 2 regions with radius 1, 1 region of 578 chunks with radius 8, no errors. Performance of larger regions was not measured, T-044 | — | 0062 / paper 0033 |
| Player autosaves are spread over the save interval: without an explicit `player-auto-save.rate` or `max-per-tick`, a region saves players/interval + 1 per tick instead of 20. 30 bots, autosave every 600 ticks: no difference on an idle disk; under constant fsync load the worst tick fell from 3.4 s to 0.31 s and the typical worst tick of an autosave window from about 350 to 270 ms (one run each). Spikes remain under disk load because the write is still synchronous on the region thread. Chunks are already capped at 24 per region tick and maps are saved asynchronously, by reading the code; neither was measured separately, T-046 | — | 0064 / paper 0035 |
| Async entity tracker check behind `performance.async-entity-tracker` (default `false`): in regions with at least 10000 entity and player pairs a pool (`async-entity-tracker-threads`, default a quarter of the CPU threads, at most 4) finds entities whose viewers changed while the region thread waits; the update itself, events and packets stay on the region thread. 100 bots and 3000 cows in one region, 6 region threads, two runs each, off/on. Stationary mobs: tracker 16.5/3.1 ms per tick, median MSPT 47/34. 10% of mobs moving: tracker 17-19.5/4.7 ms, median MSPT 47-54/37-38. With all mobs moving, the Python bots fall behind and time out, so that case has only a JFR profile of the old code: about 45% of tracker time is `sendChanges`, which this does not move. Viewer pairs from `getTrackedBy` match with the option off through a teleport to another region and back, `hideEntity`/`showEntity` and a kick, no tracker errors. Not tested: a real client, several large regions sharing the pool, bots walking, T-041 | — | 0065 / paper 0036 |
| A loan of a region that ends, or fails to start, between a failed acquire and the `isBorrowed` check no longer stops the server: the scheduler tries again. Found by reading the code, the race itself was not reproduced: a compatibility-mode plugin borrowing two regions 40 times a tick ran about 128000 loans in 160 s with 4 region threads and no errors. The old build crashed on T-201 within about 20 s of the same run, so it gives no baseline, T-200 | — | 0066 |
| The wandering trader spawner uses the random of the level instead of one `LegacyRandomSource` shared by all regions; the timer survives region merges and splits (the merge and split path was not driven separately). Three regions, 4 threads, trader timer set to every tick: the old build stopped with `Accessing LegacyRandomSource from multiple threads` within about 20 s, the new one ran 160 s with no errors, T-201 | — | 0067 |
| Management `server/save` queues a save of chunks and players on every region. Before, the call returned `true` and the player file stayed unchanged; now the player file and `r.0.0.mca` are rewritten within seconds. The chunk file of the old run was not compared (the test looked at another dimension). The result means the saves were queued, not finished, T-205 | — | 0068 |
| Recipe changes publish new maps; advancement and recipe book reloads run on each player's thread, at most once a second per player, so clients see a recipe change up to a second later. Plugin adding and removing a recipe every tick with `updateResources`, 5 players in 4 regions, 200 writes and 9 million reads. Old build: `ConcurrentModificationException` while reading recipes, and in `PlayerAdvancements#flushDirty`, which kicked the player. Build without the once-a-second limit: no failures, but 60 bots made per-player reloads pile up until the watchdog fired, which is why the limit was added. Build with the limit: 60 bots for a few minutes without errors; the 30-minute load test and the 200-write test have not been rerun on it yet. A furnace reading recipes during a change was not driven separately, T-203 | [#498](https://github.com/PaperMC/Folia/pull/498) | 0076 / paper 0039 |
| A map read inside `MapInitializeEvent` no longer fails. 64 maps, handler reading the next map: old build `Recursive update` in 21 handlers and 3 direct calls, new build none. Corrupted maps themselves (the rest of #177) are still T-019, T-019 lead | #177 | 0075 |
| Stats and criteria maps are safe from any region. Three regions creating all 9976 stats at once: old build lost 3151 entries, new build none, T-202 | — | 0071 |
| Stats and criteria run on the player's thread. Primed TNT owned by a player in another region, 10 zombies with Resistance: old build 20 stat writes from the foreign region, new build none, and the stats are still counted. `LIGHTNING_STRIKE` was not driven: a bolt and a player within 256 blocks were never in two regions in the test, T-204 | [#496](https://github.com/PaperMC/Folia/pull/496) | 0072 |
| Fast projectiles leave the region through a teleport. Arrow, snowball and fireball at 1000 blocks per tick: old build removes all three (`UNLOAD`, `DISCARD`), new build all three arrive. A fireball at the world edge stops. An arrow and a snowball out of range of players did not tick there, so the failed teleport was seen only on the fireball, T-208 | — | 0073 |
| `World#getRaids` returns the raids of the current region. Old build shows a raid to another region, new build does not, T-209 | — | paper 0038 |
| `/save-all` works: `r.0.0.mca` grew from 777192 to 1746259 bytes. The message means the saves were queued | — | 0074 |
| `reloadData`, `resetRecipes` and `Datapack#setEnabled` fail with a clear message before changing anything (`setEnabled` was checked by reading the code only), T-206 | [#498](https://github.com/PaperMC/Folia/pull/498) | paper 0040 / api 0009 |
| The waypoint transmit range is published by its owner. Two players in two regions: the link drops when the source range falls to 100 and the source stops transmitting at 0. A real client was not used, T-207 | — | 0078 |
| A failed tick thread writes `crash-reports/crash-*-server.txt`. Driven through the uncaught exception path; `regionFailed` shares the helper and was not triggered, T-210 | [#463](https://github.com/PaperMC/Folia/pull/463) | 0079 |
| `stop` read before the worlds load works. `echo stop \| java -jar`: old build NPE and the server keeps running, new build stops, T-065 | — | 0077 |
| Retired callbacks on shutdown: no change needed. Plugins are disabled before players are removed and tasks of a disabled plugin are dropped, as on Paper (by reading the code), T-213 | #479 | — |
| `Entity#remove` from `onDisable`: old build NPE, new build removes the entity. `World#spawn` from a compatibility-mode task and `getCurrentTick` work | — | paper 0037, 0069, 0070 |
