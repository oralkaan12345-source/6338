#!/usr/bin/env python3
"""Generate and fit a Kokoro narration locally; one input line per scene."""
from argparse import ArgumentParser
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import wave

from kokoro_onnx import Kokoro
import numpy as np


def read_pcm(path):
    with wave.open(str(path), "rb") as wav:
        return wav.readframes(wav.getnframes())


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("script", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--model", required=True, type=Path)
    p.add_argument("--voices", required=True, type=Path)
    p.add_argument("--voice", default="af_heart")
    p.add_argument("--lang", default="en-us")
    p.add_argument("--ends", nargs="+", type=float, required=True,
                   help="Cumulative end time of each scene, seconds")
    a = p.parse_args()
    lines = [line.strip() for line in a.script.read_text(encoding="utf-8").splitlines()
             if line.strip()]
    if not lines or len(lines) != len(a.ends) or any(
            not np.isfinite(end) or end - start < .35
            for start, end in zip([0] + a.ends[:-1], a.ends)):
        p.error("Give one increasing scene end per script line; min scene duration 0.35 s.")
    if a.output.exists():
        p.error("Output exists; choose another filename.")
    tts = Kokoro(str(a.model), str(a.voices))
    frames = []
    with TemporaryDirectory(prefix="kokoro-") as tmp:
        tmp = Path(tmp)
        for i, (line, start, end) in enumerate(zip(lines, [0] + a.ends[:-1], a.ends)):
            # Keep acronyms as individual letters/digits when read out.
            text = line.replace(" C four ", " C-four ").replace(" V eight ", " V-eight ")
            samples, rate = tts.create(text, voice=a.voice, lang=a.lang,
                                       speed=1., sentence_pause=.18, clause_pause=.1)
            n = round(end * 48000) - round(start * 48000)
            available = (n - 16320) / 48000 if n > 24000 else n / 48000 * .78
            speed = max(1., len(samples) / rate / available)
            if speed > 1.33:
                raise ValueError(f"Scene {i+1} would need {speed:.2f}x speech; shorten its line.")
            raw, proc = tmp / "raw.wav", tmp / "proc.wav"
            pcm = np.int16(np.clip(samples, -1., 1.) * 32767.)
            with wave.open(str(raw), "wb") as wav:
                wav.setparams((1, 2, rate, 0, "NONE", "not compressed"))
                wav.writeframes(pcm.tobytes())
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y",
                            "-i", str(raw), "-af",
                            f"atempo={speed:.5f},highpass=f=70,loudnorm=I=-17:TP=-2:LRA=10",
                            "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(proc)],
                           check=True)
            voiced = read_pcm(proc)
            lead = min(3840, n // 10)
            if len(voiced) > (n - lead) * 2:
                raise ValueError(f"Scene {i+1} unexpectedly overran its time allocation.")
            frames.append(b"\0" * (lead * 2) + voiced +
                          b"\0" * ((n - lead) * 2 - len(voiced)))
            print(f"{i+1}: {start:.2f}–{end:.2f}s, speech={len(voiced)/96000:.2f}s, speed={speed:.2f}x")
    with a.output.open("xb") as dst, wave.open(dst, "wb") as wav:
        wav.setparams((1, 2, 48000, 0, "NONE", "not compressed"))
        wav.writeframes(b"".join(frames))


if __name__ == "__main__":
    main()
