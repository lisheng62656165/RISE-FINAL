# AppWorld Validation Procedure

This file defines release checks. It does not record benchmark scores or a
historical execution result.

## Offline tests

```bash
python -m pytest -q
python tests/integration_smoke.py
```

The tests cover public-event compilation, source ownership of selector credit,
structural projection without literal replay, evaluator-field exclusion,
shared Vanilla candidate identity, official OAgents prompt loading, incomplete
scenario handling, resume behavior, and malformed-selector fallback.

## Algorithm invariants

- Each anchor and proposal executes in a separate fresh `AppWorld` context.
- Selection is skipped when ordered public API signatures do not materially
  disagree.
- Candidate display order may be randomized, but malformed or invalid selector
  output always retains the semantic incumbent.
- Preserve credit is sourced from the selected candidate; avoid credit is
  sourced from the rejected candidate; both are projected to structural event
  shapes before reuse.
- Evaluator success, hidden requirements, rewards, and gold state do not enter
  proposal or selector payloads.
- RISE and Best-of-4 share candidate A in paired comparison mode.

## Live smoke test

After installing AppWorld assets, run one task from each official split with
the intended model endpoint before launching the full batch. Confirm that the
environment executes a public API call, evaluation runs only after trajectory
completion, checkpoints resume, and missing API responses remain incomplete
rather than being converted to task failures.

The Best-of-4 adapter vendors the official ORM list-wise prompt but uses this
release's AppWorld ReAct runner. Report it as an adaptation, not as the entire
upstream OAgents runtime. Parallelism is across tasks; do not infer within-task
parallel wall-clock behavior from the method name.
