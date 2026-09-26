# Downloaded assets

- `data-0.1.0.bundle`: official encrypted AppWorld dataset.
- `appworld-0.1.3.post1-py3-none-any.whl`: official PyPI wheel containing the
  encrypted apps bundle.

`python download_assets.py` retrieves both files from their official public
sources and verifies the byte count and SHA-256 recorded in `manifest.json`.
They are intentionally ignored by Git. Dependency versions remain pinned in
`../requirements-linux-py312.txt` and are installed from the configured Python
package index by `bootstrap.py`.

The bootstrap is validated on Linux x86_64 / CPython 3.12. Python, package
index access, asset-host access, and model API access are not bundled. The
extracted protected data is local-only; see `../NOTICE.md`.
