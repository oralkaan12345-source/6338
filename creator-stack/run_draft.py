#!/usr/bin/env python3
"""Run the local multi-role and media preflight workflow without publishing."""
import argparse
from pathlib import Path
import subprocess
import sys

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--brief", type=Path, required=True)
    p.add_argument("--video", type=Path, required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--description", required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--language", default="tr")
    p.add_argument("--model", help="Optional Ollama model already installed on local computer.")
    a = p.parse_args()
    root = Path(__file__).resolve().parent
    if not a.brief.is_file() or not a.video.is_file():
        p.error("Provide an existing brief JSON and local video.")
    if a.output_dir.exists():
        p.error("Output folder already exists. Choose a new folder.")
    a.output_dir.mkdir(parents=True)
    draft = a.output_dir / "editorial-draft.json"
    agent = [sys.executable, str(root/"agents"/"pipeline.py"), "--brief", str(a.brief), "--output", str(draft)]
    if a.model:
        agent.extend(["--model", a.model])
    result = subprocess.run(agent, check=False)
    if result.returncode:
        print("Agent workflow did not pass QA. Review its draft if present; no Studio metadata was prepared.", file=sys.stderr)
        return result.returncode
    prep = [sys.executable, str(root/"youtube"/"prepare_short.py"), "--video", str(a.video),
            "--title", a.title, "--description", a.description, "--language", a.language,
            "--audience", "review", "--output-dir", str(a.output_dir/"studio")]
    result = subprocess.run(prep, check=False)
    if not result.returncode:
        print(f"Drafts saved in {a.output_dir}; nothing uploaded or published.")
    return result.returncode

if __name__ == "__main__":
    raise SystemExit(main())
