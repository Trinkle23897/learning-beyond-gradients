# Generation-5 Net-Pressure Structural Attempt

## Protocol

- Generation: `slimevolley-g5`
- Development seeds used: `12000..12049`
- Short screen subset: `12000..12015`
- Holdout seeds not used: `13000..13049`
- Audit seeds not used: `14000..14049`
- Prior consumed holdouts not used for tuning: generation-1 `1000..1049`, generation-2 `4000..4049`, generation-3 `7000..7049`, generation-4 `10000..10049`
- Ledger: `experiments/slimevolley/results/generation_5_trials.jsonl`
- Summary: `experiments/slimevolley/results/generation_5_summary.csv`
- Tests recorded for rows: `python3 -m pytest tests/test_slimevolley_optional.py -q`, pass

## Candidate Definition

`net-pressure` is a structural policy probe extending `rally-serve` with one named front-court rule. If the ball is near the front court, above low-rescue height, moving toward the opponent, and the agent is behind the contact point, it applies forward+jump (`101`). The intent is to convert passive draw states into point-winning pressure without using neural runtime behavior.

Rule bounds:

- `ball_x`: `-0.08..0.55`
- `ball_y`: `0.58..1.30`
- `ball_vx <= -0.02`
- `ball_vy <= 0.08`
- `agent_x - ball_x`: `0.08..0.72`

Change type: `structural policy improvement`.

## Built-In Development Results

| Policy | Seeds | Mean | W/L/D | Steps | Notes |
| --- | --- | ---: | --- | ---: | --- |
| improved-tuned | `12000..12049` | -0.74 | 6/28/16 | 150000 | scalar/config baseline |
| attack | `12000..12049` | -0.40 | 6/20/24 | 150000 | prior structural candidate |
| rally-serve | `12000..12049` | -0.28 | 7/20/23 | 150000 | prior best heuristic candidate |
| baseline-rnn | `12000..12049` | -0.18 | 18/19/13 | 149774 | packaged neural/RNN comparator |
| net-pressure short screen | `12000..12015` | 0.0625 | 3/4/9 | 48000 | fixed dev subset only |
| net-pressure full dev | `12000..12049` | -0.06 | 11/14/25 | 150000 | structural probe; beats built-in dev comparator but not promoted yet |

Built-in development delta versus `baseline-rnn`: `+0.12` mean. This is development evidence only.

## Fixed Development Opponent-Pool Check

Because `net-pressure` beat `baseline-rnn` on built-in development seeds, it was checked against a fixed development opponent pool before any holdout use. Same-seed comparator rows for `baseline-rnn` and `rally-serve` are now present for the fixed pool.

| Opponent | net-pressure mean | baseline-rnn mean | rally-serve mean |
| --- | ---: | ---: | ---: |
| builtin | -0.06 | -0.18 | -0.28 |
| random | 4.90 | 4.88 | 4.90 |
| initial | 4.86 | 4.86 | 4.88 |
| improved-v0 | 4.84 | 4.86 | 4.88 |
| improved-v2 | 4.68 | 4.80 | 4.66 |
| improved-v3 | 3.08 | 4.24 | 2.84 |
| improved-v4 | 2.56 | 3.70 | 2.38 |
| improved-v5 | 1.20 | 2.38 | 1.32 |
| improved-v6 | 1.22 | 2.40 | 1.28 |
| rally-serve | 0.10 |  |  |

The fixed-pool result is mixed. `net-pressure` beats `baseline-rnn` on the built-in development mean and beats `rally-serve` on built-in, improved-v2, improved-v3, and improved-v4. It lags `baseline-rnn` on stronger archived opponents and does not dominate `rally-serve` across improved-v5/improved-v6.

## Diagnostics

The full built-in row increased forward+jump usage compared with `rally-serve`:

- `rally-serve` action `101`: `3214`
- `net-pressure` action `101`: `6750`
- `baseline-rnn` action `101`: `54634`

`net-pressure` improved score mainly by reducing losses (`20 -> 14`) and increasing wins (`7 -> 11`) versus `rally-serve`; it still draws often (`25`) and wins fewer episodes than `baseline-rnn` (`11` versus `18`).

## Failure Analysis

The candidate is promising but incomplete. It beats the packaged RNN on built-in generation-5 development mean, but the win profile is weaker: `net-pressure` has fewer wins and more draws than `baseline-rnn`. The completed fixed-pool comparator shows that the built-in gain does not transfer to broad superiority: `net-pressure` trails `baseline-rnn` against improved-v3 through improved-v6 and trails or ties `rally-serve` on several archived opponents.

No holdout or audit seeds were used. This result must not be treated as final generalization evidence.

## Promotion Recommendation

Do not use generation-5 holdout yet.

Recommended next step: inspect traces from `net-pressure` draws where `baseline-rnn` wins, then make at most one fresh structural edit and rerun the fixed generation-5 development pool. Promote only if the candidate keeps the built-in gain and does not regress the fixed development opponent pool relative to prior heuristic candidates.
