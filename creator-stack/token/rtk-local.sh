#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$root/.state/config" "$root/.state/data"
export XDG_CONFIG_HOME="$root/.state/config" XDG_DATA_HOME="$root/.state/data"
export RTK_TELEMETRY_DISABLED=1 RTK_DB_PATH="$root/.state/rtk.sqlite"
exec "$root/bin/rtk" "$@"
