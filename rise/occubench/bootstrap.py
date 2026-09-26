#!/usr/bin/env python3
"""Create a reproducible environment for the OccuBench runner."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"


def python_in_venv() -> Path:
    return VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def main() -> None:
    if not VENV.exists():
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV)])
    python = python_in_venv()
    print("Installing pinned dependencies from the configured package index.", flush=True)
    command = [str(python), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")]
    subprocess.check_call(command)
    print(f"Environment ready: {python}")


if __name__ == "__main__":
    main()
