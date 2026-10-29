# Security policy

## Reporting a vulnerability

**Do not open public issues for exploits.** This includes item and block dupes, crash exploits,
ways to bypass region ownership checks, permission bypasses and anything else a player could abuse
on a live server.

Report them privately through GitHub Security Advisories:

**[Report a vulnerability](https://github.com/denfry/tessera/security/advisories/new)**

Please include:

- the Tessera version (full `/version` output);
- steps to reproduce, and whether it also reproduces on stock Folia;
- the impact (what a player can gain or break).

You will get a reply in the advisory thread. Please keep the details private until a fixed build
is released.

## Upstream issues

If the exploit also reproduces on stock [Folia](https://github.com/PaperMC/Folia) or
[Paper](https://github.com/PaperMC/Paper), it should be fixed upstream too. Follow the PaperMC
exploit reporting process for that part; you can still report it here so Tessera can carry a fix
in the meantime.

## Supported versions

Only the latest build for the current Minecraft version (26.3) receives fixes.
