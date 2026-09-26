# RISE on DeepPlanning

This directory contains the DeepPlanning Travel and Shopping adapter used in
the paper. Official evaluators, agent code, the RISE implementation, and the
Best-of-4 selector are included. Large local tool databases are downloaded
from the official `Qwen/DeepPlanning` release by `download_assets.py`. The
legacy output key `statetrace_dsr` is retained by the evaluator for script
compatibility; it refers to this RISE adapter, not to a separate paper method.

The packaged cohort is test-only: Shopping has 120 cases across levels 1/2/3
and Travel has 120 Chinese plus 120 English cases. No train/dev split is
created in this release.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe download_assets.py
$env:DEEPSEEK_API_KEY = "YOUR_API_KEY"
$env:DEEPPLANNING_OPENAI_BASE_URL = "https://api.deepseek.com/v1"
.\.venv\Scripts\python.exe verify_release.py
```

Use any OpenAI-compatible model by setting the model and endpoint options used
by the runner. Never commit a key. The downloader retrieves five pinned
official archives (about 100 MiB compressed), verifies their sizes and
SHA-256 values, and installs the complete 120 Shopping and 120+120 Travel
cohorts. Re-running it skips complete assets.

## Methods

| Method | Definition |
|---|---|
| `vanilla` | One independent complete agent rollout |
| `oagents_best4` | Four independent rollouts followed by public list-wise selection |
| `statetrace_dsr` | RISE: public recovery frontier, fresh proposals, selection, and event credit |

RISE maintains an accepted trajectory, compiles public tool events into a
frontier, runs a fresh proposal, gates selection on material public
disagreement, and carries source-constrained preserve/avoid credit to later
proposals. Evaluator output, hidden requirements, reward, and gold actions are
not online inputs.

## Vanilla generation

The following commands cover the complete Shopping and Travel cohorts. Change
the run names only when starting a new model or seed; outputs are resumable.

```powershell
$py = ".\.venv\Scripts\python.exe"

& $py run_deepplanning_shopping_subset.py --shopping-root .\shoppingplanning --model deepseek-v4.1-flash --level 1 --case-ids (1..50) --run-name vanilla_L1 --workers 20 --max-llm-calls 400 --trial 1 --orchestration-seed 53403 --allow-inference-failures
& $py run_deepplanning_shopping_subset.py --shopping-root .\shoppingplanning --model deepseek-v4.1-flash --level 2 --case-ids (1..50) --run-name vanilla_L2 --workers 20 --max-llm-calls 400 --trial 1 --orchestration-seed 53403 --allow-inference-failures
& $py run_deepplanning_shopping_subset.py --shopping-root .\shoppingplanning --model deepseek-v4.1-flash --level 3 --case-ids (1..20) --run-name vanilla_L3 --workers 10 --max-llm-calls 400 --trial 1 --orchestration-seed 53403 --allow-inference-failures
& $py run_deepplanning_travel_inference_only.py --travel-root .\travelplanning --model deepseek-v4.1-flash --language zh --workers 20 --max-llm-calls 400 --seed 53403 --output-root .\travel_runs\vanilla
& $py run_deepplanning_travel_inference_only.py --travel-root .\travelplanning --model deepseek-v4.1-flash --language en --workers 20 --max-llm-calls 400 --seed 53403 --output-root .\travel_runs\vanilla
```

## RISE and Best-of-4

Run the RISE adapter after its matching Vanilla anchor exists:

```powershell
& $py run_deepplanning_eds_eca.py --help
```

Use the script's `--anchor-model-slug`, `--deepplanning-adapter`, output-root,
and cohort options to point at the matching Vanilla artifacts. The exact
options are intentionally exposed by `--help` because the Travel and Shopping
cohorts have different artifact layouts. The runner must use a fresh
environment for every proposal and the same model/seed budget as the paired
baseline.

Generate four independent candidates for the comparison baseline, then run
the bundled public selector:

```powershell
& $py select_best_of_4_deepplanning.py --help
& $py select_best_of_4_deepplanning.py --root . --cohort travel-zh --workers 20
& $py select_best_of_4_deepplanning.py --root . --cohort travel-en --workers 20
& $py select_best_of_4_deepplanning.py --root . --cohort shopping --workers 20
```

Best-of-4 receives only public task and trajectory information. It does not
receive evaluator labels or RISE event credit.

## Official evaluation and metrics

Place official summaries in this layout:

```text
results/<method>/shopping/**/summary_report.json
results/<method>/travel_zh/evaluation_summary.json
results/<method>/travel_en/evaluation_summary.json
```

Use method directories `vanilla`, `oagents_best4`, and `statetrace_dsr`, then
run:

```powershell
& $py report_metrics.py --results .\results --output .\results\metrics.json `
  --csv .\results\metrics.csv --plot .\results\deepplanning_metrics.png
```

The report contains Travel Delivery, Commonsense, Personalized, Composite,
and case accuracy, plus Shopping match and case accuracy. It fails when a
method or cohort is missing, so incomplete runs cannot be reported as a full
comparison.

## Privacy and reproducibility

Keep outputs, logs, credentials, and local environment files outside a public
commit. Record the model ID, endpoint family, seed, candidate count, selector
seed, worker count, and valid-label counts. API failures are transport
failures, not task failures. This release has a fresh anonymous Git history;
the publisher account of any public GitHub URL remains visible at the hosting
level.
