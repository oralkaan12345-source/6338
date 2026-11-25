#!/usr/bin/env python3
"""Tests use local throwaway media; no API/network traffic."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from prepare_short import ValidationError, inspect_srt, probe_video, validate_metadata


class MetadataTests(unittest.TestCase):
    def test_utf8_limits_and_normalization(self):
        s = validate_metadata(" Şafak ", "Üç sahne.", ["3D kısa film", "3d kısa film"], "tr")
        self.assertEqual(s["title"], "Şafak")
        self.assertEqual(s["tags"], ["3D kısa film"])
        with self.assertRaisesRegex(ValidationError, "5000 UTF-8 bytes"):
            validate_metadata("Başlık", "ş" * 2501, [], "tr")
        with self.assertRaisesRegex(ValidationError, "1–100"):
            validate_metadata("x" * 101, "", [], "tr")

    def test_tags_count_delimiters(self):
        validate_metadata("Başlık", "", ["a a", "b" * 494], "tr")
        with self.assertRaisesRegex(ValidationError, "Tags exceed"):
            validate_metadata("Başlık", "", ["a a", "b" * 495], "tr")

    def test_caption_validation(self):
        with tempfile.TemporaryDirectory() as root:
            srt = Path(root) / "tr.srt"
            srt.write_text("1\n00:00:00,000 --> 00:00:00,900\nBir ışık göründü.\n",
                           encoding="utf-8")
            self.assertEqual(inspect_srt(srt, 1000)["cue_count"], 1)
            with self.assertRaisesRegex(ValidationError, "beyond"):
                inspect_srt(srt, 300)
            srt.write_text("1\n00:00:00,000 --> 00:00:00,500\na\n\n"
                           "2\n00:00:00,400 --> 00:00:00,800\nb\n", encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "overlaps"):
                inspect_srt(srt, 1000)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "requires FFmpeg")
class MediaTests(unittest.TestCase):
    def local_mp4(self, root, name, size, sec=1):
        p = root / f"{name}.mp4"
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                        f"color=c=navy:s={size}:r=1", "-f", "lavfi", "-i",
                        "sine=frequency=220:sample_rate=16000", "-t", str(sec),
                        "-c:v", "libx264", "-c:a", "aac", str(p)], check=True)
        return p

    def test_vertical_cli_and_redundant_output(self):
        with tempfile.TemporaryDirectory() as work:
            w = Path(work)
            vid = self.local_mp4(w, "tiny", "90x160")
            cmd = [sys.executable, str(Path(__file__).with_name("prepare_short.py")),
                   "--video", str(vid), "--title", "Deniz ışığı", "--description", "Kurgu.",
                   "--tag", "kısa film", "--output-dir", str(w / "draft")]
            subprocess.run(cmd, check=True, capture_output=True)
            draft = json.loads((w/"draft"/"short-draft.json").read_text(encoding="utf-8"))
            self.assertEqual(draft["media"]["display_aspect_ratio"], "9:16")
            self.assertEqual(draft["media"]["duration_seconds"], 1)
            self.assertEqual(draft["review_settings"]["privacyStatus"], "private")
            self.assertFalse(draft["published"])
            self.assertFalse(draft["uploaded"])
            self.assertTrue((w/"draft"/"youtube-studio.txt").is_file())
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 2)

    def test_landscape_rejected_and_square_accepted(self):
        with tempfile.TemporaryDirectory() as work:
            w = Path(work)
            landscape = self.local_mp4(w, "wide", "160x90")
            with self.assertRaisesRegex(ValidationError, "square or vertical"):
                probe_video(landscape)
            square = self.local_mp4(w, "square", "96x96")
            self.assertEqual(probe_video(square)["display_aspect_ratio"], "1:1")

    def test_long_short_and_playlist_rejected(self):
        with tempfile.TemporaryDirectory() as work:
            w = Path(work)
            too_long = self.local_mp4(w, "long", "18x32", sec=181)
            with self.assertRaisesRegex(ValidationError, "180-second limit"):
                probe_video(too_long)
            playlist = w / "network.m3u8"
            playlist.write_text("#EXTM3U\n#EXTINF:10,\nhttps://example.invalid/segment.ts\n",
                                encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "could not read"):
                probe_video(playlist)

    def test_rotated_landscape_is_displayed_vertical(self):
        with tempfile.TemporaryDirectory() as work:
            w = Path(work)
            p = self.local_mp4(w, "wide", "160x90")
            rotated = w / "rotated.mp4"
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-display_rotation", "90",
                            "-i", str(p), "-c", "copy", str(rotated)], check=True)
            facts = probe_video(rotated)
            self.assertEqual(facts["display_aspect_ratio"], "9:16")
            self.assertIn(facts["rotation_degrees"], (90, 270))


if __name__ == "__main__":
    unittest.main()
