# Configuring Tessera

Tessera reads the usual Paper files (`config/paper-global.yml`, `config/paper-world-defaults.yml`, `bukkit.yml`,
`spigot.yml`, `server.properties`) and one file of its own, `config/tessera.yml`.

## How `tessera.yml` behaves

- **It is created on the first start** with every option, its default and a comment.
- **New options appear by themselves.** When a newer build adds options, they are written into your file with their
  defaults and comments at startup. Your values stay; comments you wrote yourself do not, so the previous file is kept
  as `tessera.yml.old`. The console lists what was added.
- **Mistakes are reported, not ignored.** A wrong type (`light-entities: yes please`), a number out of range or an
  unknown key gets a warning in the console, with the closest known key for typos
  (`unknown option performance.ligth-entities (did you mean performance.light-entities?)`). The option keeps its
  default until it is fixed.
- **`/tessera reload`** reads the file again and applies what can change while the server runs. It lists every changed
  option; the ones marked *after a restart* are kept as they were until the next start. Permission
  `tessera.command.reload` (operators by default).

## Options

| Option | Default | Reload | What it does |
|---|---|---|---|
| `compat.plugins` | `[]` | restart | Plugins without `folia-supported: true` that are loaded anyway, by name, or `"*"`. See [COMPAT.md](COMPAT.md) |
| `performance.poi-searches-load-chunks` | `true` | yes | `false`: villagers look for job sites, beds and meeting points in loaded chunks only |
| `performance.light-entities` | `false` | yes | Marker and no-gravity armor stands run a full tick once a second; their viewers and those of display entities are updated every `light-entity-tracker-interval` ticks |
| `performance.light-entity-tracker-interval` | `5` | yes | 1..200 ticks |
| `performance.distant-mob-ai` | `false` | yes | Mobs far from players pick new goals and run sensors less often |
| `performance.distant-mob-ai-start-distance` | `12` | yes | Blocks from the nearest player where throttling starts |
| `performance.distant-mob-ai-max-interval` | `20` | yes | Longest interval, ticks |
| `performance.distant-mob-ai-exclude` | `[]` | restart | Entity types left alone, e.g. `[villager, minecraft:piglin]` |
| `performance.async-entity-tracker` | `false` | yes | Busy regions find entity viewer changes on a small thread pool |
| `performance.async-entity-tracker-threads` | `0` | restart | Pool size; `0` is a quarter of the CPU threads, at most 4 |
| `console.style` | `pretty` | restart | `pretty` or `classic` (Paper's format). `-Dtessera.log.style` and `TESSERA_LOG_STYLE` take precedence |
| `console.banner.enabled` | `true` | restart | Print the startup banner |
| `console.banner.logo` | Tessera logo | restart | Lines of the logo |
| `console.banner.lines` | build, Java, CPU, memory | restart | Lines under the logo |
| `branding.server-brand` | `''` | yes, for new joins | Name in the F3 screen and, with the version, in the server list for an incompatible client. `&` colors work, e.g. `'&6My&fServer'`. Empty keeps `Tessera`. A proxy may replace it |
| `monitoring.spike-threshold-ms` | `0` | yes | A region tick or task longer than this is sampled every 5 ms; the top frames and stacks go to `logs/spikes/` with the region's location. `0` is off, `200` is a good start |
| `monitoring.spike-max-reports` | `50` | yes | Reports kept in `logs/spikes/`; a region writes at most one every 10 s |

## Branding the console

`console.banner` is printed at startup, before anything else of the server. Put your own ASCII art into `logo`, one
line per entry, in single quotes (inside single quotes only `'` itself needs doubling, as `''`):

```yaml
console:
  banner:
    enabled: true
    logo:
      - '&6  __  __         ___                       '
      - '&6 |  \/  |_  _   / __| ___ _ ___ _____ _ _  '
      - '&e | |\/| | || |  \__ \/ -_) ''_\ V / -_) ''_| '
      - '&e |_|  |_|\_, |  |___/\___|_|  \_/\___|_|   '
      - '&e         |__/                              '
    lines:
      - '&f{brand} &7on {core} {version}, Minecraft {minecraft}'
      - '&7Java {java}, {cpus} CPU threads, {memory} heap'
```

- Colors: `&0`-`&9` and `&a`-`&f` as in Minecraft, `&l` bold, `&o` italic, `&n` underline, `&r` reset, `&#rrggbb` for
  terminals with true color. A color resets bold and the like, as in the game. Without color support (`NO_COLOR`,
  `-Dterminal.ansi=false`, a plain pipe) the codes are dropped.
- Placeholders: `{brand}` (`branding.server-brand` when set, otherwise `Tessera`), `{core}` (always the build's
  name), `{version}` `{minecraft}` `{java}` `{os}` `{cpus}` `{memory}`.
- In the console the banner has no time and level; `logs/latest.log` has it with them and without colors.
- Any FIGlet generator gives usable art; fonts like *Small* or *Standard* fit an 80-column panel.
