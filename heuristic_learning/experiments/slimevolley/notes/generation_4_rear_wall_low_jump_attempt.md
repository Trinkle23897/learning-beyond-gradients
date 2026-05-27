# Generation-4 Rear-Wall Low-Jump Attempt

Development-only note. Generation-4 holdout seeds `10000..10049` and audit seeds `11000..11049` were not used.

## Diagnosis

After `front_hit_suppression`, remaining built-in losses clustered around front-net, floor-low, and rear-wall states. Rear-wall traces showed the current policy backing away from balls near `ball_x >= 2.0` when the ball was below the normal jump threshold, for example `ball_y` around `0.21..0.32` with negative `ball_vx` and `ball_vy`.

## Failed Or Partial Probes

- Front-net emergency rescue improved win count on a short probe but did not improve full 50-seed built-in mean; it also traded off some archived-opponent cells. It was not promoted.
- Floor-scoop rescue for low balls moving toward the net produced no score change on the first 10 development seeds and was not promoted.
- Combined front-net plus rear-wall rescue worsened built-in mean versus the rear-wall-only candidate, so the front-net branch was excluded.

## Kept Structural Edit

The kept `rear_wall_low_jump` rule activates when all are true:

- `ball_x >= 2.0`,
- `ball_y <= 0.32`,
- `ball_vx <= -0.20`,
- `ball_vy < -0.30`,
- and the agent is near the rear wall with `x >= 1.90`.

When active, the policy takes a forward jump action. This is intended to contest low rear-wall balls that the previous rear-wall press mode treated as too low to jump.

## Ledgered Result

Latest generation-4 development rows after the edit:

- `improved` vs `builtin`, seeds `9000..9049`: mean `-2.24`, W/L/D `1/43/6`.
- Same-seed `baseline-rnn` vs `builtin`: mean `0.12`, W/L/D `18/12/20`.

The edit is a small structural improvement, not evidence that the heuristic has beaten the neural comparator.
