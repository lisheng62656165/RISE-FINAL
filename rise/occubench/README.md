# RISE on OccuBench

This folder is a self-contained OccuBench release for the 382-task benchmark.
The historical implementation label `StateBench-EDS-ECA` denotes the paper's
RISE adapter; it is not a separate method.
It contains the benchmark data, Language World Model environment, verifier,
the StateBench EDS-ECA adapter, and the OAgents list-wise Best-of-4 adapter.
All benchmark-specific files are inside this folder.

## Experiment protocol

The default configuration covers all 382 tasks. Command-line options override
its model, seeds, limits, and concurrency. It runs RISE, OAgents Best-of-4, and
the shared Vanilla anchor, then generates overall and category metrics under
the selected output directory. No precomputed scores or historical run IDs are
stored in this source release.

Recompute the category table from a completed run with:

~~~bash
python aggregate_occubench_metrics.py --data-root data --scores-dir results/run/scores --out results/run/scores/category_metrics.json
~~~

## Codex Run Instructions

In Codex, open this folder (or reference this README) and ask it to execute the
experiment. Merely referencing a README does not install Python, configure API
credentials, or launch a run. Suggested instruction:

> Work only inside this OccuBench folder. Read README.md and follow its setup
> and run instructions. The complete 382-task dataset is already in data/;
> do not download another benchmark. Ask me for the API model ID, base URL,
> and key if not configured. Keep the key in an environment variable, never
> print it, and never write it to the repository. First run tests and CLI help,
> then run run_full_comparison.py for StateBench-EDS-ECA Original,
> OAgents Best-of-4, and Vanilla on the same 382 tasks. Use
> configs/default_experiment.json unless I provide model or seed overrides. Resume the same output
> directory after interruption. Keep invalid verifier/API responses pending,
> not failures. Report overall and category metrics, including valid-label
> counts, only after scoring.

The model is not bundled. A user must provide a model endpoint and API key.
A compatible Python interpreter must already be installed because an
application folder cannot include the interpreter. No benchmark or world-model
download is needed; pinned Python dependencies are installed from the
configured package index. A ChatGPT web subscription alone is
not an API credential: use a model ID enabled for API access, its API endpoint,
and a valid API key. The provider must support OpenAI-compatible Chat
Completions, tool/function calls, and the structured responses used by this
runner; compatibility is not guaranteed for every endpoint. Other compatible
providers can be used by supplying their model ID and `/v1` base URL.

## Setup

The included data and source code are sufficient; no dataset download is
needed. Install the pinned dependencies with:

~~~bash
python3.12 bootstrap.py
source .venv/bin/activate
~~~

On Windows PowerShell:

~~~powershell
py -3.12 bootstrap.py
.\.venv\Scripts\Activate.ps1
~~~

For another platform or Python version, use Python 3.10+ and install
`requirements.txt` with pip.

## Full 382-Task Run

Set the endpoint and key through environment variables:

~~~bash
export OPENAI_BASE_URL="https://api.openai.com/v1"
export OPENAI_API_KEY="REDACTED"
~~~

Then run:

~~~bash
python run_full_comparison.py \
  --config configs/default_experiment.json \
  --base-url "$OPENAI_BASE_URL" \
  --api-key-env OPENAI_API_KEY \
  --seed 53403 \
  --selector-seed 77113 \
  --oagents-selector-seed 53403 \
  --workers 8 \
  --selector-workers 8 \
  --max-tokens 16384 \
  --limit 382
~~~

On Windows PowerShell, set the same variables and run:

