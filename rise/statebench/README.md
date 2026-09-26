# RISE on StateBench

This directory contains the paper-aligned StateBench implementation of RISE,
the Vanilla baseline, and the modified official OAgents ORM Best-of-4
baseline. It includes the StateBench tasks, environments, prompts, scoring
code, and the bundled ORM prompt. No separate StateBench or OAgents checkout
is required.

Python 3.12, an OpenAI-compatible Chat Completions endpoint, and an API key
are required for live inference. No GPU or key is bundled. Keep credentials in
environment variables and keep runtime outputs outside a published release.

## Codex instruction

Read this file and `AGENTS.md`, work only in this directory, and use
`run_experiment.py` as the public entry point. Run the offline tests and a
three-task real-API smoke first. A full Test split has 150 tasks: 50 each for
customer support, shopping assistant, and travel. Do not call a smoke or
partial run a complete benchmark.

## Installation and smoke test

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:OPENAI_API_KEY = "YOUR_API_KEY"

.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe verify_release.py

.\.venv\Scripts\python.exe run_experiment.py `
  --model gpt-4.1 --base-url https://api.openai.com/v1 `
  --seeds 42 --tasks-per-domain 1 --workers 3 `
  --output-dir outputs/smoke
```

Linux/macOS can use the same commands with `python3.12` and `.venv/bin/python`.

## Complete Test comparison

```powershell
.\.venv\Scripts\python.exe run_experiment.py `
  --model gpt-4.1 --base-url https://api.openai.com/v1 `
  --seeds 42 --workers 10 --output-dir outputs/test_one
```

Use `--seeds 42 142 242 342 442` for five complete Test runs and the
`pass^5` statistic. Reusing the same output directory with the same settings
resumes successful work. Use a new directory for a different model, endpoint,
seed set, or scoring configuration.

The run compares three methods with the same tasks, model, and scoring setup:

1. `Vanilla`: one complete rollout, also the shared candidate A.
2. `StateTrace-EDS-ECA`: the legacy StateBench name for RISE.
3. `OAgents ORM Best-of-4`: four independent candidates and the bundled
   official list-wise ORM selector.

## Algorithm

```text
A = Vanilla rollout in a fresh environment
incumbent = A; credit = empty
for proposal B', C', D' within the four-rollout budget:
    events = public event view of incumbent
    frontier = public recovery risk + event credit + permitted history
    proposal = fresh complete rollout guided by frontier
    disagreement = public transaction comparison(incumbent, proposal)
    if disagreement is material:
        choose incumbent or proposal from public complete trajectories
        derive source-constrained preserve/avoid structural credit
    otherwise retain incumbent
return incumbent
```

Every proposal runs the original task from a fresh initial environment. The
selector and event-credit construction use public task text, tool schemas,
actions, observations, results, and derived public events only. They never
read evaluator labels, hidden requirements, gold actions, reward, or final
state differences. `FRD` is a retrospective audit label, not an online input.

The runner and core implementation are:

| File | Role |
|---|---|
| `run_experiment.py` | Three-method StateBench entry point and aggregation |
| `run_statetrace_eds_eca_paper.py` | RISE A/B'/C'/D' fresh proposals and pairwise selection |
| `state_trace_eds_ec.py` | Recovery frontier, event credit, and selector protocol |
| `state_trace_event_scaling.py` | Public event analysis and disagreement predicates |
| `run_oagents_best_of4.py` | Independent candidates and ORM selection |
| `third_party/OAgents/ORM_list_wise.yaml` | Bundled comparison prompt |
| `aggregate_metrics.py` | pass@1, pass^5, UX, and seed aggregation |

## Metrics

- `Task Completion pass@1`: mean completion over final selected trajectories.
- `pass^5`: fraction of the 150 task keys that pass in all five independent
  complete runs. It is not an oracle over Best-of-4 candidates.
- `UX`: mean official StateBench UX score on the same final trajectories.

The output directory contains `comparison.md`, `comparison.json`, and one
metrics file per method. A single run reports `pass^5 = N/A`; missing tasks or
API errors remain incomplete and are not silently converted to zeros.

## Model compatibility

The client accepts an OpenAI-compatible base URL ending at `/v1`. The model
must support Chat Completions, tool calls, and the request context length. The
actual model ID is required; the word ChatGPT alone is not an API model ID.
Some providers require explicit environment options for seed, temperature, or
the completion-token parameter. See `.env.example` and the client modules.

## Release boundary

Do not commit `.env`, API keys, output directories, logs, virtual environments,
or private endpoints. The release has a fresh Git history and no author
metadata; the URL of a public hosting account remains visible at the hosting
level.
