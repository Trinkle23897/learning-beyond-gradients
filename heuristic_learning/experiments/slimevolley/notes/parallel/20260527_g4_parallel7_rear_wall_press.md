# Generation-4 Parallel7 Rear-Wall Press Probe

Date: 2026-05-27

Worker: C

## Protocol

Development-only rear-wall branch probe. kind=`structural policy improvement`.
No maintained policy, eval, report, ledger, summary, holdout, or audit file was
edited. The only repository artifact written by this run is this note.

Transient files stayed in `/tmp`:

- `/tmp/g4_parallel7_rear_wall_press_probe.py`
- `/tmp/g4_parallel7_rear_wall_press_results.json`

Command run:

- `cd /home/alpha/dev/research/learning-beyond-gradients/heuristic_learning && PYTHONPATH=. .venv/bin/python /tmp/g4_parallel7_rear_wall_press_probe.py`

Short-screen seeds used exactly:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

Full development seeds used exactly when the promotion protocol required them:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

No holdout seeds `10000..10049` or audit seeds `11000..11049` were used.

## Candidate Definitions

| Candidate | Type | Definition |
| --- | --- | --- |
| `rally_reference` | reference structural plus scalar/config | Current `SlimeVolleyRallyServePolicy`. |
| `post_contact_reference` | reference structural/history plus scalar/config | Current `SlimeVolleyPostContactPolicy`. |
| `baseline_rnn` | neural comparator | Packaged slimevolleygym `BaselinePolicy` wrapper. |
| `rear_wall_force_jump_close` | structural policy improvement | When inherited `rear_wall_press` sees a close low descending ball (`0.24 <= ball_y <= 0.46`, `ball_vy < -0.42`, `abs(ball_x - agent_x) <= 0.30`), force `011`. |
| `rear_wall_low_brace_nojump` | structural policy improvement | When inherited `rear_wall_press` sees a very low clearing ball (`ball_y <= 0.30`, `ball_vx <= 0.12`, `abs(ball_x - agent_x) <= 0.22`), brace with `010`. |
| `rear_wall_early_guard` | structural policy improvement | Before inherited `rear_wall_press`, if `falling_floor_intercept` or `low_ball_rescue` sees `ball_x >= 1.88`, `ball_y <= 0.68`, `ball_vy < -0.42`, retreat to rear guard without jump. |
| `rear_wall_release_forward` | structural policy improvement | When inherited `rear_wall_press` is active but the ball is already leaving the wall (`ball_vx < -0.16`, `ball_y <= 0.42`), recover toward defensive home without jump. |

## Short Screen Results

Seeds: `9000..9015`. Opponents: `builtin`, `improved-v4`, `improved-v6`.

| Candidate | Opponent | Mean | W-L-D | Steps | Trigger frames | Override frames | Action-change frames |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| `rally_reference` | `builtin` | `0.3125` | `4-0-12` | `48000` | `0` | `0` | `0` |
| `rally_reference` | `improved-v4` | `2.5625` | `15-0-1` | `44632` | `0` | `0` | `0` |
| `rally_reference` | `improved-v6` | `1.1875` | `9-3-4` | `48000` | `0` | `0` | `0` |
| `post_contact_reference` | `builtin` | `0.3125` | `4-0-12` | `48000` | `0` | `0` | `0` |
| `post_contact_reference` | `improved-v4` | `2.7500` | `15-0-1` | `44527` | `0` | `0` | `0` |
| `post_contact_reference` | `improved-v6` | `1.3750` | `9-3-4` | `47686` | `0` | `0` | `0` |
| `baseline_rnn` | `builtin` | `0.1250` | `6-4-6` | `48000` | `0` | `0` | `0` |
| `baseline_rnn` | `improved-v4` | `3.2500` | `16-0-0` | `40985` | `0` | `0` | `0` |
| `baseline_rnn` | `improved-v6` | `2.5625` | `14-1-1` | `45819` | `0` | `0` | `0` |
| `rear_wall_force_jump_close` | `builtin` | `0.3125` | `4-0-12` | `48000` | `3` | `3` | `2` |
| `rear_wall_force_jump_close` | `improved-v4` | `2.8750` | `16-0-0` | `44527` | `8` | `8` | `6` |
| `rear_wall_force_jump_close` | `improved-v6` | `1.2500` | `8-3-5` | `47686` | `10` | `10` | `8` |
| `rear_wall_low_brace_nojump` | `builtin` | `0.3125` | `4-0-12` | `48000` | `0` | `0` | `0` |
| `rear_wall_low_brace_nojump` | `improved-v4` | `2.7500` | `15-0-1` | `44527` | `0` | `0` | `0` |
| `rear_wall_low_brace_nojump` | `improved-v6` | `1.3750` | `9-3-4` | `47686` | `2` | `2` | `0` |
| `rear_wall_early_guard` | `builtin` | `0.1250` | `3-2-11` | `48000` | `32` | `32` | `25` |
| `rear_wall_early_guard` | `improved-v4` | `2.5000` | `14-0-2` | `44632` | `71` | `71` | `63` |
| `rear_wall_early_guard` | `improved-v6` | `1.0000` | `7-4-5` | `47674` | `60` | `60` | `54` |
| `rear_wall_release_forward` | `builtin` | `0.2500` | `3-0-13` | `48000` | `2` | `2` | `2` |
| `rear_wall_release_forward` | `improved-v4` | `2.8750` | `15-0-1` | `44369` | `8` | `8` | `8` |
| `rear_wall_release_forward` | `improved-v6` | `1.5000` | `9-4-3` | `47686` | `5` | `5` | `5` |

