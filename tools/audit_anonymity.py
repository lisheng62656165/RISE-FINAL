"""Scan tracked source or a supplementary zip for identity and secret leaks."""

from __future__ import annotations

import argparse
import configparser
from pathlib import Path, PurePosixPath
import re
import subprocess
from urllib.parse import urlparse
import zipfile


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".cfg", ".csv", ".html", ".ini", ".json", ".jsonl", ".md", ".ps1",
    ".py", ".sh", ".toml", ".txt", ".yaml", ".yml",
}
EMAIL = re.compile(rb"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
STATIC_PATTERNS = {
    "openai_key": re.compile(rb"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "nvidia_key": re.compile(rb"\bnvapi-[A-Za-z0-9_-]{20,}\b"),
    "github_token": re.compile(rb"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    "huggingface_token": re.compile(rb"\bhf_[A-Za-z0-9]{20,}\b"),
    "aws_access_key": re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
}
GENERIC_HOME = re.compile(
    rb"(?:[A-Za-z]:\\Users\\[^\\\s]+|/(?:home|Users)/[^/\s]+)", re.IGNORECASE
)
FORBIDDEN_ARCHIVE_PARTS = {
    ".git", ".github", ".venv", ".asset-cache", ".pytest_cache",
    "__pycache__", "outputs", "results", "scores", "logs", "runtime",
}
FORBIDDEN_ARCHIVE_SUFFIXES = {".bundle", ".key", ".log", ".part", ".pyc", ".whl"}


def configured_markers() -> dict[str, bytes]:
    markers = {
        "home_path": str(Path.home()).encode(),
        "home_posix": Path.home().as_posix().encode(),
        "os_username": Path.home().name.encode(),
    }
    config_path = ROOT / ".git" / "config"
    if config_path.is_file():
        config = configparser.ConfigParser()
        config.read(config_path, encoding="utf-8")
        for section in config.sections():
            if section.startswith('remote "') and config.has_option(section, "url"):
                url = config.get(section, "url")
                markers["git_remote"] = url.encode()
                markers["git_remote_without_suffix"] = url.removesuffix(".git").encode()
                account = urlparse(url).path.strip("/").split("/", 1)[0]
                if account:
                    markers["publishing_account"] = account.encode()
    return {name: value for name, value in markers.items() if value}


def tracked_files() -> list[tuple[str, bytes]]:
    output = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=ROOT
    )
    result = []
    for raw in output.split(b"\0"):
        if not raw:
            continue
        relative = raw.decode("utf-8", errors="surrogateescape")
        path = ROOT / relative
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            result.append((relative.replace("\\", "/"), path.read_bytes()))
    return result


def archive_files(path: Path) -> list[tuple[str, bytes]]:
    result = []
    with zipfile.ZipFile(path) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            relative = PurePosixPath(member.filename)
            if set(relative.parts) & FORBIDDEN_ARCHIVE_PARTS:
                raise SystemExit(f"forbidden directory in archive: {member.filename}")
            if relative.suffix.lower() in FORBIDDEN_ARCHIVE_SUFFIXES:
                raise SystemExit(f"forbidden file type in archive: {member.filename}")
            if relative.suffix.lower() in TEXT_SUFFIXES:
                result.append((member.filename, archive.read(member)))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    files = archive_files(args.archive.resolve()) if args.archive else tracked_files()

    patterns = dict(STATIC_PATTERNS)
    for name, marker in configured_markers().items():
        patterns[name] = re.compile(re.escape(marker), re.IGNORECASE)

    leaks: list[tuple[str, str]] = []
    email_files: set[str] = set()
    fixture_home_files: set[str] = set()
    for name, data in files:
        if EMAIL.search(data):
            email_files.add(name)
        if GENERIC_HOME.search(data):
            normalized = name.removeprefix("RISE/")
            if normalized.startswith("rise/occubench/data/"):
                fixture_home_files.add(name)
            else:
                leaks.append(("home_path", name))
        for kind, pattern in patterns.items():
            if pattern.search(data):
                leaks.append((kind, name))

    print(f"Scanned {len(files)} text files.")
    print(f"Email-shaped fixture/attribution strings: {len(email_files)} files.")
    print(f"Virtual benchmark home paths: {len(fixture_home_files)} files.")
    if leaks:
        for kind, name in sorted(set(leaks)):
            print(f"LEAK {kind}: {name}")
        raise SystemExit(1)
    print("No configured identity, home-path, or credential patterns found.")


if __name__ == "__main__":
    main()
