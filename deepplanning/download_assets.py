"""Download the official DeepPlanning databases used by this release."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
import tempfile
import urllib.request
import zipfile


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "assets" / "manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def complete(entry: dict[str, object]) -> bool:
    target = ROOT / str(entry["destination"]) / str(entry["top_level"])
    return target.is_dir() and len(list(target.glob(str(entry["expected_glob"])))) == int(
        entry["expected_count"]
    )


def safe_member_path(base: Path, member: str) -> Path:
    candidate = (base / member).resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError as error:
        raise RuntimeError(f"archive member escapes extraction root: {member}") from error
    return candidate


def extract_archive(archive: Path, entry: dict[str, object]) -> None:
    destination = ROOT / str(entry["destination"])
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / str(entry["top_level"])
    if target.exists():
        raise RuntimeError(
            f"partial asset already exists: {target}. Remove that directory and run again."
        )

    with tempfile.TemporaryDirectory(prefix="deepplanning-", dir=destination) as temporary:
        staging = Path(temporary)
        if entry["format"] == "zip":
            with zipfile.ZipFile(archive) as bundle:
                for member in bundle.infolist():
                    safe_member_path(staging, member.filename)
                bundle.extractall(staging)
        elif entry["format"] == "tar.gz":
            with tarfile.open(archive, "r:gz") as bundle:
                members = []
                for member in bundle.getmembers():
                    safe_member_path(staging, member.name)
                    if member.issym() or member.islnk():
                        raise RuntimeError(f"links are not allowed in asset archive: {member.name}")
                    members.append(member)
                bundle.extractall(staging, members=members)
        else:
            raise ValueError(f"unsupported archive format: {entry['format']}")

        extracted = staging / str(entry["top_level"])
        if not extracted.is_dir():
            raise RuntimeError(f"archive does not contain {entry['top_level']}/")
        shutil.move(str(extracted), str(target))

    if not complete(entry):
        raise RuntimeError(f"extracted asset failed its cohort-count check: {target}")


def download(entry: dict[str, object], cache: Path, source_dir: Path | None) -> Path:
    cache.mkdir(parents=True, exist_ok=True)
    archive = cache / str(entry["name"])
    if source_dir is not None:
        source = source_dir / str(entry["name"])
        if not source.is_file():
            raise FileNotFoundError(source)
        shutil.copy2(source, archive)
    elif not archive.exists() or archive.stat().st_size != int(entry["size"]):
        partial = archive.with_suffix(archive.suffix + ".part")
        partial.unlink(missing_ok=True)
        print(f"Downloading {entry['name']} ({int(entry['size']) / 1024 / 1024:.1f} MiB)...")
        urllib.request.urlretrieve(str(entry["url"]), partial)
        partial.replace(archive)

    if archive.stat().st_size != int(entry["size"]):
        raise RuntimeError(f"size mismatch for {archive.name}")
    actual = sha256(archive)
    if actual != entry["sha256"]:
        raise RuntimeError(f"SHA-256 mismatch for {archive.name}: {actual}")
    return archive


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=ROOT / ".asset-cache")
    parser.add_argument(
        "--source-dir",
        type=Path,
        help="Use already downloaded archives from this directory (for offline testing).",
    )
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for entry in manifest["assets"]:
        if complete(entry):
            print(f"Ready: {entry['top_level']}")
            continue
        archive = download(entry, args.cache_dir.resolve(), args.source_dir)
        extract_archive(archive, entry)
        print(f"Installed: {entry['top_level']}")

    print("DeepPlanning assets are ready. Run: python verify_release.py")


if __name__ == "__main__":
    main()
