# Generation-3 Delayed Low Receive Attempt

Status: rolled back after development-seed evidence.

## Diagnosis

Generation-3 built-in-opponent traces on dev seeds `6000..6049` showed repeated point losses where the heuristic jumped while grounded with the ball still around `y=0.40..0.48`, then remained airborne as the fast low ball reached floor height. This looked earlier than the rejected rear-wall recovery failure mode.

## Change

A `delayed_low_receive` structural branch was added to the current `improved` policy. When the agent was still grounded, the ball was low but not yet floor-low, the ball was descending quickly, and the ball was within the existing receive window, the branch moved toward the intercept target but suppressed the jump bit.

## Development Evidence

- Pre-change/rollback baseline `improved` vs `builtin`, generation-3 dev seeds `6000..6049`: mean `-4.24`, W/L/D `0/49/1`.
- Post-change `improved` vs `builtin`, generation-3 dev seeds `6000..6049`: mean `-4.72`, W/L/D `0/50/0`.

## Decision

The branch made the primary built-in-opponent score worse before any opponent-pool tournament was needed. The behavior was therefore rolled back. The failed development evaluation remains append-only in `generation_3_trials.jsonl`.

## Next Hypothesis

The early jump pattern is real, but a simple suppression band removes useful contacts. The next structural attempt should use more context, such as whether the ball is coming from the built-in opponent after a strong return, whether the agent is moving in the same direction as the ball, or whether a short macro-action can stay grounded and then jump at a later phase. Keep all work on generation-3 development seeds until the policy and tests are frozen.
