# Anonymous supplementary release

The double-blind supplementary is a clean source export, not the public Git
repository. Do not put the account-identifying public repository URL in the
paper or submission form during review.

Build the archive from the repository root:

```powershell
python tools/build_anonymous_supplement.py `
  --output ..\RISE-anonymous-supplementary.zip
```

The builder excludes Git history, GitHub publishing metadata, downloaded
databases and wheels, caches, virtual environments, credentials, logs, and run
outputs. It retains source, tests, configs, official asset manifests,
downloaders, dependency files, and all benchmark README files. It also refuses
to package source text containing the local home path or the current Git remote.

Before submission:

1. Extract the archive into a new directory.
2. Confirm there is no `.git` or `.github` directory.
3. Follow each benchmark's README from that extracted directory.
4. Run unit and smoke tests; do not treat a static preflight as execution
   evidence.
5. Upload the zip to the supplementary-material field, or upload the extracted
   clean tree to an anonymous code-hosting service.

Run `python tools/audit_anonymity.py --archive <archive.zip>` before upload.
The expected result is no configured identity, home-path, or credential
patterns; email-shaped benchmark fixtures are reported separately.

Large assets are obtained after extraction from official sources:

- DeepPlanning databases: `python deepplanning/download_assets.py`
- AppWorld encrypted bundle and package: `python appworld/download_assets.py`

The SHA-256 checks in the manifests protect the formal release against a
truncated download or silent upstream replacement. They do not assert that
experimental outputs are bit-identical across model providers.
