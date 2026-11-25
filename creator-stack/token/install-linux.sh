#!/usr/bin/env bash
set -euo pipefail
if [[ "$(uname -s)/$(uname -m)" != Linux/x86_64 ]]; then
  echo "This pinned setup targets Linux x86_64 (including x86_64 WSL)." >&2
  exit 1
fi
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
upstream="$root/../upstream/token"
version=v1.2.1
archive=rtk-oss-x86_64-unknown-linux-musl.tar.gz
sha=44aa460c4827d206d11405c652832c9f7082edccfbc3a9f15a69a851e8a9e8b4
mkdir -p "$root/bin" "$upstream"
check() { (cd "$upstream"; printf '%s  %s\n' "$sha" "$1" | sha256sum -c -); }
if [[ ! -f "$upstream/$archive" ]]; then
  partial="$(mktemp "$upstream/.rtk.XXXXXX")"
  trap 'rm -f -- "$partial"' EXIT
  curl --fail --location --proto '=https' --max-time 90 --retry 2     "https://github.com/rtk-ai/rtk/releases/download/$version/$archive" -o "$partial"
  check "$(basename "$partial")"
  mv -- "$partial" "$upstream/$archive"
fi
check "$archive"
tar -xzf "$upstream/$archive" -C "$root/bin" -- rtk LICENSE
"$root/bin/rtk" --version
