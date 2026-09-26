# Double-blind code audit

The public repository is a development and archival surface. Its hosting URL
identifies the publishing account, so it must not be cited or submitted during
double-blind review. Use the clean archive described in `SUPPLEMENTARY.md`.

## Automated checks

Run from the repository root:

```powershell
python tools/audit_anonymity.py
python tools/build_anonymous_supplement.py `
  --output ..\RISE-anonymous-supplementary.zip
python tools/audit_anonymity.py `
  --archive ..\RISE-anonymous-supplementary.zip
```

The audit uses Git-tracked files for the repository scan and zip members for
the archive scan. It rejects:

- the current Git remote URL or publishing account;
- the current OS user and home-directory paths;
- common Windows, Linux, and macOS home-directory paths outside known benchmark
  fixtures;
- likely OpenAI, NVIDIA, GitHub, Hugging Face, and AWS secret formats;
- `.git`, `.github`, credential files, logs, run outputs, downloaded databases,
  wheels, and protected extracted AppWorld data in the supplementary archive.

Email-shaped strings are reported separately rather than rejected. The bundled
STATE-Bench task fixtures contain synthetic user email addresses, and upstream
license/provenance files may name third-party authors. Removing or rewriting
those values would modify benchmark inputs or erase required attribution; they
are not author-identity evidence.

OccuBench also contains a generic virtual home path inside one simulated
debugging task. The audit reports home paths inside `rise/occubench/data/` as
benchmark fixtures, while the same pattern anywhere else remains a failure.

Passing this scan means no configured machine-detectable author identity or
credential pattern was found. It cannot prove anonymity against inference from
writing style, research topic, or prior public artifacts.