Short-screen gate observations:

- `post_contact_reference` already improved the archived rows over `rally_reference`: `+0.1875` on `improved-v4` and `+0.1875` on `improved-v6`.
- `rear_wall_force_jump_close` improved `improved-v4` but regressed `improved-v6`.
- `rear_wall_early_guard` was broadly harmful and did not warrant full-dev follow-up.
- `rear_wall_low_brace_nojump` and `rear_wall_release_forward` cleared the screen gate for a full built-in check.

## Full Built-In Check

Seeds: `9000..9049`. Opponent: `builtin`.

| Candidate | Mean | W-L-D | Steps | Trigger frames | Override frames | Action-change frames |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `rally_reference` | `0.1400` | `13-8-29` | `150000` | `0` | `0` | `0` |
| `post_contact_reference` | `0.1400` | `13-8-29` | `150000` | `0` | `0` | `0` |
| `baseline_rnn` | `0.1200` | `18-12-20` | `150000` | `0` | `0` | `0` |
| `rear_wall_low_brace_nojump` | `0.1400` | `13-8-29` | `150000` | `0` | `0` | `0` |
| `rear_wall_release_forward` | `0.1000` | `12-8-30` | `150000` | `10` | `10` | `10` |

Protocol decision:

- `rear_wall_release_forward` failed the promotion gate on full built-in dev seeds because it fell below `baseline_rnn` (`0.1000` vs `0.1200`).
- `rear_wall_low_brace_nojump` tied `rally_reference` and `post_contact_reference` on full built-in and still exceeded the built-in `baseline_rnn` mean, so it required the fixed development opponent-pool check before any recommendation.

## Fixed Development Opponent-Pool Check

Seeds: `9000..9049`. Candidate: `rear_wall_low_brace_nojump`. Opponents:
`builtin`, `random`, `initial`, `improved-v0`, `improved-v2`, `improved-v3`,
`improved-v4`, `improved-v5`, `improved-v6`.

