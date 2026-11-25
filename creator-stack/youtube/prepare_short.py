#!/usr/bin/env python3
"""Validate a rendered Short and prepare local metadata for manual Studio review."""
import argparse
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

FIELDS = {
    "title_limit_characters": 100,
    "description_limit_utf8_bytes": 5000,
    "tags_limit_characters_including_delimiters": 500,
    "short_duration_limit_seconds": 180,
}
CAP_TS = r"(\d{2,}):(\d{2}):(\d{2})[,.](\d{3})"


class ValidationError(Exception):
    """An input did not pass the local preflight."""


def check(cond, message):
    if not cond:
        raise ValidationError(message)


def identity(path):
    with path.open("rb") as stream:
        h = sha256()
        while chunk := stream.read(2 ** 20):
            h.update(chunk)
    return {"filename": path.name, "bytes": path.stat().st_size, "sha256": h.hexdigest()}


def utf8(path):
    return path.read_text(encoding="utf-8-sig")


def require_clean(value, field, multiline=False):
    check("<" not in value and ">" not in value, f"{field}: '<' and '>' are not allowed.")
    check(all(ord(c) >= 32 or (multiline and c in "\n\t") for c in value),
          f"{field}: contains an unsupported control character.")


def validate_metadata(title, description, tags, language):
    title, description = title.strip(), description.strip()
    check(0 < len(title) <= FIELDS["title_limit_characters"],
          "Title must contain 1–100 characters.")
    require_clean(title, "Title")
    require_clean(description, "Description", multiline=True)
    check(len(description.encode("utf-8")) <= FIELDS["description_limit_utf8_bytes"],
          "Description exceeds 5000 UTF-8 bytes.")
    clean = []
    seen = set()
    for tag in tags:
        tag = tag.strip()
        check(tag and "," not in tag,
              "Enter one nonempty tag per --tag argument (commas are not valid here).")
        require_clean(tag, "Tag")
        if tag.casefold() not in seen:
            clean.append(tag)
            seen.add(tag.casefold())
    tag_units = sum(len(tag) + (2 if " " in tag else 0) for tag in clean)
    tag_units += max(0, len(clean) - 1)
    check(tag_units <= FIELDS["tags_limit_characters_including_delimiters"],
          "Tags exceed 500 characters (separating commas and quotes around spaces count).")
    check(re.fullmatch(r"[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*", language),
          "Language must look like a BCP 47 code, for example tr or en-US.")
    return {"title": title, "description": description, "tags": clean,
            "defaultLanguage": language}


def probe_video(path):
    ffprobe = shutil.which("ffprobe")
    check(ffprobe, "ffprobe is required. Install the FFmpeg package first.")
    check(path.is_file(), f"Video not found: {path}")
    try:
        raw = subprocess.run([ffprobe, "-v", "error", "-protocol_whitelist", "file",
                              "-format_whitelist", "mov,matroska,webm,avi,mpegts",
                              "-show_streams", "-show_format", "-of", "json", str(path.resolve())],
                             capture_output=True, text=True, timeout=45)
    except subprocess.TimeoutExpired as exc:
        raise ValidationError("Video inspection timed out.") from exc
    check(raw.returncode == 0, "ffprobe could not read this file as valid media.")
    try:
        facts = json.loads(raw.stdout)
    except json.JSONDecodeError as exc:
        raise ValidationError("ffprobe returned unreadable metadata.") from exc
    streams = facts.get("streams", [])
    vid = next((s for s in streams if s.get("codec_type") == "video"
                and not (s.get("disposition") or {}).get("attached_pic")), None)
    check(vid is not None, "No actual video stream found.")
    aud = [s for s in streams if s.get("codec_type") == "audio"]
    vw, vh = vid.get("width", 0), vid.get("height", 0)
    check(isinstance(vw, int) and isinstance(vh, int) and vw > 0 and vh > 0,
          "Invalid video dimensions.")
    try:
        ratio = vid.get("sample_aspect_ratio", "1:1")
        sar = Fraction(ratio.replace(":", "/"))
        if sar <= 0:
            sar = Fraction(1)
    except (ValueError, ZeroDivisionError, AttributeError):
        sar = Fraction(1)
    raw_rot = next((s["rotation"] for s in vid.get("side_data_list", []) if "rotation" in s),
                   (vid.get("tags") or {}).get("rotate", 0))
    try:
        rotation = int(float(raw_rot)) % 360
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValidationError("Unreadable rotation metadata.") from exc
    check(rotation in (0, 90, 180, 270),
          "Rotation must be a multiple of 90° for this offline preflight.")
    display_width, display_height = Fraction(vw) * sar, Fraction(vh)
    if rotation in (90, 270):
        display_width, display_height = display_height, display_width
    check(display_width <= display_height, "Short must be square or vertical (display orientation).")
    formats = facts.get("format") or {}
    candidates = [formats.get("duration"), vid.get("duration")]
    seconds = None
    for value in candidates:
        try:
            d = Decimal(str(value))
        except InvalidOperation:
            continue
        if d.is_finite() and d > 0:
            seconds = d
            break
    check(seconds is not None, "Could not determine a positive duration.")
    check(seconds <= FIELDS["short_duration_limit_seconds"], "Short exceeds the 180-second limit.")
    ratio = display_width / display_height
    warnings = []
    if not aud:
        warnings.append("No audio stream; confirm intentionally silent.")
    if vid.get("codec_name") != "h264" or not any(s.get("codec_name") == "aac" for s in aud):
        warnings.append("For broad compatibility, consider H.264 video and AAC audio in MP4.")
    if seconds > 60:
        warnings.append("A Short over 60 seconds with an active Content ID claim can be blocked.")
    return {
        **identity(path),
        "container": formats.get("format_name"),
        "width": vw, "height": vh,
        "rotation_degrees": rotation,
        "display_aspect_ratio": f"{ratio.numerator}:{ratio.denominator}",
        "duration_seconds": float(seconds),
        "duration_milliseconds": int((seconds * 1000).to_integral_value(
            rounding=ROUND_HALF_UP)),
        "video_codec": vid.get("codec_name"),
        "audio_codecs": [s.get("codec_name") for s in aud],
        "orientation_duration_preflight_passed": True,
        "warnings": warnings,
    }


