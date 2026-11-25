#!/usr/bin/env bash
set -euo pipefail
out=${1:-video-smoke.mp4}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cat >"$tmp/subs.srt" <<'SRT'
1
00:00:00,000 --> 00:00:02,000
Cloud video test

2
00:00:02,000 --> 00:00:04,000
Two scenes. No upload.
SRT
cd "$tmp"
export XDG_CACHE_HOME="$tmp/cache"
mkdir -p "$XDG_CACHE_HOME"
# Distinct scenes, an offline spoken English sample, and burned-in subtitles.
ffmpeg -nostdin -hide_banner -loglevel error -y \
  -f lavfi -i 'color=0x15294a:s=1080x1920:r=24:d=2' \
  -f lavfi -i 'color=0x204640:s=1080x1920:r=24:d=2' \
  -f lavfi -i "flite=text='This is a cloud video test. Two scenes. No upload.':voice=slt" \
  -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0,subtitles=subs.srt,format=yuv420p[v]" \
  -map '[v]' -map 2:a -af apad -t 4 -c:v libx264 -preset ultrafast -threads 2 \
  -c:a aac -movflags +faststart preview.mp4
ffprobe -v error -show_entries stream=codec_name,width,height -show_entries format=duration -of json preview.mp4 |
  python3 -c 'import json,sys; d=json.load(sys.stdin); v,a=d["streams"]; assert (v["codec_name"],v["width"],v["height"],a["codec_name"])==("h264",1080,1920,"aac"); assert abs(float(d["format"]["duration"])-4)<.1; print("Verified 1080x1920 H.264 + AAC, 4 seconds.")'
cd - >/dev/null
cp -- "$tmp/preview.mp4" "$out"
printf 'Wrote %s\n' "$out"
