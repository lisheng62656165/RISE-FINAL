# Reviewer-Oriented Code Review

This note records the paper-to-code audit for the anonymous RISE release. It is
intended to make the implementation boundary explicit for reviewers and for a
new reproduction run.

## Verdict

The live implementations match the paper's central algorithmic contract:

- one unguided Vanilla anchor;
- at most three complete proposal rollouts, for a four-rollout budget;
- a fresh benchmark environment for every rollout;
- a selector call only after a material public disagreement;
- public recovery-risk evidence and source-constrained event credit;
- an accepted incumbent that can survive later rejected proposals.

The AppWorld `faithful-v3` entry point and the StateBench
`StateTrace-EDS-ECA` entry point are historical names for the RISE adapter,
not separate algorithms. The mapping is documented in `PAPER_ALIGNMENT.md`.

## Audit Findings

### Matches

1. `rise/statebench/run_statetrace_eds_eca_paper.py` implements the A -> B' ->
   C' -> D' accepted-incumbent loop and persists stage checkpoints.
2. `appworld/scripts/run_appworld_state_trace_eds_eca.py` creates a separate
   `AppWorld` context for the anchor and each proposal. Its selector sees the
   projected event packet, not the stored evaluator result.
3. StateBench uses deterministic structural credit. AppWorld validates
   candidate-local event IDs before constructing preserve/avoid credit.
4. `appworld/scripts/run_appworld_best_of4.py` keeps the official comparison
   as four independent candidates and a separate list-wise selector. It does
   not consume RISE feedback.
5. Evaluator calls and result fields are retained for post-run scoring, but the
   public packet boundary rejects or projects them before online decisions.

### Reviewer Caveats

- The paper's point estimates are reference values in `PAPER_ALIGNMENT.md`;
  they are not presented as a guarantee of bit-identical results from a new
  endpoint.
- The main comparison matches complete rollout count, not token cost or
  latency. Reports should retain the cost fields when comparing methods.
- FRD is a retrospective audit label. The online implementation uses public
  recovery-risk signals and never supplies the FRD label to generation or
  selection.
- The current host has Python 3.9, while the released StateBench environment
  requires Python 3.12. AppWorld's offline tests pass on the current host;
  StateBench must be tested with the documented Python 3.12 environment.
- Synthetic benchmark user emails are data fixtures, not author identity. They
  should not be edited as part of anonymization because changing them changes
  benchmark inputs.

## Engineering Changes In This Release

- Added the existing forbidden-field validator to AppWorld selector packets and
  all AppWorld frontier variants.
- Added a regression test ensuring evaluator fields do not enter a selector
  packet.
- Replaced verbose Chinese runner narration with concise implementation-level
  docstrings in the StateBench entry point.

These changes are boundary checks and documentation-only cleanup on valid
inputs. They do not change model parameters, seeds, prompt text, rollout
count, candidate order, or scoring.

## Verification

The following checks were run after the cleanup:

```text
AppWorld tests: 18 passed
OccuBench tests: 43 passed
DeepPlanning release check: Shopping 50/50/20; Travel zh/en 120/120
Python compileall: passed for appworld, StateBench, and DeepPlanning Python files
Anonymous supplementary: 1,917 files, 5.2 MiB, zip CRC passed
```

Large DeepPlanning databases, the AppWorld encrypted bundle/package, and
platform-specific dependency wheels are not tracked in the lightweight source
tree. Official asset downloaders and pinned manifests were tested by restoring
the databases outside the repository; all 1,937 effective database files
matched the former in-tree copies byte-for-byte by SHA-256.

The paid API pipeline was not invoked by this audit. A full numerical
reproduction still requires a Python 3.12 environment and an API endpoint.
