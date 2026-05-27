# Generation-4 Front-Net Low-Scoop Attempt

Development-only note. Generation-4 holdout seeds `10000..10049` and audit seeds `11000..11049` were not used.

## Diagnosis

After `rear_wall_low_jump`, a development trace refresh on `improved` versus the built-in opponent showed `132` point losses. A simple bucket analysis found `75` losses where the ball ended low near the net (`ball_x <= 0.35`, `ball_y <= 0.34`). On the same development seeds, the packaged `baseline-rnn` comparator had only `7` low-net losses. Raw traces showed the maintained heuristic often stopped around `agent_x ~= 0.267` because of the front overcommit guard while the ball dropped around `ball_x ~= 0.10..0.20`.

## Failed Structural Probes

Two explicit code edits were tested and ledgered on development seeds `9000..9049`:

- Broad `front_net_low_scoop`: when the ball was low near the net, force forward movement and permit a below-normal jump. Result versus built-in: mean `-2.72`, W/L/D `1/45/4`. This was worse than the pre-scoop checkpoint.
- Narrowed `front_net_low_scoop`: additionally require a tighter x/y window, positive `ball_vx`, and the agent already near the front guard. Result versus built-in: mean `-2.36`, W/L/D `1/44/5`. This recovered some damage but still underperformed the pre-scoop checkpoint.

Both variants were rolled back. The maintained `improved` policy returned to the `improved-v6` checkpoint behavior.

## Rollback Result

After rollback:

- `improved` vs `builtin`, seeds `9000..9049`: mean `-2.24`, W/L/D `1/43/6`.
- `improved` vs frozen `improved-v6`, seeds `9000..9049`: mean `0.18`, W/L/D `18/19/13`.
- Same-seed `baseline-rnn` vs `builtin`: mean `0.12`, W/L/D `18/12/20`.

The failed scoop direction is evidence against a naive near-net override. The next structural attempt should use better contact timing or return-placement diagnostics rather than simply overriding the front guard.
