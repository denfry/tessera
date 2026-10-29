# Tessera backlog

Список багов и фич для Tessera. Каждый пункт можно целиком отдать исполнителю: там есть контекст, где искать, что
считать готовым и как проверить. Сделанное переносится в раздел «Готово» и в [PATCHES.md](PATCHES.md).

Приоритеты: **P0** нужно в первую очередь (без этого не обойтись большому серверу), **P1** заметно игрокам или роняет сервер, **P2** производительность
и удобство, **P3** когда-нибудь.

---

## Как брать задачу (прочитать исполнителю целиком)

1. **Где код.** Сначала `./gradlew applyAllPatches`. Исходники Minecraft с патчами Folia лежат в
   `folia-server/src/minecraft/java` (отдельный git-репозиторий), исходники Paper-сервера — в `paper-server`, API — в
   `paper-api`. Правки коммитятся **внутри этих репозиториев**, по одному коммиту на изменение. Затем `./rb.sh`
   пересобирает `.patch` файлы в `folia-server/minecraft-patches/features`, `folia-server/paper-patches/features` и
   `folia-api/paper-patches`. Номера патчей paperweight проставляет сам.
2. **Поиск по коду.** Сначала `codebase-index search "<запрос>" --compact` / `refs` / `impact` из корня репозитория, Grep — запасной вариант.
3. **Стиль.**
   - Изменённые строки помечаются `// Tessera - <зачем>`, блоки — `// Tessera start - ...` / `// Tessera end - ...`.
   - Править как можно меньше строк upstream.
   - Поведение, меняющее геймплей, прячется за опцию конфига, по умолчанию — ванильное.
   - В рабочем дереве CRLF: если `git apply` не накладывается, правь скриптом с учётом `\r\n`.
4. **Коммиты.**
   - Автор строго `git -c user.name=denfry -c user.email=dabinayo@pm.me commit`.
   - Сообщение во вложенных репозиториях — по-английски, в стиле Paper: заголовок, абзац «почему», затем `Fixes PaperMC/Folia#N` и,
     если код взят из чужого PR, `Based on PaperMC/Folia#N (автор)`.
   - В репозитории tessera — по-русски: `fix: ...`, `feat: ...`.
   - Никакой AI-атрибуции (Co-Authored-By, «Generated with», упоминаний Claude/AI) — нигде.
   - Не пушить без явного разрешения.
5. **Проверка.**
   - Собрать: `./gradlew :folia-server:compileJava`, затем `./gradlew createPaperclipJar`; jar — `folia-server/build/libs/folia-paperclip-*.jar`.
   - Запустить тестовый сервер на **JDK 25** (`~/.jdks/azul-25/bin/java`) в отдельной папке. В `server.properties`: `online-mode=false`,
     `white-list=false`, свой порт.
   - Для входа игроков есть `tools/joinbot.py <порт> <ник> <секунд онлайн> [лишних finish_configuration]` — минимальный клиент
     26.3 (протокол 777): логин, конфигурация, вход в игру, ответы на keep-alive.
   - Если поведение проверяется плагином, написать маленький тестовый плагин (`folia-supported: true`) и собрать его
     `javac` против jar из `<сервер>/libraries`.
   - В логе не должно быть новых `ERROR` / `Exception`.
6. **После.** Строка в PATCHES.md, пункт здесь перенести в «Готово».
7. **Плагины.** Каждый сторонний плагин, запущенный на Tessera, записывается в [PLUGINS.md](PLUGINS.md) (статус, версия,
   сборка Tessera, что сломано). Только публичные плагины.

---

## P0 — в первую очередь

### T-003 Метрики и профилирование регионов (spark) — [#299](https://github.com/PaperMC/Folia/issues/299), [#398](https://github.com/PaperMC/Folia/issues/398), [#31](https://github.com/PaperMC/Folia/issues/31)
- **Зачем.** Без профайлера на проде не понять, какой регион тормозит. У Folia есть свой `/profiler` (патч Region-profiler), но
  нет API и экспорта.
- **Где.** `TickRegionScheduler`, `TickRegions.TickRegionData` (там уже есть статистика тиков), `RegionizedServer`, патч
  «Add TPS From Region».
