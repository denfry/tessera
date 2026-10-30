# Plugins on Tessera

Third-party plugins checked on a Tessera build. A row is added only after the plugin was actually run on Tessera,
not because its page says it supports Folia.

| Plugin | Version | Tessera build | `folia-supported` | Status | Notes |
|--------|---------|---------------|-------------------|--------|-------|
| [AuraSkills](https://modrinth.com/plugin/auraskills) | 2.4.0 | main@7b98588 | yes | partly | Loads, but `VersionUtils` cannot parse the local build version `26.3.local-SNAPSHOT`: `java.lang.NumberFormatException: For input string: "local"`. The ProtocolLib hook fails and the action bar task throws `NoClassDefFoundError: Could not initialize class ...AttributeCompat` every second while players are online. Re-check on a numbered build. |
| [AuthMeReloaded](https://modrinth.com/plugin/authmereloaded) | 6.0.1 (Folia build) | main@7b98588 | yes | works | `authme register`, `authme forcelogin` (player let in), `authme getip`; an unregistered player is kicked on login timeout as configured. No errors. |
| [BlueMap](https://modrinth.com/plugin/bluemap) | 5.29-paper | main@7b98588 | yes | works | After `accept-download: true`: 3 maps loaded, web server started, `bluemap`, `bluemap maps`, `bluemap update world`. No errors with 2 players online. |
| [Chunky](https://modrinth.com/plugin/chunky) | 1.5.3 | main@7b98588 | yes | works | `chunky radius 50` / `120` + `chunky start`: 81 and 289 chunks generated, `chunky progress`. No errors. |
| [CoreProtect](https://modrinth.com/plugin/coreprotect) | 24.1 | main@7b98588 | yes | broken | The plugin disables itself: "Minecraft 26.3 is not supported". Its own version check, not a Tessera error; 24.1 is the latest release. |
| [EssentialsX](https://modrinth.com/plugin/essentialsx) | 2.22.0 | main@7b98588 | no | needs Folia build | Refused: "not marked as supporting Folia". |
| [EssentialsX](https://modrinth.com/plugin/essentialsx) + EssentialsX Spawn | 2.22.0 | feat/plugin-compat@8954d5f | no | works in compatibility mode | Listed in `compat.plugins` of `config/tessera.yml` ([COMPAT.md](COMPAT.md)). With 2 players in different regions: `heal`, `feed`, `give`, `gamemode`, `whois` from the console; `heal <other>`, `sethome`/`home`, `tp <player>`, `tppos` and console `tp` to unloaded chunks 9000–112000 blocks away, `back`, `setspawn`/`spawn`, `tphere`, `tpa`/`tpaccept`, `top`, `near`, `god`, `fly`, `speed`, `kit`, `msg` from players. Prints "You are running an unsupported server version!". No other errors. |
| [FastAsyncWorldEdit](https://modrinth.com/plugin/fastasyncworldedit) | 2.16.1 (Paper) | main@7b98588 | no | needs Folia build | Refused: "not marked as supporting Folia". |
| [InvSee++](https://modrinth.com/plugin/invsee-plus-plus) | 0.31.22 | main@7b98588 | no | needs Folia build | Declares `folia-supported: false`; refused. |
| [LagFixer](https://modrinth.com/plugin/lagfixer) | 1.7.2-folia | main@7b98588 | yes | works | `lagfixer monitor`, `lagfixer ping` with 2 players online. Entity cleaning was not run. No errors. |
| [LevelledMobs](https://modrinth.com/plugin/levelledmobs) | 4.5.3.2 b159 | main@7b98588 | no | needs Folia build | Declares `folia-supported: false`; refused. |
| [LuckPerms](https://luckperms.net) | 5.5.88 (Bukkit) | main@7b98588 | yes | works | `lp info`, `lp creategroup`, group permission set, `lp user ... parent add`, `permission check`, `lp user ... info` for online players; serves Vault permissions and chat. No errors. |
| [Multiverse-Core](https://modrinth.com/plugin/multiverse-core) | 5.8.2 | main@7b98588 | no | needs Folia build | Refused: "not marked as supporting Folia". |
| [PlaceholderAPI](https://modrinth.com/plugin/placeholderapi) | 2.12.3 | main@7b98588 | yes | works | `papi list`, `papi ecloud download Player`, `papi reload`, `papi parse` for an online player. No errors. |
| [Plan](https://modrinth.com/plugin/plan) | 5.8 build 3638 | main@7b98588 | yes | works | Web server on 8804, SQLite, `plan info`, `plan player` for an online player. Geolocation is off until the GeoLite2 EULA is accepted in its config. No errors. |
| [ProtocolLib](https://github.com/dmulloy2/ProtocolLib) | 5.4.0 | main@7b98588 | yes | partly | Loads and players join, but packet serialization fails: `packetlog` throws `java.lang.IllegalStateException: can't access packet read/write method after 1.20.5`. Use the dev build. |
| [ProtocolLib](https://github.com/dmulloy2/ProtocolLib/releases/tag/dev-build) | 5.5.0-SNAPSHOT-501e187 (dev-build) | main@7b98588 | yes | works | `packetlog` decodes outgoing and incoming keep-alive packets for online players. Warns "MC 26.3.0 has not yet been tested". No errors. |
| [SkinsRestorer](https://modrinth.com/plugin/skinsrestorer) | 15.12.6 | main@7b98588 | yes | works | `sr status`, `sr applyskin`. On an offline-mode server it looks up each joining name on the Mojang API inside `AsyncPlayerPreLoginEvent`, which held logins for 10–56 s here (slow DNS); one test player timed out. |
| [Skript](https://modrinth.com/plugin/skript) | 2.17.1 | main@7b98588 | no | needs Folia build | Refused: "not marked as supporting Folia". |
| [spark](https://spark.lucko.me) | 1.10.194 (Bukkit, CI build 546) | main@73c05f6 | no | needs Folia build | Refused: "not marked as supporting Folia". With `folia-supported: true` forced into `plugin.yml` it fails in `onEnable`: `UnsupportedOperationException` in `BukkitSparkPlugin.executeAsync` (Bukkit scheduler). The spark bundled with Paper is switched off in Folia. For region numbers use `/tps` and the region report API / JMX. Not needed since paper 0013: the bundled spark works on Tessera. |
| [squaremap](https://modrinth.com/plugin/squaremap) | 1.4.3 (paper-mc26.3) | main@7b98588 | yes | works | Web server on 8080, `map fullrender minecraft:overworld` rendered 4096 chunks, `map progresslogging`. No errors. |
| [TAB](https://modrinth.com/plugin/tab-was-taken) | 6.2.1 | main@7b98588 | yes | works | `tab reload`, `tab cpu`, `tab dump` for an online player. No errors. |
| [TabTPS](https://modrinth.com/plugin/tabtps) | 1.4.2 | main@7b98588 | no | needs Folia build | Refused: "not marked as supporting Folia". |
| [Towny](https://modrinth.com/plugin/towny) | 0.103.2.0 | main@7b98588 | yes | works | `ta town new TestTown <online player>`, `town list`, `townyadmin`. Latest release is tagged up to MC 26.2 but runs on 26.3. No errors. |
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

Check it on a test server (see "Проверка" in [BACKLOG.md](BACKLOG.md)): start it, use its main commands and features,
join with players in different regions if the plugin touches players or the world, and read the log. Then add or update
its row. When a Tessera release fixes a problem, re-check the plugin and update the row.
