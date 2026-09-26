# RISE: Recovery-Informed Scaling via Events

This is the anonymous reproducibility release for the paper
**RISE: Recovery-Informed Scaling via Events for Tool-Using Language Models**.
RISE is a bounded test-time search over complete tool-agent executions. It
uses public event evidence to guide a fresh proposal, compares the accepted
trajectory with that proposal, and keeps an accepted trajectory as the search
state.

The repository is self-contained at the benchmark level: task data,
environment code, scoring code, prompts, and the released offline wheels are
stored in the corresponding benchmark directory. A Python interpreter and a
model API key are still required. No API key, private endpoint, server path,
experiment output, or author metadata is included.

## Method

For a task `x`, RISE runs the following bounded loop. Every rollout starts in
a fresh environment.

```text
I <- Vanilla rollout; C <- empty event credit
repeat for the remaining rollout budget:
    V <- public event view of the accepted trajectory I
    F <- recovery frontier from public risk, credit, and permitted history
    P <- fresh complete proposal rollout guided by F
    D <- material public disagreement between I and P
    if D is material:
        select I or P from their public complete trajectories
        derive source-constrained preserve/avoid event credit
    otherwise retain I
return the accepted trajectory I
```

`FRD` (Failed Recovery Decision) is a retrospective audit label. The online
pipeline uses only public recovery-risk evidence; it never gives evaluator
labels, hidden requirements, gold actions, rewards, or final state diffs to the
agent, selector, or event-credit construction.

The implementation names below are historical names of benchmark adapters,
not separate algorithms:

| Paper name | Release entry point | Historical implementation label |
|---|---|---|
| RISE | `rise/statebench/` | StateTrace-EDS-ECA |
| RISE AppWorld adapter | `appworld/` | Faithful v3 / StateTrace-EDS-ECA |
| RISE OccuBench adapter | `rise/occubench/` | StateBench-EDS-ECA |
| RISE DeepPlanning adapter | `deepplanning/` | `statetrace_dsr` |

## Repository layout

```text
RISE-FINAL/
  rise/statebench/       StateBench, RISE, Vanilla, and official ORM Best-of-4
  rise/occubench/        OccuBench adapter, evaluator, and aggregation
  appworld/              AppWorld RISE adapter and Test-N/Test-C runner
  deepplanning/          DeepPlanning Travel and Shopping adapters
  PAPER_ALIGNMENT.md     Paper sections, terminology, and code map
```

## Quick start

All live runs require an OpenAI-compatible Chat Completions endpoint. A
ChatGPT web subscription is not an API credential. Keep credentials in
environment variables or in a file outside the repository.

### StateBench

```powershell
cd rise/statebench
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:OPENAI_API_KEY = "YOUR_API_KEY"

# Offline checks first.
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe verify_release.py

# Three-task smoke run.
.\.venv\Scripts\python.exe run_experiment.py `
  --model gpt-4.1 --base-url https://api.openai.com/v1 `
  --seeds 42 --tasks-per-domain 1 --workers 3 `
  --output-dir outputs/smoke

# Full 150-task Test comparison.
.\.venv\Scripts\python.exe run_experiment.py `
  --model gpt-4.1 --base-url https://api.openai.com/v1 `
  --seeds 42 --workers 10 --output-dir outputs/test_one
```

Use five seeds (`42 142 242 342 442`) when `pass^5` is required. The runner
compares Vanilla, RISE/StateTrace-EDS-ECA, and the modified official ORM
Best-of-4 under the same model and scoring configuration.

### AppWorld

```bash
cd appworld
python3.12 bootstrap.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/smoke_environment.py

export OPENAI_API_KEY='YOUR_API_KEY'
export OPENAI_BASE_URL='https://api.openai.com/v1'
export MODEL_NAME='gpt-4.1'

# Both official test splits, both methods, shared Vanilla candidate A.
.venv/bin/python run.py \
  --config configs/appworld_main.json \
  --method both --workers 4 \
  --output outputs/full-comparison

.venv/bin/python summarize.py --output outputs/full-comparison
```

The command covers Test-N (`test_normal`, 168 tasks and 56 scenarios) and
Test-C (`test_challenge`, 417 tasks and 139 scenarios). The two splits use the
same model, endpoint, rollout budget, selector budget, method definitions, and
seed protocol; only the official task/scenario list differs. It reports:
`Test-N TGC`, `Test-N SGC`, `Test-C TGC`, and `Test-C SGC` for Vanilla, the
RISE AppWorld adapter, and OAgents parallel Best-of-4.

### OccuBench

```powershell
cd rise/occubench
py -3.12 bootstrap.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe run_full_comparison.py `
  --config configs/main_results.json `
  --base-url $env:OPENAI_BASE_URL --api-key-env OPENAI_API_KEY `
  --workers 8 --selector-workers 8 --limit 382
```

The complete comparison is Vanilla, OAgents Best-of-4, and the RISE adapter;
official verifier labels are used only after generation for scoring.

### DeepPlanning

```powershell
cd deepplanning
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:DEEPSEEK_API_KEY = "YOUR_API_KEY"
$env:DEEPPLANNING_OPENAI_BASE_URL = "https://api.deepseek.com/v1"
.\.venv\Scripts\python.exe verify_release.py
```

Use `run_deepplanning_shopping_subset.py` for Shopping levels 1/2/3,
`run_deepplanning_travel_inference_only.py` for Travel, and then
`run_deepplanning_eds_eca.py` or `select_best_of_4_deepplanning.py` for the
corresponding RISE and Best-of-4 paths. The detailed argument layouts and
metric command are in [`deepplanning/README.md`](deepplanning/README.md).

## Accounting and comparison rules

- Vanilla uses one complete rollout.
- Best-of-4 uses four independent complete rollouts and one list-wise selector.
- RISE uses one initial rollout and at most three guided complete proposals.
- The rollout budget is matched; token cost and latency are reported
  separately and are not assumed identical.
- Failed API calls and missing outputs remain incomplete; they are not scored
  as algorithm failures or successes.
- Test labels are never used to tune prompts, event rules, selectors, or
  credit construction.

## Anonymity

This release has a fresh Git history and contains no author names, email
addresses, personal filesystem paths, private server addresses, API keys, or
runtime logs. The hosting account and URL of a public GitHub repository are
controlled by the account used to publish it and therefore cannot be made
account-anonymous by repository contents alone.

See [`PAPER_ALIGNMENT.md`](PAPER_ALIGNMENT.md) for the paper-to-code map,
historical naming policy, data boundaries, and result tables.
