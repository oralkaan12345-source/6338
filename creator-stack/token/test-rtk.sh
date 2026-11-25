#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
state="$root/.state"
mkdir -p "$state/config" "$state/data"
export XDG_CONFIG_HOME="$state/config" XDG_DATA_HOME="$state/data"
export RTK_TELEMETRY_DISABLED=1 RTK_DB_PATH="$state/rtk.sqlite"
fixture="$(mktemp -d "$state/bench.XXXXXX")"
trap 'rm -rf -- "$fixture"' EXIT
git -C "$fixture" init -q -b main
cd "$fixture"
mkdir -p video tests
for i in {01..20}; do printf 'fixture %s\n' "$i" > "video/scene-$i.txt"; done
git add video
git -c user.name=Fixture -c user.email=fixture@example.invalid -c commit.gpgsign=false commit -qm 'create sample scenes'
for i in {01..06}; do printf 'revised %s\n' "$i" >> "video/scene-$i.txt"; done
for i in {01..04}; do printf 'staged %s\n' "$i" > "tests/test-$i.txt"; done
git add tests
for i in {07..18}; do printf 'pending %s\n' "$i" > "tests/test-$i.txt"; done
git -c color.status=never -c core.quotePath=false status > "$state/raw-git-status.txt"
"$root/bin/rtk" git status > "$state/rtk-git-status.txt"
"$root/bin/rtk" telemetry status > "$state/telemetry-status.txt"
"$root/bin/rtk" gain --text > "$state/gain.txt"
python3 - "$state/raw-git-status.txt" "$state/rtk-git-status.txt" <<'PY'
import sys
from pathlib import Path
before, after = [Path(p).read_bytes() for p in sys.argv[1:]]
assert b"video/scene-" in before and b"test-" in before
assert before != after and 0 < len(after) < len(before)
pct = (1 - len(after)/len(before)) * 100
print(f'Raw: {len(before)} bytes / {len(before.splitlines())} lines')
print(f'RTK: {len(after)} bytes / {len(after.splitlines())} lines')
print(f'Output size reduction: {pct:.2f}% (bytes, not a billing guarantee)')
PY
