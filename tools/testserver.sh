#!/usr/bin/env bash
# Local test server for checking a change on a running Tessera build.
#
#   tools/testserver.sh start <dir> [jar]   create or reuse <dir>, copy the jar (default: the latest paperclip jar
#                                           in folia-server/build/libs), start it and wait for "Done"
#   tools/testserver.sh rcon <dir> <cmd>... run console commands through RCON
#   tools/testserver.sh bot <dir> <name> <seconds>   join with tools/joinbot.py (runs in the background, log in <dir>/bot-<name>.log)
#   tools/testserver.sh errors <dir>        print ERROR lines and exceptions from the log; exit 1 if there are any
#   tools/testserver.sh stop <dir>          stop through RCON, kill the process if it does not exit
#
# Environment: TESSERA_JAVA (java 25 binary, default: java on PATH), TESSERA_JAVA_OPTS (extra JVM flags),
# TESSERA_TEST_PORT (game port of a new server, default 25600; RCON uses the next port).
# Plugins for the test go into <dir>/plugins.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JAVA="${TESSERA_JAVA:-java}"
PYTHON="$(command -v python3 || command -v python)"
RCON_PASSWORD=test

property() { grep -E "^$2=" "$1/server.properties" | cut -d= -f2; }
rcon() { "$PYTHON" "$ROOT/tools/rcon.py" "$(property "$1" rcon.port)" "$RCON_PASSWORD" "${@:2}"; }

init() {
    local dir="$1" port="${TESSERA_TEST_PORT:-25600}"
    mkdir -p "$dir/plugins/bStats"
    echo "eula=true" > "$dir/eula.txt"
    # test servers stay out of the public bStats numbers
    [ -f "$dir/plugins/bStats/config.yml" ] || echo "enabled: false" > "$dir/plugins/bStats/config.yml"
    [ -f "$dir/server.properties" ] || cat > "$dir/server.properties" <<EOF
server-port=$port
online-mode=false
white-list=false
enable-rcon=true
rcon.port=$((port + 1))
rcon.password=$RCON_PASSWORD
broadcast-rcon-to-ops=false
spawn-protection=0
view-distance=6
simulation-distance=6
EOF
}

start() {
    local dir="$1" jar="${2:-}"
    [ -n "$jar" ] || jar="$(ls -t "$ROOT"/folia-server/build/libs/*-paperclip-*.jar | head -1)"
    init "$dir"
    cp "$jar" "$dir/server.jar"
    rm -f "$dir/out.log"
    (cd "$dir" && nohup "$JAVA" -Xmx2G ${TESSERA_JAVA_OPTS:-} -jar server.jar --nogui > out.log 2>&1 & echo $! > "$dir/server.pid")
    for _ in $(seq 1 600); do
        grep -qE 'Done \(' "$dir/out.log" 2>/dev/null && { echo "started: port $(property "$dir" server-port), rcon $(property "$dir" rcon.port)"; return 0; }
        grep -qE 'Failed to start|Exception in server tick loop' "$dir/out.log" 2>/dev/null && break
        sleep 0.5
    done
    echo "server did not start, see $dir/out.log" >&2
    tail -20 "$dir/out.log" >&2
    return 1
}

stop() {
    local dir="$1" pid
    pid="$(cat "$dir/server.pid" 2>/dev/null || true)"
    rcon "$dir" stop > /dev/null 2>&1 || true
    for _ in $(seq 1 60); do
        [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null || { rm -f "$dir/server.pid"; return 0; }
        sleep 0.5
    done
    kill -9 "$pid" 2>/dev/null || true
    rm -f "$dir/server.pid"
}

errors() {
    if grep -aE 'ERROR|Exception' "$1/out.log"; then return 1; fi
    echo "no errors"
}

bot() {
    "$PYTHON" "$ROOT/tools/joinbot.py" "$(property "$1" server-port)" "$2" "$3" > "$1/bot-$2.log" 2>&1 &
}

command="${1:-}"
[ $# -ge 2 ] || { sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }
shift
case "$command" in
    start) start "$@" ;;
    stop) stop "$1" ;;
    rcon) rcon "$@" ;;
    bot) bot "$@" ;;
    errors) errors "$1" ;;
    *) echo "unknown command: $command" >&2; exit 2 ;;
esac
