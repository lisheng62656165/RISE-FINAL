# Paper-to-Code Alignment

This document maps the paper's RISE algorithm to the anonymous release. It
contains method contracts, not manuscript results or historical run records.

## Shared algorithm

Every adapter implements the same accepted-trajectory loop:

1. Run one unguided trajectory in a fresh environment and accept it initially.
2. Compile its public execution into events and a recovery frontier.
3. Run a complete guided proposal in another fresh environment.
4. Skip selection when the public representations do not materially disagree.
5. Otherwise compare the two complete public trajectories. Invalid selector
   output retains the incumbent.
6. Validate preserve IDs against the selected side and avoid IDs against the
   rejected side, then project nominated events to structural shapes.
7. Carry only structural credit and an unresolved issue into the next round.
8. Return the final accepted trajectory after at most three proposals.

The structural projection may retain operation, event class, tool, entity
field names, argument keys, result class, interaction type, and source event
IDs. It excludes literal argument values, result bodies, and selector prose.

## Public-information boundary

Generation and selection may read the visible task, public tool schemas,
public actions, public observations, public results, and derived event views.
They must not read evaluator labels, verifier output, hidden requirements,
gold actions, final-state diffs, rewards, or another method's task outcome.
FRD is adjudicated retrospectively and is never an online control label.

## Benchmark adapters

| Benchmark | RISE entry point | Public disagreement | Credit implementation |
|---|---|---|---|
| StateBench | `rise/statebench/run_statetrace_eds_eca_paper.py` | Transaction content and order | Rule-based source validation and shape projection |
| AppWorld | `appworld/scripts/run_appworld_state_trace_eds_eca.py` | Ordered API signatures | Joint selector nominations, source validation, shape projection |
| OccuBench | `rise/occubench/run_occubench_eds_eca_mimo.py` | Public action-observation transactions | Joint selector nominations through the vendored StateBench event core |
| DeepPlanning | `deepplanning/run_deepplanning_eds_eca.py` | Tool, argument-key, result-category sequence or final answer | Joint nominations, source validation, shape projection |

`StateTrace-EDS-ECA`, `StateBench-EDS-ECA`, and AppWorld's `faithful-v3`
remain in compatibility entry points and output schemas. They denote the RISE
adapter, not additional methods.

## Evaluation boundary

Scoring runs only after trajectory generation and selection. The repository
contains aggregation code that computes metrics from newly generated outputs;
it does not embed manuscript scores or historical experiment identifiers.
StateBench reports PASS@1, PASS5, and UX. AppWorld reports TGC and SGC for both
official splits. OccuBench reports PASS@1. DeepPlanning Travel reports
Delivery, Commonsense, Personalized, and Composite separately for Chinese and
English; its reporter requires the explicit 120-task cohort IDs for each
language.
