# Tessera patches

Changes Tessera carries on top of [Folia](https://github.com/PaperMC/Folia). Upstream Folia and Paper
patches are not listed here.

| Patch | Area | Description | Upstream ref |
|-------|------|-------------|--------------|
| _none yet_ | | | |

_Patches are added here as they land._

## Numbering

Tessera patches are numbered from `1000-` (for example `1000-Fix-something.patch`). Upstream Folia
uses low numbers (`0001-` and up), so the two sets never collide and upstream merges do not force
renumbering.

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
