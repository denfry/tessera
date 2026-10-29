<div align="center">

<img src=".github/assets/tessera-logo.svg" alt="Логотип Tessera" width="112" height="112">

# Tessera

**Форк Folia с исправлениями и оптимизациями для больших выживательных серверов.**

[English](README.md) | Русский

[![Build](https://img.shields.io/github/actions/workflow/status/denfry/tessera/release.yml?branch=main&label=build)](https://github.com/denfry/tessera/actions/workflows/release.yml)
[![Release](https://img.shields.io/github/v/release/denfry/tessera?include_prereleases&sort=semver)](https://github.com/denfry/tessera/releases)
[![License](https://img.shields.io/badge/license-GPL--3.0-blue)](PATCHES-LICENSE)
[![Java 25](https://img.shields.io/badge/Java-25-orange)](https://adoptium.net/)
[![Minecraft 26.3](https://img.shields.io/badge/Minecraft-26.3-62b47a)](https://minecraft.net/)
[![Upstream: Folia](https://img.shields.io/badge/upstream-PaperMC%2FFolia-2f81f7)](https://github.com/PaperMC/Folia)

[Сайт](https://denfry.github.io/tessera/ru/) · [Скачать](https://github.com/denfry/tessera/releases) · [Патчи](PATCHES.md) · [Плагины](PLUGINS.md)

</div>

Tessera — форк [Folia](https://github.com/PaperMC/Folia) (региональная многопоточность поверх
[Paper](https://github.com/PaperMC/Paper)) с исправлениями багов, оптимизациями и небольшим набором
функций для больших выживательных серверов.

> [!NOTE]
> Ранняя стадия, идёт тестирование, для продакшена пока не готово. Планы — в [BACKLOG.md](BACKLOG.md).

## Главное

- **Скорборды** — скорборд потокобезопасен: личные доски, `Player#setScoreboard`, команды и цели
  работают из любого потока, как и `/team` и `/scoreboard`.
- **События телепорта** — `PlayerTeleportEvent`, `EntityTeleportEvent` и события порталов вызываются
  для асинхронных телепортов, порталов и эндер-жемчуга.
- **Миры на ходу** — `Bukkit.createWorld` и `unloadWorld` работают на запущенном сервере.
- **Исправления** — эндер-жемчуг и стазис-камеры, debug-подписки MiniHUD, дракон вдали от 0,0, жители
  в порталах, владение регионами в AI мобов, автосохранение карт и новых игроков, защита сети.

Полный список со ссылками на issues апстрима — в [PATCHES.md](PATCHES.md).

## Зачем Tessera

Folia делит мир на регионы, которые тикаются независимо, и благодаря этому один сервер использует
много ядер. Upstream развивается осторожно, и часть исправлений, важных для нагруженного выживания,
приходит не сразу. Tessera держит такие изменения отдельными небольшими патчами с описанием поверх
Folia: каждый можно проверить, убрать или отправить в upstream независимо от остальных.

## Цели

- Держаться близко к upstream Folia; каждое изменение Tessera — отдельный задокументированный патч.
- Исправления (дюпы, краши, нарушения владения регионами), которые upstream ещё не принял.
- Оптимизации, сохраняющие ванильное поведение, если опция конфига не говорит иначе.
- Ничего, что молча ломает плагины, написанные под Folia API.

## Плагины

Tessera запускает только плагины с `folia-supported: true`. В Paper API уже есть планировщики Folia
(`getRegionScheduler()`, `getGlobalRegionScheduler()`, `getAsyncScheduler()`, `Entity#getScheduler()`),
поэтому плагин, написанный под них, без изменений работает на Paper, Leaf и Tessera.

## Скачать

Сборки публикуются на странице [Releases](https://github.com/denfry/tessera/releases). Кроме того,
каждый push в `main` собирается [Release workflow](https://github.com/denfry/tessera/actions/workflows/release.yml),
и paperclip-jar прикрепляется к запуску как артефакт.

Запуск — как у любого jar Paper (нужна Java 25):

```bash
java -Xms4G -Xmx4G -jar server.jar --nogui   # server.jar — скачанный *-paperclip-*.jar
```

## Сборка

Нужны Git и JDK 25 (если JDK нет, Gradle скачает её сам).

```bash
./gradlew applyAllPatches
./gradlew createPaperclipJar   # отдельным запуском: задача появляется только после наложения патчей
```

Готовый jar: `folia-server/build/libs/*-paperclip-*.jar`.

## Работа с патчами

Структура унаследована от Folia, чтобы слияния с upstream оставались дешёвыми:

- `folia-server/minecraft-patches/` — патчи к исходникам Minecraft (`features/` — по одной фиче).
- `folia-server/paper-patches/` — патчи к исходникам сервера Paper.
- `folia-api/paper-patches/` — патчи к API.

Патчи Tessera идут после патчей upstream Folia в каждой папке; номера paperweight расставляет сам
при каждой пересборке. Порядок работы:
правите исходники в `folia-server/src/minecraft` или `paper-server`, коммитите там, затем
пересобираете файлы патчей через `./rb.sh` (`rb.bat` на Windows).

Полный порядок работы и соглашения о патчах — в [CONTRIBUTING.md](CONTRIBUTING.md) (на английском).

## Патчи Tessera

Все изменения Tessera поверх Folia перечислены в [PATCHES.md](PATCHES.md): затронутая область и
ссылка на соответствующий issue или PR в upstream, если он есть.

Сторонние плагины, проверенные на Tessera, и то, как они работают, перечислены в [PLUGINS.md](PLUGINS.md).

## Отношения с upstream

Tessera следует за [PaperMC/Folia](https://github.com/PaperMC/Folia) и регулярно вливает её ветки
версий. Почти вся работа в этом репозитории принадлежит командам Folia и Paper, и в первую очередь
[Spottedleaf](https://github.com/Spottedleaf), который спроектировал и написал региональную
многопоточность Folia. Если баг воспроизводится на обычной Folia, сообщите о нём
[в upstream](https://github.com/PaperMC/Folia/issues).

Обновление upstream:

```bash
git fetch upstream
git merge upstream/ver/<version>
./gradlew applyAllPatches   # разрешить конфликты, затем пересобрать патчи
```

## Сообщить о проблеме

- Баги, краши, проблемы производительности: [создайте issue](https://github.com/denfry/tessera/issues/new/choose)
  и приложите полный вывод `/version`.
- Баги, которые есть и на обычной Folia: сообщайте в [PaperMC/Folia](https://github.com/PaperMC/Folia/issues).
- Дюпы, краш-эксплойты и другие проблемы безопасности: только приватно, см. [SECURITY.md](SECURITY.md).

## Лицензия

Патчи распространяются на условиях [PATCHES-LICENSE](PATCHES-LICENSE), как и в Folia.
Исходники Minecraft не распространяются — они декомпилируются локально во время сборки.
