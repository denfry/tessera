# Compatibility mode: design

How plugins without `folia-supported: true` work on Tessera. Tasks are in [BACKLOG.md](BACKLOG.md), section "Directions", A.

## What already exists (T-101, T-102)

Plugins listed in `compat.plugins` in `config/tessera.yml` are loaded. Their sync `BukkitScheduler` tasks run on the
global region thread, async ones in the Bukkit pool. Plugins with Folia support are not affected.

## Problem (T-103)

A plugin task on the global thread cannot touch blocks and entities: every entity `getHandle()` and every `CraftBlock`
method calls `TickThread.ensureTickThread(...)`, and the check fails because the global thread owns no region. There
are more than two hundred such checks in CraftBukkit.

## Options

1. **Intercept every API method** (apply changes later on the owner, turn `teleport` into `teleportAsync`).
   Rejected: the checks live in `getHandle()`, not at method boundaries, so hundreds of places would need changes. Reads
   (`getType`, `getHealth`) cannot be done this way at all.
2. **Rerun the task on the owning region after the exception.** Rejected: everything the task did before the
   exception (messages, counters, database writes) would run a second time.
3. **Stop all regions while plugin tasks run** (like the Paper main thread). Works, but every tick with such tasks
   stops the whole server, and it needs a mechanism to stop and resume the whole scheduler.
4. **Region loans — chosen.** A plugin task acquires only the regions it actually touches, and only for the
   duration of its execution.

## Region loans

World unloading (T-001) already works in a similar way: the global thread acquires regions via
`ThreadedRegion#tryMarkTicking`, after which no scheduler thread can tick them.

1. **Scope.** `TesseraCompat` wraps the execution of a compat-mode plugin's sync task.
   Outside this scope behavior is unchanged: an exception. Folia plugins never enter it.
2. **Entry point.** The failure branch in `TickThread.ensureTickThread(...)` (for position, chunk and entity). If the
   thread is inside the scope, `TesseraCompat.borrow(world, chunkX, chunkZ)` is called. If the loan succeeds, the check
   passes, otherwise an exception as before. Passing checks cost nothing: code is added only to the failure branch.
3. **Acquisition.** The region is looked up by chunk (`regioniser.getRegionAtUnsynchronised`). If there is no region
   (chunk not loaded), the chunk gets a region (T-103d, see below). If the region is ticking right now, the global thread
   waits for the tick to end (`tryMarkTicking` in a loop) for at most 500 ms, then an exception.
