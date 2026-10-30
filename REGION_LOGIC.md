# Region Logic

This page has been moved to [the PaperMC documentation](https://docs.papermc.io/folia/reference/region-logic) site.

## Region size settings on Tessera

Both options are in `config/paper-global.yml` under `threaded-regions` and are read once at startup.

| Option | Default | Meaning |
|--------|---------|---------|
| `grid-exponent` | 4 | A region section is 2^`grid-exponent` chunks wide, so 16 chunks by default. Regions are built from sections. |
| `merge-radius` | 1 | Regions merge when their sections are within this many sections of each other. Clamped to 1..16. |

Raising `merge-radius` keeps nearby players and contraptions on one thread: there are fewer teleports between
regions, but one region does more work and regions tick less in parallel. A radius of 8 with the default grid merges
regions up to about 128 chunks apart. Lowering `grid-exponent` makes sections smaller, so regions split sooner, at the
cost of more sections to track. The regions stay at least 8 chunks apart with any value of either option.
