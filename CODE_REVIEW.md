# Implementation Audit

This note records the code-level checks that enforce the paper's algorithmic
contract. It deliberately contains no benchmark scores or historical run IDs.

## Enforced invariants

- One unguided anchor and at most three fresh complete proposals.
- Selection only after benchmark-specific material public disagreement.
- Invalid selector output retains the semantic incumbent, independent of
  randomized candidate display order.
- Preserve IDs belong to the selected trajectory and avoid IDs belong to the
  rejected trajectory.
- Cross-round credit is projected to structural event shapes. Literal argument
  values, result bodies, and free-form selector rationale are excluded.
- Evaluator labels, hidden requirements, rewards, and gold state are rejected
  or projected away before online proposal and selection calls.
- RISE and Best-of-4 use the same maximum complete-rollout count; token and
  latency accounting remain separate.

## Adapter checks

- StateBench owns the reference event and transaction representation.
- AppWorld creates a fresh `AppWorld` context for every rollout and tests the
  reversed-display fallback case.
- OccuBench maps public action-observation traces into the same accepted-state
  loop and keeps verifier calls after trajectory selection.
- DeepPlanning validates nomination provenance, projects credit through an
  allowlist, and validates both 120-task language cohorts before table export.

## Release verification

Run the unit tests in each benchmark directory, the DeepPlanning release
check, Python compilation, `git diff --check`, and the anonymity scanner before
building the supplementary archive. Paid API runs are not part of this static
audit and must be recorded in a new output directory with their effective
model, endpoint family, seeds, and completion status.

Synthetic benchmark emails and virtual benchmark paths are fixtures. They are
not author identity and must not be edited during anonymization.
