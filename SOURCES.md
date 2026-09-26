# Sources and provenance

This file records the external code, prompts, benchmarks, and binary assets
used by the release. Project-specific RISE adapters and runners are described
in `PAPER_ALIGNMENT.md`; upstream materials retain their own licenses.

## Source inventory

| Component | Upstream source | Version or revision | Local use | License / boundary |
|---|---|---|---|---|
| STATE-Bench | https://github.com/microsoft/STATE-Bench | `5644b1838d96bc4483da29642d058ecaa6f80f7f` | Benchmark environment, task definitions, official test split, and scoring under `rise/statebench/benchmark/` | MIT; original license retained at `rise/statebench/benchmark/LICENSE` |
| OAgents | https://github.com/OPPO-PersonalAI/OAgents | `027f2c4579ee7e7767bfe54c66df48a902d43e98` | Official ORM list-wise selector prompt used by the Best-of-4 adaptations | Apache-2.0; prompt and license retained under each `third_party/OAgents/` or `vendor/oagents/` directory |
| AppWorld | https://github.com/stonybrooknlp/appworld | PyPI `appworld==0.1.3.post1` | AppWorld environment, evaluator, encrypted apps package, Test-N and Test-C data | Apache-2.0 plus AppWorld's protected-content redistribution terms; see `appworld/NOTICE.md` |
| AppWorld data | https://s3.us-west-2.amazonaws.com/appworld.dev/data-0.1.0.bundle | `data-0.1.0.bundle`, SHA-256 in `appworld/assets/manifest.json` | Official encrypted benchmark bundle downloaded during setup | Must remain encrypted when redistributed; extracted `runtime/` is never packaged |
| DeepPlanning code | https://github.com/QwenLM/Qwen-Agent/tree/main/benchmark/deepplanning | Upstream snapshot used by the research workspace; exact code commit was not recorded | Travel/Shopping environments and official evaluators adapted under `deepplanning/` | Qwen-Agent upstream is Apache-2.0; downloaded datasets retain their published terms |
| DeepPlanning data | https://huggingface.co/datasets/Qwen/DeepPlanning | `213876cce679f993a476d01042e13d111c0e3648` | Five official Shopping and Travel database archives installed by `deepplanning/download_assets.py` | Not tracked in Git; URLs, sizes, and SHA-256 values are pinned in `deepplanning/assets/manifest.json` |
| OccuBench | https://github.com/GregxmHu/OccuBench | Upstream snapshot used by the research workspace; exact code commit was not recorded | 382-task data, Language World Model environment, and verifier under `rise/occubench/` | Apache-2.0; included license retained at `rise/occubench/LICENSE` |

## Adaptation boundary

- RISE event compilation, recovery frontier, proposal loop, event credit,
  public-information validation, checkpointing, and cross-benchmark adapters
  are project code.
- OAgents comparisons reuse the official list-wise selection prompt over
  benchmark-specific ReAct trajectories. They are adaptations, not claims of
  reproducing the complete upstream OAgents runtime.
- Evaluator labels, hidden requirements, rewards, and gold states are used only
  after execution for scoring. They are not online selector or proposal input.
- Large assets are downloaded only from the sources listed above. The release
  manifests verify downloads at the formal setup boundary.

## Dependency packages

Python package names and versions are recorded in each benchmark's
`requirements.txt`, lockfile, or constraint file. Packages are obtained from
the user's configured Python package index and retain their individual
licenses. Platform wheel caches are intentionally not committed.
