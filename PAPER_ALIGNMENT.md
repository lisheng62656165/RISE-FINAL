# Paper Alignment and Release Notes

This document maps the anonymous code release to the paper terminology. It is
deliberately free of author, institution, machine, and credential metadata.

## Terminology map

The paper presents one method, RISE. The repository predates the final paper
name in several directories, so filenames retain compatibility names:

| Paper term | Code location | Meaning |
|---|---|---|
| accepted trajectory | StateBench `run_statetrace_eds_eca_paper.py`; analogous adapter runners | Current search state, initially Vanilla |
| public event view | `state_trace_event_scaling.py`, adapter event modules | Structured calls, results, failures, and public evidence |
| recovery frontier | `state_trace_eds_ec.py` and benchmark adapters | Public recheck guidance for the next fresh rollout |
| material disagreement | `compare_public_trajectories` and adapter predicates | Gate before pairwise selection |
| bilateral event credit | `state_trace_eds_ec.py` and adapter credit modules | Source-checked preserve/avoid structural feedback |
| RISE | unified algorithm | Final paper name |
| StateTrace-EDS-ECA | legacy StateBench/AppWorld label | RISE-compatible implementation label |
| Faithful v3 | legacy AppWorld label | RISE AppWorld adapter release label |

The legacy names are retained in CLI arguments, output directories, and JSON
schemas to preserve existing scripts. They do not denote extra algorithms.

## Public-information boundary

Online generation and selection may read only the task instruction, public
tool schemas, public actions, public observations, public results, and the
adapter's derived event representation. They must not read:

- evaluator labels or verifier output;
- hidden requirements, gold actions, or final-state diffs;
- reward, task success, or scenario success;
- a task's outcome from another method or another split.

The evaluator is invoked after a complete trajectory is produced. FRD is a
retrospective audit label and is not an input to generation, selection, or
credit construction.

## Benchmark adapters

### StateBench

`rise/statebench/run_statetrace_eds_eca_paper.py` starts from a Vanilla anchor,
generates up to three fresh proposals, performs pairwise selection only for a
material public transaction disagreement, and carries structural event credit
to later proposals. `run_oagents_best_of4.py` is the comparison baseline and
uses the bundled ORM list-wise prompt.

### AppWorld

`appworld/run.py` is the public driver. The `faithful-v3` method is the legacy
name for the AppWorld RISE adapter. `--method both` runs Faithful/RISE and the
modified official OAgents parallel Best-of-4 with shared Vanilla candidate A.
`test_normal` and `test_challenge` use the same basic configuration.

### OccuBench

`rise/occubench/run_full_comparison.py` runs the three-way comparison on the
bundled 382-task cohort. Its adapter maps public action-observation traces into
the same event-and-frontier abstraction while retaining benchmark-specific
credit validation.

### DeepPlanning

`deepplanning/run_deepplanning_eds_eca.py` and the travel/shopping adapters
implement the same bounded search idea for travel planning and shopping. The
legacy output key `statetrace_dsr` is retained for compatibility with the
existing evaluator and report scripts.

## Reference results from the manuscript

These are paper reference values, not a claim that a new API run will be
bit-for-bit identical. The primary tables are reproduced here so a release
user can compare the correct columns and model settings.

### StateBench

| Method | DeepSeek pass@1 | DeepSeek pass^5 | DeepSeek UX | Qwen pass@1 | Qwen pass^5 | Qwen UX | GPT pass@1 | GPT pass^5 | GPT UX |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Vanilla | 65.20 | 38.67 | 3.9709 | 69.33 | 41.33 | 4.0217 | 71.33 | 42.00 | 4.0658 |
| Best-of-N | 72.13 | 46.67 | 4.1428 | 76.00 | 49.33 | 4.1893 | 78.00 | 50.67 | 4.2374 |
| RISE | 72.67 | 48.67 | 4.1499 | 81.33 | 54.67 | 4.3512 | 82.67 | 56.67 | 4.3981 |

### OccuBench

| Method | DeepSeek | Qwen | GPT |
|---|---:|---:|---:|
| Vanilla | 49.74 | 57.85 | 59.69 |
| Best-of-N | 61.78 | 68.85 | 70.68 |
| RISE | 63.35 | 74.35 | 76.96 |

### AppWorld

| Model | Split | Vanilla TGC | Vanilla SGC | Best-of-N TGC | Best-of-N SGC | RISE TGC | RISE SGC |
|---|---|---:|---:|---:|---:|---:|---:|
| DeepSeek-v4.1-Flash | Test-N | 91.07 | 80.36 | 91.07 | 82.14 | 92.26 | 85.71 |
| DeepSeek-v4.1-Flash | Test-C | 87.77 | 75.54 | 88.01 | 77.70 | 89.69 | 82.01 |
| Qwen3.8-Max | Test-N | 91.07 | 82.14 | 92.26 | 83.93 | 96.43 | 89.29 |
| Qwen3.8-Max | Test-C | 89.93 | 79.14 | 90.41 | 81.29 | 94.72 | 88.49 |
| GPT-5.6-Sol | Test-N | 92.26 | 83.93 | 93.45 | 85.71 | 97.62 | 92.86 |
| GPT-5.6-Sol | Test-C | 90.65 | 80.58 | 91.13 | 82.73 | 95.68 | 91.37 |

### Historical AppWorld Test-C reference configuration

The following user-supplied full-coverage table is retained as a historical
reference for the shared basic configuration. It is separate from the
manuscript's multi-model table above.

| Method | TGC | SGC |
|---|---:|---:|
| Vanilla | 366/417 = 87.8% | 105/139 = 75.5% |
| OAgents Best-of-4 | 367/417 = 88.0% | 108/139 = 77.7% |
| Faithful v3 | 374/417 = 89.7% | 114/139 = 82.0% |

## Reproducibility scope

The included tests validate imports, local environments, public payload
boundaries, scoring, and checkpoint behavior without making paid API calls.
They do not prove that a new model endpoint reproduces the paper point
estimates. For a live run, record the model ID, endpoint family, seeds, worker
count, completion counts, API failures, and the exact output directory.
