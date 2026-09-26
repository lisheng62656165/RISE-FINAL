"""Download official assets, install dependencies, and prepare AppWorld."""
import os
from pathlib import Path
import subprocess
import sys
import venv
import platform

ROOT = Path(__file__).resolve().parent


def main():
    if sys.version_info[:2] != (3, 12):
        raise SystemExit('This self-contained release requires Python 3.12.')
    if sys.platform != 'linux' or platform.machine() != 'x86_64':
        raise SystemExit('This self-contained release is validated on Linux x86_64 only.')
    os.chdir(ROOT)
    subprocess.run([sys.executable, 'download_assets.py'], check=True)
    target = ROOT / '.venv'
    python = target / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    if not python.exists():
        venv.EnvBuilder(with_pip=True).create(target)
    command = [str(python), '-m', 'pip', 'install']
    command += ['-c', 'requirements-linux-py312.txt']
    print('Installing pinned dependencies from the configured Python package index.', flush=True)
    subprocess.run(command + ['-r', 'requirements.txt'], check=True)
    subprocess.run([str(python), 'scripts/prepare_data.py'], check=True)
    print(f'Ready. Run: {python} run.py --help')


if __name__ == '__main__':
    main()
