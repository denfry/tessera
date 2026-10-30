# Plugins on Tessera

Third-party plugins checked on a Tessera build. A row is added only after the plugin was actually run on Tessera,
not because its page says it supports Folia.

| Plugin | Version | Tessera build | `folia-supported` | Status | Notes |
|--------|---------|---------------|-------------------|--------|-------|
| [AuraSkills](https://modrinth.com/plugin/auraskills) | 2.4.0 | main@7b98588 | yes | partly | Loads, but `VersionUtils` cannot parse the local build version `26.3.local-SNAPSHOT`: `java.lang.NumberFormatException: For input string: "local"`. The ProtocolLib hook fails and the action bar task throws `NoClassDefFoundError: Could not initialize class ...AttributeCompat` every second while players are online. Re-check on a numbered build. |
| [AuthMeReloaded](https://modrinth.com/plugin/authmereloaded) | 6.0.1 (Folia build) | main@7b98588 | yes | works | `authme register`, `authme forcelogin` (player let in), `authme getip`; an unregistered player is kicked on login timeout as configured. No errors. |
| [BlueMap](https://modrinth.com/plugin/bluemap) | 5.29-paper | main@7b98588 | yes | works | After `accept-download: true`: 3 maps loaded, web server started, `bluemap`, `bluemap maps`, `bluemap update world`. No errors with 2 players online. |
| [Chunky](https://modrinth.com/plugin/chunky) | 1.5.3 | main@7b98588 | yes | works | `chunky radius 50` / `120` + `chunky start`: 81 and 289 chunks generated, `chunky progress`. No errors. |
| [ClickMobs](https://modrinth.com/plugin/clickmobs) | 1.3.1 | feat/plugin-compat@1bbe79b | no | loads in compatibility mode | Listed in `compat.plugins` ([COMPAT.md](COMPAT.md)); 2 players in different regions. Enables; picking up mobs needs a real client and was not tested. On Windows it failed to overwrite its own `lang/en_US.json` (file in use). |
| [CoreProtect](https://modrinth.com/plugin/coreprotect) | 24.1 | main@7b98588 | yes | broken | The plugin disables itself: "Minecraft 26.3 is not supported". Its own version check, not a Tessera error; 24.1 is the latest release. |
| [DeluxeMenus](https://modrinth.com/plugin/deluxemenus) | 1.14.1-Release | feat/plugin-compat@1bbe79b | no | works in compatibility mode | Listed in `compat.plugins` ([COMPAT.md](COMPAT.md)); 2 players in different regions. Requires PlaceholderAPI. `dm list`, `dm open basics_menu <player>` from the console and `dm open requirements_menu` from a player open the menus. No errors. |
| [EssentialsX](https://modrinth.com/plugin/essentialsx) | 2.22.0 | main@7b98588 | no | needs Folia build | Refused: "not marked as supporting Folia". |
| [EssentialsX](https://modrinth.com/plugin/essentialsx) + EssentialsX Spawn | 2.22.0 | feat/plugin-compat@8954d5f | no | works in compatibility mode | Listed in `compat.plugins` of `config/tessera.yml` ([COMPAT.md](COMPAT.md)). With 2 players in different regions: `heal`, `feed`, `give`, `gamemode`, `whois` from the console; `heal <other>`, `sethome`/`home`, `tp <player>`, `tppos` and console `tp` to unloaded chunks 9000–112000 blocks away, `back`, `setspawn`/`spawn`, `tphere`, `tpa`/`tpaccept`, `top`, `near`, `god`, `fly`, `speed`, `kit`, `msg` from players. Prints "You are running an unsupported server version!". No other errors. |
| [FastAsyncWorldEdit](https://modrinth.com/plugin/fastasyncworldedit) | 2.16.1 (Paper) | main@7b98588 | no | needs Folia build | Refused: "not marked as supporting Folia". |
| [FastAsyncWorldEdit](https://modrinth.com/plugin/fastasyncworldedit) | 2.16.1 (Paper) | feat/plugin-compat@1bbe79b | no | broken in compatibility mode | Listed in `compat.plugins` ([COMPAT.md](COMPAT.md)); 2 players in different regions. `//pos1`, `//pos2` work; `//set` fails: FAWE compares the current thread with the thread that enabled it ("Not main thread") and queues work on `MinecraftServer#execute`, which Folia does not have. Use WorldEdit, which supports Folia. |
| [GriefPrevention](https://modrinth.com/plugin/griefprevention) | 16.18.7 | feat/plugin-compat@1bbe79b | no | works in compatibility mode | Listed in `compat.plugins` ([COMPAT.md](COMPAT.md)); 2 players in different regions. `adjustbonusclaimblocks` from the console; `claim 10`, `trust`, `claimslist`, `abandonclaim` from a player. No errors. |
| [InvSee++](https://modrinth.com/plugin/invsee-plus-plus) | 0.31.22 | main@7b98588 | no | needs Folia build | Declares `folia-supported: false`; refused. |
| [InvSee++](https://modrinth.com/plugin/invsee-plus-plus) | 0.31.22 | feat/plugin-compat@1bbe79b | no | works in compatibility mode | Listed in `compat.plugins` ([COMPAT.md](COMPAT.md)); 2 players in different regions. Declares `folia-supported: false`. `invsee` and `endersee` open the inventory and ender chest of a player in another region. No errors. |
| [LagFixer](https://modrinth.com/plugin/lagfixer) | 1.7.2-folia | main@7b98588 | yes | works | `lagfixer monitor`, `lagfixer ping` with 2 players online. Entity cleaning was not run. No errors. |
| [LevelledMobs](https://modrinth.com/plugin/levelledmobs) | 4.5.3.2 b159 | main@7b98588 | no | needs Folia build | Declares `folia-supported: false`; refused. |
| [LevelledMobs](https://modrinth.com/plugin/levelledmobs) | 4.5.3.2 b159 | feat/plugin-compat@1bbe79b | no | partly | Listed in `compat.plugins` ([COMPAT.md](COMPAT.md)); 2 players in different regions. Enables, `lm info` works. Its `PlayerTeleportEvent` handler walks all entities of the world and fails on entities of other regions ("Accessing entity state off owning region's thread"). |
| [LevelledMobs](https://modrinth.com/plugin/levelledmobs) | 4.5.3.2 b159 | main@8696b6e | no | works | Listed in `compat.plugins` ([COMPAT.md](COMPAT.md)); 2 players in different regions, levelled mobs in both. Its `PlayerTeleportEvent` handler now sees only the entities of the player's region, no thread check failures. |
| [LuckPerms](https://luckperms.net) | 5.5.88 (Bukkit) | main@7b98588 | yes | works | `lp info`, `lp creategroup`, group permission set, `lp user ... parent add`, `permission check`, `lp user ... info` for online players; serves Vault permissions and chat. No errors. |
| [Multiverse-Core](https://modrinth.com/plugin/multiverse-core) | 5.8.2 | main@7b98588 | no | needs Folia build | Refused: "not marked as supporting Folia". |
| [Multiverse-Core](https://modrinth.com/plugin/multiverse-core) | 5.8.2 | main (T-108) | no | works in compatibility mode | Listed in `compat.plugins` ([COMPAT.md](COMPAT.md)); 2 players in different regions. `mv create`, `mv tp <player> <world>`, `mv info`, `mv list` work, and config and worlds load on startup, including a second world after a restart. Portals and inventories are separate plugins, see below. |
| [Multiverse-Inventories](https://modrinth.com/plugin/multiverse-inventories) | 5.3.6 | feat/plugin-compat@1bbe79b | no | loads in compatibility mode | Listed in `compat.plugins` ([COMPAT.md](COMPAT.md)); 2 players in different regions. `mvinv list`, `mvinv info world` work. Depends on Multiverse-Core. |
| [Multiverse-Portals](https://modrinth.com/plugin/multiverse-portals) | 5.3.0 | feat/plugin-compat@1bbe79b | no | loads in compatibility mode | Listed in `compat.plugins` ([COMPAT.md](COMPAT.md)); 2 players in different regions. `mvp list` works; portals were not built. |
| [PlaceholderAPI](https://modrinth.com/plugin/placeholderapi) | 2.12.3 | main@7b98588 | yes | works | `papi list`, `papi ecloud download Player`, `papi reload`, `papi parse` for an online player. No errors. |
| [Plan](https://modrinth.com/plugin/plan) | 5.8 build 3638 | main@7b98588 | yes | works | Web server on 8804, SQLite, `plan info`, `plan player` for an online player. Geolocation is off until the GeoLite2 EULA is accepted in its config. No errors. |
| [PlayerKits2](https://modrinth.com/plugin/playerkits-2) | 1.24.2 | feat/plugin-compat@1bbe79b | no | works in compatibility mode | Listed in `compat.plugins` ([COMPAT.md](COMPAT.md)); 2 players in different regions. `kit` opens the kits menu for a player, `kit reload`. No errors. |
| [ProtocolLib](https://github.com/dmulloy2/ProtocolLib) | 5.4.0 | main@7b98588 | yes | partly | Loads and players join, but packet serialization fails: `packetlog` throws `java.lang.IllegalStateException: can't access packet read/write method after 1.20.5`. Use the dev build. |
| [ProtocolLib](https://github.com/dmulloy2/ProtocolLib/releases/tag/dev-build) | 5.5.0-SNAPSHOT-501e187 (dev-build) | main@7b98588 | yes | works | `packetlog` decodes outgoing and incoming keep-alive packets for online players. Warns "MC 26.3.0 has not yet been tested". No errors. |
| [SetHome](https://modrinth.com/plugin/sethome) | 6.3 | feat/plugin-compat@1bbe79b | no | works in compatibility mode | Listed in `compat.plugins` ([COMPAT.md](COMPAT.md)); 2 players in different regions. `sethome`, then `home` from 300 blocks away brings the player back. No errors. |
| [SkinsRestorer](https://modrinth.com/plugin/skinsrestorer) | 15.12.6 | main@7b98588 | yes | works | `sr status`, `sr applyskin`. On an offline-mode server it looks up each joining name on the Mojang API inside `AsyncPlayerPreLoginEvent`, which held logins for 10–56 s here (slow DNS); one test player timed out. |
| [Skript](https://modrinth.com/plugin/skript) | 2.17.1 | main@7b98588 | no | needs Folia build | Refused: "not marked as supporting Folia". |
| [spark](https://spark.lucko.me) | 1.10.194 (Bukkit, CI build 546) | main@73c05f6 | no | needs Folia build | Refused: "not marked as supporting Folia". With `folia-supported: true` forced into `plugin.yml` it fails in `onEnable`: `UnsupportedOperationException` in `BukkitSparkPlugin.executeAsync` (Bukkit scheduler). The spark bundled with Paper is switched off in Folia. For region numbers use `/tps` and the region report API / JMX. Not needed since paper 0013: the bundled spark works on Tessera. |
| [Skript](https://modrinth.com/plugin/skript) | 2.17.1 | feat/plugin-compat@1bbe79b | no | works in compatibility mode | Listed in `compat.plugins` ([COMPAT.md](COMPAT.md)); 2 players in different regions. Script commands from the console and from a player set a block under a player in another region and teleport players; `every 5 seconds` loops over players, `on join`. No errors. |
| [squaremap](https://modrinth.com/plugin/squaremap) | 1.4.3 (paper-mc26.3) | main@7b98588 | yes | works | Web server on 8080, `map fullrender minecraft:overworld` rendered 4096 chunks, `map progresslogging`. No errors. |
| [TAB](https://modrinth.com/plugin/tab-was-taken) | 6.2.1 | main@7b98588 | yes | works | `tab reload`, `tab cpu`, `tab dump` for an online player. No errors. |
| [TabTPS](https://modrinth.com/plugin/tabtps) | 1.4.2 | main@7b98588 | no | needs Folia build | Refused: "not marked as supporting Folia". |
| [TabTPS](https://modrinth.com/plugin/tabtps) | 1.4.2 | feat/plugin-compat@1bbe79b | no | partly | Listed in `compat.plugins` ([COMPAT.md](COMPAT.md)); 2 players in different regions. `tickinfo`, `mspt`, `tabtps toggle tab` run without errors, but MSPT shows 0 and `Long.MAX_VALUE`: Folia does not fill the server tick times it reads. |
| [Towny](https://modrinth.com/plugin/towny) | 0.103.2.0 | main@7b98588 | yes | works | `ta town new TestTown <online player>`, `town list`, `townyadmin`. Latest release is tagged up to MC 26.2 but runs on 26.3. No errors. |
| [tps-hud](https://modrinth.com/plugin/tps-hud) | 2.0.0+26.2 | feat/plugin-compat@1bbe79b | no | needs client mod | Listed in `compat.plugins` ([COMPAT.md](COMPAT.md)); 2 players in different regions. Its task throws `ArrayIndexOutOfBoundsException` and its handshake fails without the client mod. |
| [VaultUnlocked](https://modrinth.com/plugin/vaultunlocked) | 2.20.3 | main@7b98588 | yes | works | `vault-info` shows the LuckPerms permission and chat providers; PlaceholderAPI expansion registered. No economy provider was installed. No errors. |
| [WorldEdit](https://modrinth.com/plugin/worldedit) | 7.4.6 | main@7b98588 | yes | partly | `we version`, `//world`, `//pos1`, `//pos2` work from the console, but console edits do not: `//set` changes 0 blocks or fails, and `//count` throws `IllegalStateException: Thread failed main thread check: Cannot asynchronously load chunks` (the console runs on the global region thread). Edits by a player were not tested. |
| [WorldGuard](https://modrinth.com/plugin/worldguard) | 7.0.20 | main@7b98588 | yes | works | `rg define`, `rg flag ... pvp deny`, `rg info`, `rg list` from the console; the region survives a restart. Protection against player actions was not tested. No errors. |

## Status

- **works** — loads, its main features were used on a test server, no new `ERROR` / exceptions in the log.
- **partly** — loads, but some features fail; the Notes column says which and links the issue.
- **broken** — does not load or breaks the server; link the issue or the reason.
- **needs Folia build** — the plugin has no `folia-supported: true` build, so Tessera refuses to load it.

## Columns

- **Plugin** — name, linked to its Modrinth / Hangar / SpigotMC / GitHub page.
- **Version** — the exact plugin version that was checked.
- **Tessera build** — the release tag or commit the check ran on.
- **`folia-supported`** — whether the jar declares Folia support (`yes` / `no`).
- **Notes** — what was checked, what fails, links to Tessera or upstream issues.

## Adding a plugin

Check it on a test server (see "Testing" in [BACKLOG.md](BACKLOG.md)): start it, use its main commands and features,
join with players in different regions if the plugin touches players or the world, and read the log. Then add or update
its row. When a Tessera release fixes a problem, re-check the plugin and update the row.

For a plugin in compatibility mode, run `/tessera compat` after the check ([COMPAT.md](COMPAT.md)): every `failed`
line is an API method that does not work for the plugin on that thread, and the Notes should name it.
