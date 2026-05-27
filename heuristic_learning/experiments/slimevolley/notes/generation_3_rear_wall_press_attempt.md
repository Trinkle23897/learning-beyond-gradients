# Generation-3 Rear-Wall Press Attempt

Status: kept after development-seed evidence.

## Diagnosis

The generation-3 contact/return diagnostic artifact showed that the built-in-opponent failure was dominated by rear-wall and low-far-right events. The selected rollback-baseline row had `low_far_right: 130` losses and inferred contact candidates concentrated at `rear_wall: 145`. Several traces showed the policy emitting `000` while the ball was outside the rear guard, because target x was clipped at `rear_guard_x`.

## Change

A `rear_wall_press` structural branch was added to the current `improved` policy. When a low descending ball is outside the rear guard and the agent is already in the back court, the policy presses toward the rear wall instead of accepting the clipped target/no-op behavior. It only jumps when the agent is close enough vertically to plausibly contact the ball.

## Development Evidence

- Pre-change rollback baseline `improved` vs `builtin`, generation-3 dev seeds `6000..6049`: mean `-4.24`, W/L/D `0/49/1`.
- Post-change `improved` vs `builtin`, generation-3 dev seeds `6000..6049`: mean `-3.80`, W/L/D `0/48/2`.
- Refreshed generation-3 round-robin: current `improved` mean across opponents `2.86`, W/L/D `299/37/14`; archived `improved-v3` mean `2.34`, W/L/D `286/50/14`.
- Current `improved` vs `improved-v3`: mean `0.82`, W/L/D `27/15/8`.

## Decision

The branch improved the primary built-in-opponent development result and did not collapse against the archived opponent pool. It is kept as a structural policy improvement. At the time this decision was made, generation-3 holdout was still unopened; the evidence in this note is development evidence only.

## Next Hypothesis

Use the refreshed contact diagnostics from the kept policy to determine whether the remaining built-in losses are still rear-wall dominated or have shifted toward near-net/front-court failures. This was the pre-holdout next hypothesis; subsequent final conclusions must use the frozen generation-3 holdout artifact rather than tuning from this note.