4. **Context.** The global thread is also a `TickThreadRunner`. After acquisition it gets the current region set
   (`currentTickingRegion` and the region's world data), and all checks and `getCurrentWorldData()` work as if the
   code were running in that region's tick. Accessing another acquired region switches the context to it.
5. **Release.** At the end of the task (including on exception) all acquired regions are released
   (`markNotTicking`, which runs deferred merges and splits), and the context is reset.
6. **Scheduler.** Currently, if a scheduled tick cannot acquire a region, the scheduler throws
   `IllegalStateException("Scheduled region should be acquirable")`. For a loaned region the tick must be skipped and
   moved to the next one. This is the only change in the scheduler core.

### Result

- A plugin task reads and modifies blocks and entities in any loaded chunks, as on Paper.
- Only the affected regions stop, and only for the duration of the task. The rest tick in parallel.
- An affected region skips ticks while the task holds it. For players in it this looks like a short lag —
  the same as a long task on the Paper main thread.

### Deadlocks

- Only the global thread takes regions (both here and in world unloading, also on the global thread), so two
  threads cannot wait for each other's regions.
- A region thread never waits for the global thread because of a loan: the scheduler just skips the tick.
- One case remains: a plugin task holds its own lock, and an event handler of the same plugin waits for it in the tick
  of the region the task wants to take. The task waits for the tick to end, the tick waits for the lock. Such a wait
  is cut off by the 500 ms limit: the task gets an exception, the region keeps running.

### Limitations

- A sync chunk load (T-103d) stops the global tick while the chunk loads, like the Paper main thread.
  If there is only one scheduler thread (as with `threads: -1` on a machine with up to 10 cores), all regions stop too.
- A sync load releases already taken regions. If the task held a reference to a block or entity in such a region
  and keeps accessing it without a thread check, the region may be ticking at that time.
- A single call that covers several regions at once (an AABB or radius check on a region border)
  still fails: the context is one region.
- Sync `Entity#teleport` (T-103c) is not instant: it returns `true` and runs via `teleportAsync` in the
  entity's next tick. `getLocation()` right after it returns the old position, and the plugin cannot see a
  `PlayerTeleportEvent` cancellation from the result.
- Plugin event handlers run on region threads. Loans from there are impossible: two regions could wait for each
  other. Another region is still inaccessible from an event handler.

## Report (T-104)

`/tessera compat` (permission `tessera.command.compat`, operators by default) shows what compat-mode plugins do that
Folia does not allow. A report row is plugin, kind, thread and the API method the plugin called, with the call count
and the stack of the first call:

- `failed` — the thread check did not pass, the call threw an exception (`TickThread.ensureTickThread`, `AsyncCatcher`).
  This is what does not work for the plugin;
- `teleport` — a sync teleport executed via `teleportAsync` in the next tick (T-103c);
- `region_entities` — a world entity list cut down to the caller's own region (T-109).

Thread: `global` — tasks and commands on the global thread, `region` — event handlers on a region thread, `other` —
async tasks and other threads. `/tessera compat <plugin>` shows the first stacks, `/tessera compat dump` writes
the whole report to `debug/tessera-compat-<time>.txt` (the row is copied from there into PLUGINS.md), `reset` clears it.

The report costs nothing where the call passes anyway: recording is added only in the branch that throws, and in
places where the stack is already walked. `UnsupportedOperationException` exceptions from API that Folia does not have
are not reported.

## Stages

T-103a done: a plugin task modified and read blocks and entities in two regions every tick for ~20 s, with bots in
both, no errors, region TPS 20.

T-103b done. A Bukkit command (`BukkitCommandNode`) of a compat-mode plugin runs in the loan scope.
The command owner is `PluginIdentifiableCommand#getPlugin()`, and for commands registered directly in `CommandMap`,
the plugin's class loader. Console and RCON already run commands on the global thread: the command runs immediately.
From a region thread (player, command block, `dispatchCommand` from a Folia plugin) the command goes to
`GlobalRegionScheduler` and runs in the next global tick; `dispatchCommand` returns `true` immediately. An error in
such a deferred command is logged, and the player gets a message. Check: `/cheal`, `/cblock` from RCON and from
players in two regions (a player heals a player in another region and places a block under them), no errors, TPS 20.

T-103c done. In Folia sync `teleport` always throws an exception. Now, if the call stack contains code of a compat-mode
plugin (the `StackWalker` check is done only on this path, which used to always fail), the teleport is put into the
entity scheduler and runs via `teleportAsync` in the entity's next tick; `teleport` returns `true` immediately.
Teleporting immediately is not possible: from `PlayerJoinEvent` it crashes the region (T-067). Works from tasks,
commands and event handlers. Folia plugins still get the exception. Check: teleport from an RCON command, from a
player command, from a task — between three regions; sync teleport in `PlayerJoinEvent`; a Folia plugin gets
`UnsupportedOperationException`. No errors.

T-103e done. Skript and plugins on the Paper Commands API register brigadier commands, bypassing `BukkitCommandNode`.
Now `Commands#performCommand` looks at the first command node: the owner is the plugin from `apiCommandMeta`, and if
there is none (Skript adds nodes directly to the dispatcher), the class loader of the command executor class. Such a
plugin's command runs the same way as in T-103b. Check: Skript script commands place a block under a player in another
region and teleport the player, from the console and from a player; no errors.

T-103d done. Many plugins (EssentialsX and everyone who embeds PaperLib) load chunks synchronously: PaperLib does not
parse version "26.x" and treats the server as old. Now, if a chunk has no region, `borrow` releases the taken
regions, puts a ticket on the chunk (`folia:delay`, holds the chunk for a few ticks of its region) and takes the new
region. After that the normal sync load proceeds the same way as on a Folia region thread: while waiting, it runs the
load tasks of the taken region itself. Waiting for an async load on the global thread is not possible: with a single
scheduler thread, the new chunk's region would never tick far enough to finish the load. One more change: a region
created next to a taken one waits to merge with it and cannot be taken. In that case the taken regions are released
and immediately taken again, and the scheduler does not grab them at that moment: the loan check is added to the
`tryMarkTicking` refusal condition under the regioniser lock. Check with one and with two scheduler threads: a plugin
task loads a new chunk next to a taken region and far from everything (up to 1 s on ungenerated terrain); EssentialsX
`/tppos` at 9000–112000 blocks, `/tp` of a player to coordinates from the console, `/home` — players end up in place.
No errors.

- **T-103a.** Skipping the tick of a loaned region in the scheduler. Loan, context and release. Entry in
  `ensureTickThread` for position, chunk and entity. Scope — sync `BukkitScheduler` tasks.
  Check: a plugin task modifies blocks in two distant regions, damages an entity, reads blocks. The server with
  bots in these regions keeps running, no errors in the log.
- **T-103b.** Compat-mode plugin commands (from the console and from players) run on the global thread in the
  same scope: `/tp`, `/heal`, `/give` for a player in another region. Done (except `/tp` — that is T-103c).
- **T-103c.** Sync `Entity#teleport` and `Player#teleport` for a compat-mode plugin. Done.
- **T-103d.** Sync chunk load from compat-mode plugin tasks and commands. Done.
- **T-103e.** Compat-mode plugin brigadier commands. Done.
