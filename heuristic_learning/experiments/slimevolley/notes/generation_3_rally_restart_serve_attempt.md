# Generation-3 Rally Restart Serve Attempt

Status: rolled back after development-seed evidence.

## Diagnosis

SlimeVolley reset traces on development seed `6000` showed that the current `serve` branch was effectively inert: the environment starts and restarts rallies around `ball_y=1.2`, while the legacy serve gate required `ball_y >= 1.45` and was also tied to the first episode steps. This suggested a per-rally, state-based restart detector.

## Changes Tried

1. Added `rally_restart_serve`, a state detector for reset-like ball states near center with upward velocity while the agent is grounded. The first version jumped immediately.
2. Revised the detector into approach and hit phases, moving toward the attack home position first and jumping only when near that target.

## Development Evidence

- Rollback baseline `improved` vs `builtin`, generation-3 dev seeds `6000..6049`: mean `-4.24`, W/L/D `0/49/1`.
- Immediate restart jump version: mean `-4.32`, W/L/D `0/49/1`.
- Approach-then-hit revision: mean `-4.26`, W/L/D `0/49/1`.

## Decision

Both versions underperformed the rollback baseline on the primary built-in-opponent development evaluation. The branch was therefore removed before any opponent-pool tournament or holdout use. The failed trial rows remain append-only in `generation_3_trials.jsonl`.

## Next Hypothesis

The inert serve detector is a real code smell, but a simple state-based restart serve does not solve the built-in gap. Future attempts should first compare point-level trajectories after each restart to see whether serve changes alter the next low-return failure, or target return placement after contact rather than the restart itself.