def srt_time(parts):
    h, m, s, ms = map(int, parts)
    check(m < 60 and s < 60, "SRT timestamp minute/second out of range.")
    return ((h * 60 + m) * 60 + s) * 1000 + ms


def inspect_srt(path, duration_ms):
    payload = utf8(path).strip()
    check(payload, "SRT must not be empty.")
    chunks = re.split(r"\n[ \t]*\n", payload)
    last_end = 0
    for i, chunk in enumerate(chunks, 1):
        lines = chunk.splitlines()
        check(len(lines) >= 3 and lines[0].strip().isdigit() and
              any(x.strip() for x in lines[2:]), f"Malformed SRT cue {i}.")
        m = re.fullmatch(CAP_TS + r"\s+-->\s+" + CAP_TS, lines[1].strip())
        check(m is not None, f"Malformed SRT timestamp in cue {i}.")
        start, end = srt_time(m.groups()[:4]), srt_time(m.groups()[4:])
        check(start >= last_end and end > start and end <= duration_ms + 1,
              f"SRT cue {i} overlaps, has an invalid interval, or extends beyond the media.")
        last_end = end
    return {**identity(path), "cue_count": len(chunks), "last_end_ms": last_end}


def studio_text(draft):
    snip, status = draft["snippet"], draft["review_settings"]
    checklist = [
        "[ ] Görüntüyü, sesi ve telefon ekranında altyazıyı son kez izle.",
        "[ ] Müzik/görsel haklarını ve varsa sentetik içerik beyanını değerlendir.",
        "[ ] Çocuklara özel hedef kitle seçimini doğrula.",
        "[ ] Studio’da görünürlüğü Özel olarak seç; bu dosya otomatik yükleme yapmaz.",
    ]
    if draft["caption_file"]:
        checklist.append("[ ] Doğru dildeki SRT dosyasını Studio’da ayrıca ekle.")
    return "\n".join([
        "YOUTUBE STUDIO — YEREL TASLAK",
        "",
        f"Video: {draft['media']['filename']}",
        "Başlık:", snip["title"], "",
        "Açıklama:", snip["description"] or "(boş)", "",
        "Etiketler: " + (", ".join(snip["tags"]) or "(yok)"),
        f"Video dili: {snip['defaultLanguage']}",
        "Planlanan görünürlük: Özel (private)",
        f"Hedef kitle: {status['audience']}",
        "",
        *checklist, "",
    ])


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--video", type=Path, required=True)
    p.add_argument("--title", required=True)
    desc = p.add_mutually_exclusive_group()
    desc.add_argument("--description")
    desc.add_argument("--description-file", type=Path)
    p.add_argument("--tag", action="append", default=[])
    p.add_argument("--language", default="tr")
    p.add_argument("--audience", choices=["review", "made-for-kids", "not-made-for-kids"],
                   default="review")
    p.add_argument("--caption-file", type=Path, help="Optional separate SRT file; no copy or upload.")
    p.add_argument("--output-dir", type=Path, required=True,
                   help="A new output directory; it must not already exist.")
    return p


def main():
    args = parser().parse_args()
    try:
        dsc = utf8(args.description_file) if args.description_file else args.description or ""
        snippet = validate_metadata(args.title, dsc, args.tag, args.language)
        media = probe_video(args.video)
        cap = inspect_srt(args.caption_file, media["duration_milliseconds"]) if args.caption_file else None
        setting = {"privacyStatus": "private", "audience": args.audience}
        if args.audience != "review":
            setting["selfDeclaredMadeForKids"] = args.audience == "made-for-kids"
        draft = {
            "manifest_version": 1,
            "mode": "local_draft_only",
            "snippet": snippet,
            "review_settings": setting,
            "media": media,
            "caption_file": cap,
            "review_gates": [
                "Confirm rendering, branding, and audio/captions",
                "Review rights, platform policies, and synthetic-content disclosures",
                "Confirm audience and private visibility in YouTube Studio before any upload",
            ],
            "uploaded": False,
            "published": False,
        }
        args.output_dir.mkdir(parents=True, exist_ok=False)
        with (args.output_dir / "short-draft.json").open("x", encoding="utf-8") as out:
            json.dump(draft, out, ensure_ascii=False, indent=2)
            out.write("\n")
        with (args.output_dir / "youtube-studio.txt").open("x", encoding="utf-8") as out:
            out.write(studio_text(draft))
        print(f"Local draft: {args.output_dir / 'short-draft.json'}")
        print(f"Studio fields: {args.output_dir / 'youtube-studio.txt'}")
        for warning in media["warnings"]:
            print(f"Review: {warning}")
    except (ValidationError, OSError, UnicodeError) as exc:
        print(f"Preflight failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
