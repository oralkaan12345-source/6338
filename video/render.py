#!/usr/bin/env python3
"""Render ordered user-owned stills with an existing narration (no network)."""
import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory


def run(*args, cwd=None, capture=False):
    return subprocess.run(args, check=True, cwd=cwd, text=True,
                          capture_output=capture).stdout


def probe(path):
    return json.loads(run("ffprobe", "-v", "error", "-show_format",
                          "-show_streams", "-of", "json", str(path),
                          capture=True))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--audio", required=True, type=Path, help="Narration audio")
    p.add_argument("--output", required=True, type=Path, help="New .mp4 file")
    p.add_argument("--subtitles", type=Path, help="Optional UTF-8 SRT")
    p.add_argument("--scene-seconds", type=float, nargs="+",
                   help="Optional per-image durations, summing to narration duration")
    p.add_argument("images", type=Path, nargs="+", help="Stills in playback order")
    a = p.parse_args()
    if a.output.suffix.lower() != ".mp4" or a.output.exists():
        p.error("--output must be a new .mp4 file")
    for path in [a.audio, *a.images, *([a.subtitles] if a.subtitles else [])]:
        if not path.is_file():
            p.error(f"Missing file: {path}")
    if not all(shutil.which(exe) for exe in ("ffmpeg", "ffprobe")):
        p.error("Install ffmpeg and ffprobe first")
    audio = probe(a.audio)
    try:
        audio_stream = next(s for s in audio["streams"] if s["codec_type"] == "audio")
        duration = float(audio_stream.get("duration") or audio["format"]["duration"])
    except (KeyError, ValueError, StopIteration):
        p.error("Could not determine the duration of the narration audio")
    if not math.isfinite(duration) or duration <= 0:
        p.error("Narration duration must be positive")
    timings = a.scene_seconds or [duration / len(a.images)] * len(a.images)
    if len(timings) != len(a.images) or any(not math.isfinite(x) or x < 1/24 for x in timings):
        p.error("Supply one duration per image, each at least one 24 fps frame")
    if abs(sum(timings) - duration) > 0.1:
        p.error("Scene durations must add up to the narration length (within 0.1 seconds)")
    if timings[-1] + duration - sum(timings) < 1/24:
        p.error("Last scene's adjusted duration is shorter than one frame")
    timings[-1] += duration - sum(timings)
    ff = ("ffmpeg", "-nostdin", "-v", "error")
    with TemporaryDirectory() as folder:
        work = Path(folder)
        listing = []
        elapsed, prev = 0.0, 0
        for i, (image, seconds) in enumerate(zip(a.images, timings)):
            elapsed += seconds
            end = math.ceil(elapsed * 24 - 1e-8)
            frames, prev = end - prev, end
            name = f"scene{i:04}.mp4"
            vf = ("scale=1080:1920:force_original_aspect_ratio=decrease:"
                  "force_divisible_by=2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:"
                  "color=0x101520,setsar=1,format=yuv420p")
            run(*ff, "-loop", "1", "-framerate", "24", "-i", str(image.resolve()),
                "-vf", vf, "-filter_threads", "2", "-frames:v", str(frames),
                "-an", "-c:v", "libx264", "-preset", "veryfast", "-threads", "2",
                "-crf", "20", name, cwd=work)
            listing.append(f"file '{name}'\n")
        (work / "scenes.txt").write_text("".join(listing), encoding="utf-8")
        if a.subtitles:
            shutil.copyfile(a.subtitles, work / "captions.srt")
            video = ("-vf", "subtitles=captions.srt", "-filter_threads", "2",
                     "-c:v", "libx264", "-preset", "veryfast", "-threads", "2", "-crf", "19")
        else:
            video = ("-c:v", "copy")
        run(*ff, "-n", "-f", "concat", "-safe", "1", "-i", "scenes.txt",
            "-i", str(a.audio.resolve()), "-map", "0:v:0", "-map", "1:a:0", *video,
            "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart",
            "render.mp4", cwd=work)
        rendered = probe(work / "render.mp4")
        streams = rendered["streams"]
        if not any(s["codec_name"] == "h264" and s.get("width") == 1080
                   and s.get("height") == 1920 for s in streams) or not any(
                       s["codec_name"] == "aac" for s in streams):
            raise SystemExit("Unexpected render streams")
        with a.output.open("xb") as dst, (work / "render.mp4").open("rb") as src:
            shutil.copyfileobj(src, dst)
    print(f"Rendered {a.output}: {len(a.images)} scenes, 1080×1920, {duration:.2f} s narration.")


if __name__ == "__main__":
    main()