~~~powershell
$env:OPENAI_BASE_URL = "https://api.openai.com/v1"
$env:OPENAI_API_KEY = "REDACTED"
python run_full_comparison.py --config configs/default_experiment.json --base-url $env:OPENAI_BASE_URL `
  --api-key-env OPENAI_API_KEY --seed 53403 --selector-seed 77113 `
  --oagents-selector-seed 53403 `
  --workers 8 --selector-workers 8 --max-tokens 16384 --limit 382
~~~

Set OPENAI_BASE_URL to a provider serving the configured model; the example
OpenAI URL above requires an OpenAI model override such as `--model gpt-4o`.
To use another seed, explicitly set the seeds you want to change, for example:

~~~bash
python run_full_comparison.py --model YOUR_MODEL --base-url "$OPENAI_BASE_URL" --seed 42 --selector-seed 42 --oagents-selector-seed 42 --output results/seed42
~~~

The endpoint must support the request fields used by the selected model. For a local vLLM server,
use its /v1 URL and the corresponding model name. The runner stores only
redacted configuration metadata.

The run creates results/run/ with eds_eca, oagents_bon4, and
scores subdirectories. The score directory contains scores.jsonl,
vanilla_scores.jsonl, category_metrics.json/.md, and overall_results.json/.md.
The overall report records per-method valid-label counts and remains marked
pending until all three methods have valid labels for the requested cohort;
invalid verifier responses are never converted to failures.

The default seeds are `53403` for cohort/Python sampling, `77113` for the
EDS-ECA selector base, and fixed `53403` for each OAgents selector API call.
`--selector-seed` changes only EDS-ECA; `--oagents-selector-seed` changes only
OAgents. Agent generation does not explicitly send an API seed or temperature;
it inherits provider defaults.
The run is resumable: EDS-ECA uses stage checkpoints and resume, while the
Best-of-4 runner skips task directories that already have result.json. Never
mix output directories from different models, endpoints, or sampling
configurations.

## Algorithm Definitions

### StateBench-EDS-ECA Original

The first trajectory A is generated as a fresh Vanilla rollout. Each later
stage generates a fresh proposal in a fresh environment. The public trace is
converted into StateBench event records; the selector compares the accepted
incumbent and proposal using only public task text, actions, observations, and
responses. It returns an event-credit decision and the accepted incumbent is
carried forward to guide the next stage. Verifier labels, reward, gold state,
and is_correct are not selector inputs. The final output is the accepted
incumbent after A/B/C/D.

### OAgents Best-of-4

The method reuses the same stage-A anchor and generates three fresh,
independent proposals. An OAgents ORM list-wise selector sees the visible task
instruction and the four public trajectories and selects exactly one
candidate. It does not receive verifier labels, reward, hidden state, or EDS
event credit. The selector prompt is vendored at
vendor/oagents/ORM_list_wise.yaml.

Vanilla in the comparison is the exact same A trajectory used as the
EDS-ECA anchor and one of the four Best-of-4 candidates. A and the accepted
EDS-ECA FINAL are scored together by the paired verifier; Best-of-4's selected
trajectory is scored with that same verifier configuration.

## Public-Information Boundary

Selector packets contain only the visible agent instruction, public agent
actions, public environment observations, and public agent responses.
They do not contain verification_plan, is_correct, verifier feedback, reward,
gold state, candidate source names, or hidden evaluator metadata.
The LWM may expose information through its public observations because that is
the benchmark environment interface; this is not silently replaced with
verifier information.

## Project Layout

~~~text
data/                         # bundled 382-task OccuBench data
occubench/                    # LWM, agent loop, verifier, evaluation CLI
vendor/statebench/            # StateBench event/EDS-ECA core
vendor/oagents/               # OAgents list-wise selector prompt
run_occubench_eds_eca_mimo.py # StateBench EDS-ECA adapter
run_occubench_bestof4.py      # OAgents Best-of-4 adapter
run_full_comparison.py        # complete 382-task entry point
score_bestof4.py              # deferred Best-of-4 verifier scoring
aggregate_occubench_metrics.py# ten-category aggregation
~~~

## Tests and Smoke Checks

Run the unit tests before a live batch:

~~~bash
python -m pytest -q tests
~~~

To inspect all available CLI arguments without calling a model:

~~~bash
python run_occubench_eds_eca_mimo.py --help
python run_occubench_bestof4.py --help
python run_full_comparison.py --help
~~~

## Citation

~~~bibtex
@article{hu2026occubench,
  title={OccuBench: Evaluating AI Agents on Real-World Professional Tasks via Language World Models},
  author={Xiaomeng Hu and Yinger Zhang and Fei Huang and Jianhong Tu and Yang Su and Lianghao Deng and Yuxuan Liu and Yantao Liu and Dayiheng Liu and Tsung-Yi Ho},
  journal={arXiv preprint arXiv:2604.10866},
  year={2026}
}
~~~

## Licenses

OccuBench files retain the included OccuBench Apache-2.0 license.
StateBench-derived modules and OAgents materials retain their respective
license files under vendor/statebench/ and vendor/oagents/.
