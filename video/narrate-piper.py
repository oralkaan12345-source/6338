#!/usr/bin/env python3
"""Render a Piper voice locally into exact per-scene timing."""
import argparse
import math
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import wave

from piper import PiperVoice
from piper.config import SynthesisConfig


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("script", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--model", required=True, type=Path)
    p.add_argument("--ends", required=True, nargs="+", type=float)
    a = p.parse_args()
    rate = 48_000
    start = [0.0] + a.ends[:-1]
    lines = [s.strip() for s in a.script.read_text(encoding="utf-8").splitlines() if s.strip()]
    if len(lines) != len(a.ends) or any(not math.isfinite(y) or y-x < .35 for x,y in zip(start,a.ends)):
        p.error("Provide one strictly increasing end time per nonempty line.")
    if a.output.exists():
        p.error("Output exists; choose another output.")
    voice = PiperVoice.load(a.model)
    with TemporaryDirectory() as tmp:
        raw = Path(tmp)/"raw.wav"
        proc = Path(tmp)/"proc.wav"
        result = []
        for i, (line, s, e) in enumerate(zip(lines,start,a.ends)):
            with wave.open(str(raw), "wb") as f:
                voice.synthesize_wav(line, f, syn_config=SynthesisConfig(length_scale=.95))
            with wave.open(str(raw), "rb") as f:
                raw_duration = f.getnframes()/f.getframerate()
            n = round(e*rate)-round(s*rate)
            lead = round(.06*rate)
            tail = round(.10*rate)
            pace = max(1.,raw_duration*rate/(n-lead-tail))
            if pace > 1.4:
                raise ValueError(f"Line {i+1} ({line}) needs {pace:.2f}x; shorten the narration.")
            subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-i",str(raw),
                "-af",f"atempo={pace:.5f},highpass=f=70,loudnorm=I=-17:TP=-2:LRA=10",
                "-ar",str(rate),"-ac","1","-c:a","pcm_s16le",str(proc)],check=True)
            with wave.open(str(proc),"rb") as f:
                data = f.readframes(f.getnframes())
            if len(data)//2 > n-lead:
                raise ValueError(f"Line {i+1} overruns the scene.")
            result.append(bytes(lead*2)+data+bytes((n-lead)*2-len(data)))
            print(f"{i+1:2}: {s:5.2f}–{e:5.2f}s, {len(data)/2/rate:.2f}s voiced, speed {pace:.2f}x", flush=True)
        with a.output.open("xb") as out, wave.open(out,"wb") as f:
            f.setparams((1,2,rate,0,"NONE","not compressed"))
            f.writeframes(b"".join(result))


if __name__ == "__main__":
    main()