- **Готово, когда.**
  - В API (`folia-api`) есть `Bukkit.getRegionTickReport(World, chunkX, chunkZ)` или аналог: MSPT/TPS региона, число
    чанков, сущностей и игроков в регионе.
  - Есть список всех регионов мира со сводкой.
  - Есть JMX MBean `dev.tessera:type=Region` с теми же числами (для Prometheus через jmx_exporter).
  - Проверено, что spark (последняя версия с поддержкой Folia) запускается и снимает профиль. Если не запускается —
    записать почему и что нужно.
- **Проверка.** Тестовый плагин печатает отчёт. `jconsole` / `jcmd` показывает MBean.

---

## P1 — заметно игрокам

### T-010 Воронки часто не подбирают предметы — [#209](https://github.com/PaperMC/Folia/issues/209)
- **Где.** `HopperBlockEntity` (`suckInItems`, поиск `ItemEntity` в AABB над воронкой), проверки владения регионом на краю
  региона, оптимизации воронок Paper.
- **Готово, когда.** Воронка под падающими предметами (в том числе на границе чанков и регионов) подбирает их так же, как
  на Paper. Нет «пропусков» при нескольких регионах.
- **Проверка.** Плагин спавнит 1000 предметов над рядом воронок с сундуками, в том числе на стыке чанков, и считает
  предметы в сундуках через N тиков. Сравнить с Paper той же версии.

### T-011 `setRespawnLocation` стирает точку возрождения — [#337](https://github.com/PaperMC/Folia/issues/337)
- **Где.** `CraftPlayer#setRespawnLocation`, `ServerPlayer#setRespawnPosition`, обработка возрождения в Folia
  (`respawn` в PlayerList / Region-Threading-Base).
- **Готово, когда.** Точка, выставленная плагином, переживает смерть и перезаход, `getRespawnLocation()` её возвращает.

### T-012 Энд-портал на транспорте ведёт на спавн мира, а не к точке возрождения — [#453](https://github.com/PaperMC/Folia/issues/453)
- **Где.** Асинхронный путь порталов в `Entity` (Region-Threading-Base): для пассажиров и транспорта он обходит Bukkit
  portal events и `findRespawnPositionAndUseSpawnBlock`.
- **Готово, когда.** Игрок верхом выходит из энда к своей кровати или якорю, вызывается `PlayerPortalEvent` / `PlayerRespawnEvent`
  (связано с T-002).

### T-013 Нотные блоки не реагируют на редстоун, высота не меняется — [#470](https://github.com/PaperMC/Folia/issues/470)
- **Где.** `NoteBlock#neighborChanged` / `useWithoutItem` / `triggerEvent`, блок-события (`blockEvent`) в
  `ServerLevel` — в Folia они регионизированы (`RegionizedWorldData`).
- **Готово, когда.** Нотный блок звучит от редстоуна и меняет высоту при клике, как на Paper.

### T-014 Поплавок удочки пропадает при смене измерения — [#435](https://github.com/PaperMC/Folia/issues/435)
- **Где.** `FishingHook#tick` / `shouldStopFishing`, смена владельца при переходе игрока между мирами.
- **Готово, когда.** Поведение как в ванили: поплавок пропадает без ошибок и без утечки ссылки `player.fishing`. После
  перехода можно сразу закинуть удочку снова.

### T-015 Телепорт сбрасывает скорость сущности — [#441](https://github.com/PaperMC/Folia/issues/441)
- **Где.** `Entity#teleportAsync` → `transform(pos, yaw, pitch, velocity)`, `TeleportFlag`.
- **Готово, когда.** Скорость сохраняется так же, как на Paper (`teleport` с флагами относительности). Есть опция API
  или флаг, чтобы её сбросить.

### T-016 Энд-гейтвей (портал к внешним островам) не работает — [#51](https://github.com/PaperMC/Folia/issues/51)
- **Где.** `TheEndGatewayBlockEntity` (`teleportTick`, поиск выхода `findOrCreateValidTeleportPos` — грузит чанки, на Folia
  нельзя синхронно), `EndGatewayBlock#getPortalDestination`.
