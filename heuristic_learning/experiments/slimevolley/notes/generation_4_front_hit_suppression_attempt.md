# Generation-4 Front-Hit Suppression Attempt

Development-only note. Generation-4 holdout seeds `10000..10049` and audit seeds `11000..11049` were not used.

## Diagnosis

The previous `improved` policy often jumped while standing in front of a descending own-side ball moving toward the net. Traced seed `9000` showed this redirected the ball deeper into the agent half, creating low floor losses.

## Failed Or Discarded Probes

- Front-blocker probes: constant near-net and jump-heavy controllers were evaluated off-ledger on development seeds and scored around `-4.8` to `-4.85` against the built-in opponent. They were discarded because they were worse than current `improved`.
- Decision-tree distillation probe: shallow transparent trees trained from baseline-rnn development traces reached high action imitation accuracy but scored around `-4.7` to `-4.85` against the built-in opponent because compounding action errors broke rallies. No tree policy was promoted.
- Behind-ball contact probe: moving behind descending balls before contact scored `-4.8` to `-5.0` on short development probes. It was discarded because it damaged the already-working intercept timing.
- Front-net rescue probe: a broad grid for low near-net emergency jumps was started, then stopped after exceeding the intended diagnostic bound. No score from this interrupted probe is used as evidence.

These probes are diagnostic context only. The ledgered policy evidence is the final `front_hit_suppression` structural edit evaluated on fixed development seeds `9000..9049`.

## Kept Structural Edit

The kept rule suppresses jump on actions where all of the following are true:

- the ball is on the agent side,
- the ball is below `front_hit_suppression_y_max`,
- the ball is moving toward the net with `ball_vx < front_hit_suppression_vx`,
- and the agent is in front of the ball.

This is intended to avoid hitting the ball from the wrong side and sending it back into the agent half.

## Ledgered Result

Latest generation-4 development row after the edit:

- `improved` vs `builtin`, seeds `9000..9049`: mean `-2.26`, W/L/D `1/43/6`.
- Same-seed `baseline-rnn` vs `builtin`: mean `0.12`, W/L/D `18/12/20`.

The edit narrows but does not close the neural comparator gap.
