# RISE AppWorld Adapter

This directory is the self-contained AppWorld release for the paper's RISE
method. The historical public label for this adapter is **Faithful v3**; the
algorithm is the same RISE pipeline described in the root README. The package
also includes the comparison baselines Vanilla and the modified official
OAgents parallel Best-of-4.

The AppWorld bundle, wheel, dependency wheels, runner, selector, evaluator,
and tests are included here. You need Python 3.12, an OpenAI-compatible model
endpoint, and your own API key. No API key, private endpoint, server path,
old experiment output, or author metadata is included.

## Codex run instruction

Read this file and `AGENTS.md`, then work only in this directory. Use the
bundled data and wheel; do not clone another project or download another
dataset. Run the offline checks and a one-task smoke run before the full
comparison. Use a fresh output directory, resume the same directory after an
interruption, and run `summarize.py` after scoring. A partial run is not a
complete benchmark.

## Setup

The validated target is Linux/WSL2 x86_64 with Python 3.12. The bootstrap
script installs the included AppWorld wheel and Linux wheels into `.venv`.

```bash
python3.12 bootstrap.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/smoke_environment.py
```

The package can also use an existing Python 3.12 environment with
`requirements.txt`; the bundled wheel and data remain the preferred
reproducible path.

## Model configuration

```bash
export OPENAI_API_KEY='YOUR_API_KEY'
export OPENAI_BASE_URL='https://api.openai.com/v1'
export MODEL_NAME='gpt-4.1'
export MAX_COMPLETION_TOKENS=4096
```

Use a concrete API model ID, not the name of a web subscription. Any provider
must support the OpenAI-compatible Chat Completions interface and the request
features used by the selected model. Do not put a key in a config file or in
the repository.

## Full test run

First run one real task in a separate directory:

```bash
.venv/bin/python run.py \
  --method faithful-v3 --split both --limit 1 --workers 1 \
  --output outputs/smoke
```

Then run both official test splits and both methods:

```bash
.venv/bin/python run.py \
  --config configs/appworld_main.json \
  --method both --workers 4 \
  --output outputs/full-comparison
.venv/bin/python summarize.py --output outputs/full-comparison
```

The command covers:

| Split | Tasks | Scenarios | Report name |
|---|---:|---:|---|
| Test-N / `test_normal` | 168 | 56 | Test-N TGC, Test-N SGC |
| Test-C / `test_challenge` | 417 | 139 | Test-C TGC, Test-C SGC |

Test-N and Test-C use the same basic configuration: model, endpoint, maximum
steps, selector budget, method definitions, candidate seed protocol, and
evaluator. Only the official task/scenario list changes. The configuration is
also usable with a different model or seed by passing explicit CLI options and
writing to a new output directory.

## Methods

### RISE / Faithful v3

```text
A = fresh Vanilla ReAct trajectory
accepted = A
for B, C, D within the four-rollout budget:
    view accepted public API events
    build a recovery frontier and event credit
    run a fresh complete proposal
    if public API signatures materially disagree:
        select accepted or proposal
        derive source-checked preserve/avoid credit
    otherwise keep accepted
return accepted
```

The selector receives public task text and public trajectory evidence only.
Evaluator success, hidden state, gold actions, reward, and scenario labels are
used only after the trajectory finishes for reporting.

### OAgents parallel Best-of-4

The baseline uses four independent complete ReAct candidates, with Vanilla
candidate A shared with the RISE run when `--method both` is used. It then uses
the bundled ORM list-wise selector from `third_party/OAgents/ORM_list_wise.yaml`.
It does not use RISE event credit, recovery frontier, or feedback-conditioned
proposal trajectories. It is an AppWorld adaptation of the official ORM
selection protocol, not a claim of reproducing an unrelated runtime.

### Vanilla

Vanilla is exactly the shared candidate A. Its result is scored with the same
AppWorld evaluator and task list as the other methods.

## Metrics and output

```bash
.venv/bin/python summarize.py --output outputs/full-comparison
```

The summary writes `metrics.md` and `metrics.json` with these four columns:

| Method | Test-N TGC | Test-N SGC | Test-C TGC | Test-C SGC |
|---|---:|---:|---:|---:|
| Vanilla | percentage | percentage | percentage | percentage |
| RISE / Faithful v3 | percentage | percentage | percentage | percentage |
| OAgents parallel Best-of-4 | percentage | percentage | percentage | percentage |
| Faithful v3 - Vanilla | delta | delta | delta | delta |
| OAgents Best-of-4 - Vanilla | delta | delta | delta | delta |

TGC is task goal completion. SGC is scenario goal completion: every task in a
scenario must pass. The summarizer uses only matched completed task artifacts;
missing evaluations never become successes and incomplete scenario groups are
not counted as SGC successes.

## Paper reference: historical Test-C configuration

This is the recorded full-coverage reference table for the shared basic
configuration. It is included for comparison and is not silently recomputed
when a new API run starts.

| Method | TGC | SGC |
|---|---:|---:|
| Vanilla | 366/417 = 87.8% | 105/139 = 75.5% |
| OAgents Best-of-4 | 367/417 = 88.0% | 108/139 = 77.7% |
| Faithful v3 | 374/417 = 89.7% | 114/139 = 82.0% |

## Reproducibility and privacy rules

- Keep API keys in environment variables or outside the repository.
- Do not use evaluator output, hidden requirements, or test labels online.
- Keep each model, seed, and endpoint in a new output directory.
- Resume an interrupted run with the same command and output directory.
- Do not report a partial split as a full official result.
- Do not publish `outputs/`, logs, or private runtime files.

The source release intentionally has a fresh anonymous Git history. A public
GitHub host may still expose the publisher account in the repository URL; that
hosting-level identity cannot be removed by files inside this directory.
