#!/usr/bin/env bash
set -euo pipefail
pin=2dc10e850d78c61264a64ea180def2b7f1f334d8
root=${1:-"$PWD/.video-tools"}
mkdir -p "$root"
root=$(cd "$root" && pwd)
src="$root/MoneyPrinterTurbo"
if [ ! -d "$src/.git" ]; then
  git clone --no-checkout https://github.com/harry0703/MoneyPrinterTurbo.git "$src"
fi
cd "$src"
git checkout --detach "$pin"
python_bin=${PYTHON_BIN:-$(command -v python3)}
UV_HTTP_TIMEOUT="${UV_HTTP_TIMEOUT:-30}" UV_CONCURRENT_DOWNLOADS="${UV_CONCURRENT_DOWNLOADS:-4}" \
  UV_CACHE_DIR="$root/uv-cache" UV_PROJECT_ENVIRONMENT="$root/venv" \
  uv sync --frozen --no-dev --python "$python_bin"
MPT_HOME="$root/data" "$root/venv/bin/mpt" cli --help >/dev/null
printf 'MoneyPrinterTurbo %s ready: %s\n' "$pin" "$root/venv/bin/mpt"
