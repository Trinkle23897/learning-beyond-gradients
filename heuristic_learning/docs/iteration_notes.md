# Heuristic Learning Iteration Notes

This file records the intended agent-improvement loop for the benchmark. The
authoritative audit trail is `results/trials.jsonl`; this note explains how to
read the loop.

## Loop

1. Run a fixed-seed evaluation on development seeds.
2. Inspect score summaries, per-episode returns, and failures.
3. Write a short diagnosis in the ledger `failure_analysis` field.
4. Propose one structural or scalar change.
5. Apply the code/config/test edit.
6. Run regression tests.
7. Re-evaluate on development seeds.
8. Append the result to `results/trials.jsonl`.
9. Keep, revise, or roll back based on evidence.
10. Regenerate `results/summary.csv` and `results/final_report.md`.

## Initial Structural Hypotheses

- CartPole: the initial pole-only sign controller may balance briefly while the
  cart drifts. Add a center-cart guard only when the pole is already safe.
- MountainCar: velocity-direction energy pumping wastes steps near the left wall
  and goal approach. Add explicit wall and goal detectors.
- Acrobot: one swing-up rule is likely out of phase near the upright target.
  Add an upright-region mode.
- LunarLander: raw PD control often overcorrects after leg contact. Add landing
  contact guards.
- BipedalWalker: open-loop gait should fail through phase drift. Add contact
  phase resets and a hull recovery mode.

## Required Failure Notes

Every unsuccessful or partial iteration should answer:

- What failed?
- Which seeds or traces showed it?
- Was the change structural, scalar/config, harness/test, logging, bug fix, or invalid?
- What should be tried next, if anything?