| Opponent | `rally_reference` mean/W-L-D/steps | `post_contact_reference` mean/W-L-D/steps | `baseline_rnn` mean/W-L-D/steps | `rear_wall_low_brace_nojump` mean/W-L-D/steps | Trigger / override / action changes |
| --- | --- | --- | --- | --- | ---: |
| `builtin` | `0.1400` / `13-8-29` / `150000` | `0.1400` / `13-8-29` / `150000` | `0.1200` / `18-12-20` / `150000` | `0.1400` / `13-8-29` / `150000` | `0 / 0 / 0` |
| `random` | `4.7400` / `50-0-0` / `38217` | `4.7400` / `50-0-0` / `38217` | `4.8000` / `50-0-0` / `30603` | `4.7400` / `50-0-0` / `38217` | `0 / 0 / 0` |
| `initial` | `4.6800` / `50-0-0` / `44634` | `4.6800` / `50-0-0` / `44634` | `4.7600` / `50-0-0` / `34004` | `4.6800` / `50-0-0` / `44634` | `0 / 0 / 0` |
| `improved-v0` | `4.7000` / `50-0-0` / `43242` | `4.7000` / `50-0-0` / `43242` | `4.8200` / `50-0-0` / `32843` | `4.7000` / `50-0-0` / `43242` | `0 / 0 / 0` |
| `improved-v2` | `4.3800` / `49-1-0` / `76391` | `4.3800` / `49-1-0` / `76391` | `4.8000` / `50-0-0` / `54551` | `4.3800` / `49-1-0` / `76391` | `0 / 0 / 0` |
| `improved-v3` | `2.9800` / `48-0-2` / `138122` | `3.0400` / `48-0-2` / `137816` | `3.8400` / `50-0-0` / `118182` | `3.0400` / `48-0-2` / `137816` | `0 / 0 / 0` |
| `improved-v4` | `2.3400` / `44-0-6` / `143814` | `2.4000` / `44-0-6` / `143709` | `3.2600` / `48-0-2` / `132511` | `2.4000` / `44-0-6` / `143709` | `0 / 0 / 0` |
| `improved-v5` | `1.1600` / `32-7-11` / `149716` | `1.2200` / `32-7-11` / `149402` | `2.1000` / `42-2-6` / `145370` | `1.2200` / `32-7-11` / `149402` | `2 / 2 / 0` |
| `improved-v6` | `1.2200` / `32-7-11` / `149716` | `1.2800` / `32-7-11` / `149402` | `2.1800` / `42-2-6` / `144837` | `1.2800` / `32-7-11` / `149402` | `2 / 2 / 0` |

The fixed-pool result makes the key point clear: `rear_wall_low_brace_nojump`
is not a real behavioral improvement. Its only non-zero counters were two
same-action triggers on `improved-v5` and `improved-v6`, so it reproduced the
`post_contact_reference` rows exactly and never changed the action key.

## Failure Analysis

`rear_wall_force_jump_close` found a narrow archived-opponent gain but not a
robust one. It improved the `improved-v4` short-screen row from `2.7500` to
`2.8750`, but it also regressed `improved-v6` from `1.3750` to `1.2500` and
left built-in unchanged. That is not enough to justify further promotion work.

`rear_wall_early_guard` was the clearest negative result. The early retreat rule
fired often (`32` built-in trigger/override frames, `71` against
`improved-v4`, `60` against `improved-v6`) and converted many actions, but it
reduced all three short-screen rows. Generic early retreat appears too passive
for the low rear-wall exchanges that the current `post-contact` policy already
handles.

`rear_wall_release_forward` looked plausible on the short screen because it
raised the archived rows to `2.8750` on `improved-v4` and `1.5000` on
`improved-v6`, but the full built-in check rejected it. The candidate dropped
from `0.1400` to `0.1000` on seeds `9000..9049`, so the archived gain came from
a fragile trade that harms the built-in dev row.

`rear_wall_low_brace_nojump` advanced furthest in the protocol, but it exposed a
different failure mode: it did not create a meaningful policy change. On the
screen and full built-in checks it produced zero trigger or action-change frames,
and on the fixed pool it matched `post_contact_reference` exactly while showing
only two same-action triggers on `improved-v5` and `improved-v6`. The current
`post-contact` controller is already effectively taking that brace in the rare
states this rule was meant to target.

Overall, this run did not find a rear-wall branch change that closes the large
gap to `baseline_rnn` on `improved-v4` or `improved-v6`. The most useful signal
is negative: broad early retreat is harmful, a forced close jump helps one
archived row but hurts another, and the low no-jump brace is already implicit in
the current policy behavior.

## Promotion Recommendation

Do not promote any candidate from this run.

`rear_wall_release_forward` fails the full built-in gate. `rear_wall_low_brace_nojump`
survives the gate only because it is behaviorally identical to
`post_contact_reference`, not because it adds a new robust structural rule.
`rear_wall_force_jump_close` and `rear_wall_early_guard` are negative evidence.
No holdout or audit evaluation is warranted from this probe.
