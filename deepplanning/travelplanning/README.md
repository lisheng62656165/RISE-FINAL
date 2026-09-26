# DeepPlanning Travel Adapter

The Travel adapter is run from `deepplanning/`. Task files are included; the
large English and Chinese databases are installed from the pinned official
release by the parent `download_assets.py`. Do not use historical shell
launchers from older copies of the benchmark.

From the parent directory:

```powershell
python download_assets.py
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