- **Готово, когда.** Жемчуг или игрок в гейтвее попадает на внешние острова, выход ищется асинхронно, без синхронной
  загрузки чанков.

### T-017 Лишние незер-порталы до телепорта игрока — [#69](https://github.com/PaperMC/Folia/issues/69)
- **Где.** Асинхронный поиск или создание портала (`PortalForcer`, Region-Threading-Base): несколько попыток телепорта
  подряд создают несколько порталов.
- **Готово, когда.** Пока телепорт сущности через портал в процессе, повторный не запускается. Создаётся ровно один портал.

### T-018 Розы иссушения не выпадают, если голова визера прошла через портал — [#388](https://github.com/PaperMC/Folia/issues/388)
- **Где.** `LivingEntity#createWitherRose`, `WitherSkull`, владелец снаряда (`getOwner` через `ownerUUID` в другом
  мире или регионе).

### T-019 Повреждение нарисованных карт — [#177](https://github.com/PaperMC/Folia/issues/177)
- **Зачем.** Задевает ImageFrame на main.
- **Где.** `MapItemSavedData` (общие данные карт с сервера после #505), `HoldingPlayer`, `MapItem#update`. Карту
  обновляют несколько регионов одновременно, `colors[]` и `dirty` не синхронизированы.
- **Готово, когда.** Карта, висящая в рамках в разных регионах и в руках игроков, не портится. Доступ к `MapItemSavedData`
  потокобезопасен или выполняется на одном владельце.

### T-020 `/gamerule locatorBar true` не работает — [#370](https://github.com/PaperMC/Folia/issues/370)
- **Где.** `ServerWaypointManager` (глобальное состояние на мир, обновление трекинга точек между регионами).

### T-021 Не работают команда `/dialog` — [#434](https://github.com/PaperMC/Folia/issues/434) — и Conversation API — [#216](https://github.com/PaperMC/Folia/issues/216)
- **Где.** `DialogCommand`, `CraftConversation` / `ConversationTracker` (использует Bukkit scheduler и главный поток).
- **Готово, когда.** `/dialog show` работает. `Player#beginConversation` работает: ввод из чата перехватывается на потоке игрока.

### T-022 Аллай после отказанного взаимодействия рассинхронизирует инвентарь клиента — [#502](https://github.com/PaperMC/Folia/issues/502)
- **Где.** `Allay#mobInteract`, отмена `PlayerInteractEntityEvent`. После отмены клиенту не отправляется ресинхронизация
  слота и экипировки.

### T-023 BlockState из ItemMeta получает координаты 0,0,0 — [#328](https://github.com/PaperMC/Folia/issues/328)
- **Где.** `CraftMetaBlockState`, `CraftBlockStates#getBlockState(world, pos, ...)` с фиктивным миром.

### T-024 Пакет recipe discovery невалиден — [#303](https://github.com/PaperMC/Folia/issues/303)
- **Где.** `ServerRecipeBook`, `ClientboundRecipeBookAddPacket`. Проверить на 26.3, может быть уже неактуально.

### T-025 Жители неправильно определяют рабочее место — [#127](https://github.com/PaperMC/Folia/issues/127)
- **Где.** `AssignProfessionFromJobSite`, `AcquirePoi`, `PoiManager` (смежно с уже сделанными патчами по AI и POI).

### T-026 Ошибка генерации блоков — [#61](https://github.com/PaperMC/Folia/issues/61)
- Сначала воспроизвести на 26.3. Если не воспроизводится — закрыть.

---

## P1 — краши и зависания

### T-030 Чужой регион трогают сущности и AI
- Issues: [#386](https://github.com/PaperMC/Folia/issues/386) (Zombie), [#381](https://github.com/PaperMC/Folia/issues/381)
  (getEntities async), [#334](https://github.com/PaperMC/Folia/issues/334) (свиная башня), [#203](https://github.com/PaperMC/Folia/issues/203)
  (AI читает блок вне региона), [#199](https://github.com/PaperMC/Folia/issues/199) (сущность движется за пределы региона),
  [#152](https://github.com/PaperMC/Folia/issues/152) (owner state async), [#327](https://github.com/PaperMC/Folia/issues/327)
  (удаление игрока).
- **Как делать.** По стектрейсу в issue найти поведение, сенсор или метод. Добавить проверку
  `TickThread.isTickThreadFor(...)` и пропустить или отложить действие — по образцу уже сделанного патча
  «Validate region ownership in AI behaviours». Каждый случай — отдельный коммит.
- **Готово, когда.** Для каждого стектрейса есть патч или запись «не воспроизводится на 26.3».

### T-031 Жители принудительно грузят чанки ради POI — [#292](https://github.com/PaperMC/Folia/issues/292)
- **Где.** `PoiManager#ensureLoadedAndValid`, `AcquirePoi`, `YieldJobSite`, `SetClosestHomeAsWalkTarget`. Поиск POI грузит
  чанки синхронно.
- **Готово, когда.** Поиск POI не грузит чанки вне региона и не держит регион. В профиле нет `ensureLoadedAndValid` в
  горячих местах.

### T-032 Конкуренция за блокировки — [#291](https://github.com/PaperMC/Folia/issues/291)
- Снять профиль конкуренции (JFR `jdk.JavaMonitorEnter`, `jdk.ThreadPark`) при 50+ ботах в разных регионах, найти
  горячие мониторы (как было с POI в #530) и убрать общие блокировки.

### T-033 Ошибка RPC management server — [#416](https://github.com/PaperMC/Folia/issues/416)
- **Где.** `net.minecraft.server.jsonrpc` (`minecraft:server/status` читает состояние сервера с IO-потока). Перевести
  чтение на глобальный тик или на потокобезопасные снимки.

### T-034 Зависания и самопроизвольная остановка — [#447](https://github.com/PaperMC/Folia/issues/447), [#437](https://github.com/PaperMC/Folia/issues/437), [#196](https://github.com/PaperMC/Folia/issues/196)
- Логов в issue мало. Нужны watchdog-дампы с живых серверов на Tessera.
- Улучшить watchdog: при зависании региона печатать стек потока региона, центр региона, мир, число сущностей и чанков.

---

## P2 — производительность

### T-040 Лёгкий тик для `text_display`, `item_display`, `block_display`, неподвижных `armor_stand`
- **Зачем.** На спавне main 391 такая сущность (голограммы, NPC), их тикают и отслеживают как обычных.
- **Что.**
  - Display-сущности без интерполяции и пассажиров не тикают физику.
  - `ArmorStand` с `setMarker(true)` или без гравитации не проверяет коллизии.
  - Трекер реже пересчитывает их видимость.
  - Всё за опцией конфига.
- **Проверка.** 2000 голограмм у бота, сравнить MSPT региона до и после.

### T-041 Асинхронный трекер сущностей
- **Что.** Расчёт, кто кого видит (`ChunkMap.TrackedEntity#updatePlayer`), вынести в пул потоков с последующим
  применением на потоке региона. Это ответ на кейс «все игроки в одном регионе» (сложность O(P·E)).
- **Готово, когда.** При 100 ботах и 3000 сущностях в одном регионе MSPT трекера падает заметно, без рассинхрона клиентов.

### T-042 Асинхронный поиск пути
- `PathNavigation` / `PathFinder` считать вне потока региона по снимку блоков, результат применять в тике.

### T-043 DAB: реже тикать AI далёких мобов
- Частота `Mob#serverAiStep` и `Brain#tick` зависит от расстояния до ближайшего игрока. Опция конфига, по умолчанию выключено.

### T-044 Настройки размера региона
- В конфиг Folia/Tessera вынести `grid-exponent` и радиус слияния регионов, задокументировать влияние.

### T-045 Порталы, связанные между незером и обычным миром, на одном потоке — [#469](https://github.com/PaperMC/Folia/issues/469)
- Опция: регионы обычного мира и незера, связанные порталом, тикаются одним потоком (фермы и механизмы у порталов). Дизайн
  сначала обсудить.

### T-046 Сохранение игроков и чанков порциями без пиков
- В профиле Leaf были пики раз в минуту. Проверить, что автосохранение на Tessera размазано по тикам: `max-per-tick` для игроков,
  чанков и карт.

---

## P3 — потом

- **T-060** Автоматический мёрж upstream Folia ([#468](https://github.com/PaperMC/Folia/issues/468)): workflow раз в неделю
  делает ветку `upstream-sync`, мёржит PaperMC/Folia, прогоняет `applyAllPatches` и сборку и открывает PR.
- **T-061** Сообщения чанкового API ([#96](https://github.com/PaperMC/Folia/issues/96)): понятные ошибки при вызове
  синхронного API не с того потока (какой поток, какой регион, что использовать вместо).
- **T-062** Проверка версий для Tessera: `/version` сейчас пишет «Unknown version». Сделать проверку по GitHub Releases
  `denfry/tessera`.
- **T-063** CI: прогон `tools/joinbot.py` на собранном jar в Actions (сервер, два бота, вход и выход, остановка без ERROR).
- **T-065** Ранний `stop` из консоли: команда, введённая сразу после `Done`, падает с NPE `CommandSourceStack.getLevel()` is null
  (`getGameRules()`), сервер не останавливается. Видно при `echo stop | java -jar ...`.
- **T-066** Края событий телепорта (после T-002): для портала `PlayerTeleportEvent` получает примерный выход (портал ещё не найден);
  при `canCreatePortal=false` и отсутствии портала сущность ставится в точку поиска, а не остаётся на месте, как в Paper; откат
  после отменённого `PlayerMoveEvent` идёт через `teleportAsync` и сам вызывает `PlayerTeleportEvent`, его можно отменить.
- **T-067** `teleportAsync` из `PlayerJoinEvent` роняет регион: в событии `IllegalStateException: Player is already removed from player chunk loader` (`transformForAsyncTeleport` → `removePlayerImmediately`), затем регион падает с NPE в `ChunkMap.newTrackerTick` (`getChunkStatus()` null). Нужно отложить телепорт до полного входа или отказать с понятной ошибкой. Воспроизводится тестовым плагином T-004.
- **T-064** Края выгрузки миров (после T-001): сущность или игрок, чей асинхронный телепорт в мир начался до `unloadWorld`, и вход игрока, сохранённого в этом мире, в момент выгрузки. Сейчас `unloadWorld` проверяет только игроков в мире и запрещает новые `teleportAsync` туда. Пока мир сохраняется, глобальный поток ждёт (на тестах 0,1–1,4 с).

---

## Готово

| Что | Issue / PR | Патч |
|---|---|---|
| Эндер-жемчуг: смена измерения, стазис-камеры, damager | #421, #438 | 0012 |
| Debug-подписки (MiniHUD) роняли сервер | #472, #432 | 0013 |
| `spawnRadius 0` | #401 | 0014 |
| Автосохранение карт | #505 | 0015 |
| Проверки региона в AI | #523, #525, #526, #527, #495 | 0016 |
| POI деревень без общей блокировки | #530 | 0017 |
| Чат во время остановки | #461 | 0018 |
| `playersByName` потокобезопасен | #497 | 0019 |
| Автосохранение несохранённых игроков | #459 | 0020 |
| Части эндер-дракона | #427, #504 | 0021 |
| Жители в порталах («World mismatch») | #431 | 0022 |
| Смена протокола не блокирует потоки, спам finish_configuration | #454, #520 | 0023 |
| Уборка в мире из `onDisable` | #353 | 0024 / paper 0009 |
| Потокобезопасные hide/showPlayer | #406 | paper 0007 |
| Кэш типов целей мобов | #522 | paper 0008 |
| Брендинг Tessera, GitHub Release на каждую сборку | — | build.gradle.kts.patch, release.yml |
| Загрузка и выгрузка миров (`createWorld` / `unloadWorld`), T-001 | #134 | 0025 / paper 0010 |
| `PlayerTeleportEvent` / `EntityTeleportEvent` и события порталов для асинхронных телепортов, T-002 | #490, #330 | 0026 / api 0005 |
| Потокобезопасный скорборд: личные доски, команды, `/team`, `/scoreboard`, T-004 | #25 | 0027 / paper 0011 |
