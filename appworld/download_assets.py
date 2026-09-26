"""Download the official encrypted AppWorld data and pinned package wheel."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
MANIFEST = ASSETS / "manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        help="Use already downloaded files from this directory (for offline testing).",
    )
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ASSETS.mkdir(parents=True, exist_ok=True)

    for entry in manifest["assets"]:
        target = ASSETS / entry["name"]
        if target.is_file() and target.stat().st_size == entry["size"] and sha256(target) == entry["sha256"]:
            print(f"Ready: {target.name}")
            continue
        partial = target.with_suffix(target.suffix + ".part")
        partial.unlink(missing_ok=True)
        if args.source_dir is not None:
            source = args.source_dir / entry["name"]
            if not source.is_file():
                raise FileNotFoundError(source)
            shutil.copy2(source, partial)
        else:
            print(f"Downloading {target.name} ({entry['size'] / 1024 / 1024:.1f} MiB)...")
            urllib.request.urlretrieve(entry["url"], partial)
        if partial.stat().st_size != entry["size"] or sha256(partial) != entry["sha256"]:
            partial.unlink(missing_ok=True)
            raise RuntimeError(f"download verification failed: {target.name}")
        partial.replace(target)
        print(f"Installed: {target.name}")


if __name__ == "__main__":
    main()
