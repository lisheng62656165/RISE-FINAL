# DeepPlanning Travel Adapter

The Travel adapter is run from `deepplanning/`. Its local databases and task
files are already part of this release. Do not use the historical download or
shell-launcher instructions from older copies of the benchmark.

From the parent directory:

```powershell
python run_deepplanning_travel_inference_only.py --help
python run_deepplanning_eds_eca.py --help
python select_best_of_4_deepplanning.py --help
```

The inference entry point supports `zh` and `en` cohorts. Run the same model,
seed policy, and call budget for Vanilla, RISE, and Best-of-4. Convert and
score plans with the bundled evaluator, then aggregate with
`deepplanning/report_metrics.py` as described in the parent README.

The model configuration is supplied through environment variables or the
parent `models_config.json`. API keys must stay outside the repository.
