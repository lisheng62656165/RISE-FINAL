# RISE on DeepPlanning

This directory contains the RISE adapter, independent Best-of-4 selector,
official Travel evaluator, and the upstream Travel/Shopping agent code needed
to execute DeepPlanning. The manuscript evaluation uses Travel: 120 Chinese
tasks and the same 120 tasks in English. Shopping is retained as an auxiliary
execution adapter and is not folded into the Travel table.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe download_assets.py
$env:DEEPPLANNING_API_KEY = "YOUR_API_KEY"
$env:DEEPPLANNING_BASE_URL = "https://your-provider.example/v1"
$env:DEEPPLANNING_MODEL = "YOUR_MODEL_CONFIG_NAME"
.\.venv\Scripts\python.exe verify_release.py
```

`DEEPPLANNING_MODEL` names an entry in `models_config.json`. The same model,
endpoint, and key are used by proposal agents and selectors. The older
`DEEPPLANNING_OPENAI_BASE_URL` and provider-specific key named by a model entry
remain compatibility fallbacks; new runs should use the variables above.

## RISE algorithm

`run_deepplanning_eds_eca.py` starts from an independently generated Vanilla
anchor. For each of three rounds it builds a public structural frontier, runs
a complete proposal in a fresh environment, checks material disagreement, and
optionally selects and credits the pair. A malformed selector response retains
the incumbent. Preserve and avoid IDs are source-checked before projection;
only event shapes enter the next round. Literal arguments, result bodies, and
selector rationale are not replayed.

Generate the Chinese and English Vanilla Travel anchors:

```powershell
$py = ".\.venv\Scripts\python.exe"
& $py run_deepplanning_travel_inference_only.py --travel-root .\travelplanning `
  --model $env:DEEPPLANNING_MODEL --language zh --workers 20 `
  --max-llm-calls 400 --seed 53403 --output-root .\travel_runs\vanilla
& $py run_deepplanning_travel_inference_only.py --travel-root .\travelplanning `
  --model $env:DEEPPLANNING_MODEL --language en --workers 20 `
  --max-llm-calls 400 --seed 53403 --output-root .\travel_runs\vanilla
```

Run RISE on each language. The model slug defaults to a filesystem-safe form
of `--model`; pass `--anchor-model-slug` only when the anchor directory uses a
different slug.

```powershell
& $py run_deepplanning_eds_eca.py --root . --output .\results\rise `
  --cohort travel-zh --model $env:DEEPPLANNING_MODEL --anchor-tag vanilla `
  --workers 20 --proposal-seed 64639 --selector-seed 77113
& $py run_deepplanning_eds_eca.py --root . --output .\results\rise `
  --cohort travel-en --model $env:DEEPPLANNING_MODEL --anchor-tag vanilla `
  --workers 20 --proposal-seed 64639 --selector-seed 77113
```

The optional `--deepplanning-adapter` adds schema-derived public plan signals.
It is an explicit variant and is not silently enabled by the default command.

## Best-of-4

Generate four independent complete candidate sets with the same model and
rollout limits. Each invocation writes to
`<candidate-root>/<model-config>_<language>/trajectories/`. For example:

```powershell
$candidateSeeds = 53403, 64639, 64640, 64641
for ($i = 0; $i -lt $candidateSeeds.Count; $i++) {
  & $py run_deepplanning_travel_inference_only.py --travel-root .\travelplanning `
    --model $env:DEEPPLANNING_MODEL --language zh --workers 20 `
    --max-llm-calls 400 --seed $candidateSeeds[$i] --output-root ".\cand_$i"
  & $py run_deepplanning_travel_inference_only.py --travel-root .\travelplanning `
    --model $env:DEEPPLANNING_MODEL --language en --workers 20 `
    --max-llm-calls 400 --seed $candidateSeeds[$i] --output-root ".\cand_$i"
}
```

The resulting layout is:

```text
cand_0/<model-config>_zh/trajectories/id_0.json ... id_119.json
cand_0/<model-config>_en/trajectories/id_0.json ... id_119.json
...
cand_3/<model-config>_en/trajectories/id_0.json ... id_119.json
```

Then select one complete trajectory per task using only public trajectory
information:

```powershell
& $py select_best_of_4_deepplanning.py --root . --output-root .\results\best_of_n `
  --candidate-root .\cand_0 --candidate-root .\cand_1 `
  --candidate-root .\cand_2 --candidate-root .\cand_3 `
  --cohort travel-zh --model $env:DEEPPLANNING_MODEL --workers 20
```

Repeat with `--cohort travel-en`. The selector requires exactly four candidate
roots and resolves `<model-config>` from `--model`; it does not assume a
provider-specific directory name.

## Official evaluation and table export

Run conversion and the official evaluator for every method and language using
the included scripts. Place the resulting summaries at:

```text
results/<method>/travel_zh/evaluation_summary.json
results/<method>/travel_en/evaluation_summary.json
```

Use method directory names `vanilla`, `best_of_n`, and `rise`, then export the
paper-shaped table:

```powershell
& $py report_metrics.py --results .\results --output .\results\metrics.json `
  --csv .\results\metrics.csv
```

The reporter emits Delivery, Commonsense, Personalized, and Composite for
Chinese and English separately. It checks the explicit IDs of the complete
120-task cohort, delivered-plan IDs, evaluation-result IDs, counters, and the
Delivery denominator before writing output. Generated reports are run outputs
and should not be committed.

## Information boundary

Online proposal and selection use the task, public tool calls/results, final
answer, and structural event credit. Evaluator scores, hidden constraints,
gold plans, rewards, and retrospective FRD labels are scoring-only data.
