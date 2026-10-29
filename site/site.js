// Region grid: each letter is one region, "." is unloaded. Regions tick on
// their own schedule, the way Folia ticks them on separate threads.
const MAP = [
  "aa....bbb.",
  "aaa...bbb.",
  ".a..cc....",
  "....ccc..d",
  ".ee..c...d",
  ".ee.......",
];

const grid = document.querySelector(".grid");
if (grid) {
  const regions = {};
  for (const row of MAP) {
    for (const ch of row) {
      const tile = document.createElement("span");
      if (ch !== ".") {
        tile.className = "r";
        (regions[ch] ||= []).push(tile);
      }
      grid.appendChild(tile);
    }
  }

  // "c" is the crowded spawn region: it ticks slower than the rest.
  regions.c.forEach((t) => t.classList.add("slow"));

  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!still) {
    const period = { a: 900, b: 1100, c: 2300, d: 800, e: 1000 };
    for (const [id, tiles] of Object.entries(regions)) {
      const flash = () => {
        tiles.forEach((t) => t.classList.add("tick"));
        setTimeout(() => tiles.forEach((t) => t.classList.remove("tick")), 90);
      };
      setTimeout(() => {
        flash();
        setInterval(flash, period[id]);
      }, Math.random() * 600);
    }
  }
}

// Latest release tag (pre-releases included), if there is one.
const rel = document.querySelector("[data-release]");
if (rel) {
  fetch("https://api.github.com/repos/denfry/tessera/releases?per_page=1")
    .then((r) => (r.ok ? r.json() : null))
    .then((list) => {
      const data = list && list[0];
      if (data && data.tag_name) {
        rel.textContent = rel.dataset.release.replace("%s", data.tag_name);
      }
    })
    .catch(() => {});
}
