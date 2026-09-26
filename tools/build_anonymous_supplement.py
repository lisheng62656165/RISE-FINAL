"""Build a double-blind source archive without Git or downloaded assets."""

from __future__ import annotations

import argparse
import configparser
import fnmatch
from pathlib import Path
from urllib.parse import urlparse
import zipfile


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {
    ".git",
    ".github",
    ".venv",
    ".asset-cache",
    ".pytest_cache",
    "__pycache__",
    ".codex",
    ".paper-memory",
    "outputs",
    "results",
    "scores",
    "logs",
    "runtime",
}
EXCLUDED_PREFIXES = {
    "appworld/assets/wheels-linux-py312",
    "deepplanning/shoppingplanning/database_level1",
    "deepplanning/shoppingplanning/database_level2",
    "deepplanning/shoppingplanning/database_level3",
    "deepplanning/travelplanning/database/database_zh",
    "deepplanning/travelplanning/database/database_en",
    "rise/occubench/vendor/wheels-linux-py312",
    "rise/occubench/vendor/wheels-win-py312",
}
EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".whl",
    ".bundle",
    ".part",
    ".log",
}
EXCLUDED_NAMES = {".env", ".DS_Store", "Thumbs.db"}


def remote_markers() -> set[bytes]:
    markers: set[bytes] = set()
    config_path = ROOT / ".git" / "config"
    if config_path.is_file():
        config = configparser.ConfigParser()
        config.read(config_path, encoding="utf-8")
        for section in config.sections():
            if section.startswith('remote "') and config.has_option(section, "url"):
                url = config.get(section, "url")
                markers.add(url.encode())
                markers.add(url.removesuffix(".git").encode())
                parsed = urlparse(url)
                account = parsed.path.strip("/").split("/", 1)[0]
                if account:
                    markers.add(account.encode())
    home = Path.home()
    markers.add(str(home).encode())
    markers.add(home.as_posix().encode())
    markers.add(home.name.encode())
    return {marker for marker in markers if marker}


def excluded(relative: Path) -> bool:
    parts = set(relative.parts)
    posix = relative.as_posix()
    return (
        bool(parts & EXCLUDED_DIRS)
        or any(posix == prefix or posix.startswith(prefix + "/") for prefix in EXCLUDED_PREFIXES)
        or relative.suffix.lower() in EXCLUDED_SUFFIXES
        or relative.name in EXCLUDED_NAMES
        or any(
            fnmatch.fnmatch(relative.name.lower(), pattern)
            for pattern in ("api_key*", "api_*.txt", "key*.txt", "*.key", "*.secret")
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT):
        raise SystemExit("write the supplementary archive outside the repository")

    files = [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and not excluded(path.relative_to(ROOT))
    ]
    markers = remote_markers()
    leaks: list[str] = []
    for path in files:
        data = path.read_bytes()
        if any(marker in data for marker in markers):
            leaks.append(path.relative_to(ROOT).as_posix())
    if leaks:
        raise SystemExit("identity-bearing text found in: " + ", ".join(leaks))

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".part")
    temporary.unlink(missing_ok=True)
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(files):
            relative = path.relative_to(ROOT)
            archive.write(path, Path("RISE") / relative)
    temporary.replace(output)
    print(f"Created {output} with {len(files)} files ({output.stat().st_size / 1024 / 1024:.1f} MiB).")


if __name__ == "__main__":
    main()
