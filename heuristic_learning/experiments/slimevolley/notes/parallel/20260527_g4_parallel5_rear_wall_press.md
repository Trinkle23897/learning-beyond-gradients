# Generation-4 Parallel5 Rear-Wall Press Probe

Date: 2026-05-27

Worker: C

Label: structural policy improvement

## Protocol

This was a development-only structural branch probe for `rear_wall_press` and
rear-wall low-ball losses. No maintained policy code, report generator, README,
final report, ledger, or existing result file was modified. Transient probe code
was written to `/tmp/g4_parallel5_rear_wall_press.py`, and transient JSON output
was copied into the repository after review:

`heuristic_learning/experiments/slimevolley/results/generation_4_parallel5_rear_wall_press_probe.json`

Seeds used exactly:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

No holdout or audit seeds were used. In particular, seeds `10000..10049` and
`11000..11049` were not used.

Screen opponents were `builtin`, `improved-v4`, `improved-v5`, and
`improved-v6`. I did not expand to full `9000..9049` fixed-pool evaluation
because no candidate was materially promising after the short hard-opponent
screen. The only candidate that matched the `rally-serve` built-in score,
`rw_press_low_close_jump`, regressed both `improved-v5` and `improved-v6`;
therefore no promotion or follow-up is recommended from built-in evidence alone.

## Candidate Definitions

| Candidate | Type | Definition |
| --- | --- | --- |
| `rally_reference` | reference | Current `SlimeVolleyRallyServePolicy`. |
| `baseline_rnn` | neural comparator | Packaged SlimeVolley `baseline-rnn` comparator. |
| `rw_press_brace_nojump` | structural | When inherited `rear_wall_press` fires, force backward/no-jump action `010`. |
| `rw_press_low_close_jump` | structural | When inherited `rear_wall_press` fires with `0.24 <= ball_y <= 0.54`, `abs(ball_x - agent_x) <= 0.48`, `ball_vy < -0.28`, and `ball_vx <= 0.08`, force backward+jump action `011`. |
| `rw_press_two_step_macro` | structural/macro | On low `rear_wall_press`, run backward+jump `011` for one frame, then forward/no-jump `100` for one recovery frame. |
| `rw_bounce_conservative_home` | structural/history | After a confirmed low rear-wall bounce shortly after a rear-wall branch, recover toward defensive home without jump. |
| `rw_press_wider_earlier` | structural/scalar | Use earlier/wider rear-wall thresholds: `rear_wall_press_x=1.96`, `agent_x=1.62`, `y=0.74`, `vy=-0.24`, `jump_margin=0.16`. |

## Screen Results

All rows use seeds `9000..9015`.

| Candidate | Opponent | Mean | W-L-D | Steps | Overrides | Action changes |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| `rally_reference` | `builtin` | `0.3125` | `4-0-12` | `48000` | `0` | `0` |
| `rally_reference` | `improved-v4` | `2.5625` | `15-0-1` | `44632` | `0` | `0` |
| `rally_reference` | `improved-v5` | `1.1250` | `9-3-4` | `48000` | `0` | `0` |
| `rally_reference` | `improved-v6` | `1.1875` | `9-3-4` | `48000` | `0` | `0` |
| `baseline_rnn` | `builtin` | `0.1250` | `6-4-6` | `48000` | `0` | `0` |
| `baseline_rnn` | `improved-v4` | `3.2500` | `16-0-0` | `40985` | `0` | `0` |
| `baseline_rnn` | `improved-v5` | `2.3125` | `14-1-1` | `46353` | `0` | `0` |
| `baseline_rnn` | `improved-v6` | `2.5625` | `14-1-1` | `45819` | `0` | `0` |
| `rw_press_brace_nojump` | `builtin` | `0.2500` | `4-1-11` | `48000` | `51` | `31` |
| `rw_press_brace_nojump` | `improved-v4` | `2.5625` | `15-0-1` | `44628` | `57` | `34` |
| `rw_press_brace_nojump` | `improved-v5` | `1.1250` | `9-3-4` | `48000` | `61` | `34` |
| `rw_press_brace_nojump` | `improved-v6` | `1.1875` | `9-3-4` | `48000` | `60` | `33` |
| `rw_press_low_close_jump` | `builtin` | `0.3125` | `4-0-12` | `48000` | `8` | `6` |
| `rw_press_low_close_jump` | `improved-v4` | `2.6875` | `16-0-0` | `44632` | `15` | `12` |
| `rw_press_low_close_jump` | `improved-v5` | `1.0000` | `8-3-5` | `48000` | `18` | `17` |
| `rw_press_low_close_jump` | `improved-v6` | `1.0625` | `8-3-5` | `48000` | `18` | `17` |
| `rw_press_two_step_macro` | `builtin` | `0.1250` | `3-1-12` | `48000` | `22` | `15` |
| `rw_press_two_step_macro` | `improved-v4` | `2.6250` | `14-0-2` | `44470` | `28` | `23` |
| `rw_press_two_step_macro` | `improved-v5` | `1.0000` | `7-3-6` | `48000` | `38` | `34` |
| `rw_press_two_step_macro` | `improved-v6` | `1.0625` | `7-3-6` | `48000` | `38` | `34` |
| `rw_bounce_conservative_home` | `builtin` | `0.1875` | `3-1-12` | `48000` | `7` | `4` |
| `rw_bounce_conservative_home` | `improved-v4` | `2.2500` | `14-0-2` | `44770` | `10` | `5` |
| `rw_bounce_conservative_home` | `improved-v5` | `1.0000` | `9-4-3` | `48000` | `14` | `7` |
| `rw_bounce_conservative_home` | `improved-v6` | `1.0625` | `9-4-3` | `48000` | `14` | `7` |
| `rw_press_wider_earlier` | `builtin` | `-0.3125` | `0-5-11` | `48000` | `0` | `0` |
| `rw_press_wider_earlier` | `improved-v4` | `2.3125` | `15-0-1` | `44060` | `0` | `0` |
| `rw_press_wider_earlier` | `improved-v5` | `0.7500` | `7-4-5` | `47552` | `0` | `0` |
| `rw_press_wider_earlier` | `improved-v6` | `0.6875` | `7-5-4` | `47552` | `0` | `0` |

Built-in action-change details when available:

| Candidate | Action-change pattern | Count |
| --- | --- | ---: |
| `rw_press_brace_nojump` | `011 -> 010` | `31` |
| `rw_press_low_close_jump` | `010 -> 011` | `6` |
| `rw_press_two_step_macro` | `010 -> 011` | `9` |
| `rw_press_two_step_macro` | `010 -> 100` | `4` |
| `rw_press_two_step_macro` | `011 -> 100` | `2` |
| `rw_bounce_conservative_home` | `010 -> 100` | `4` |

## Failure Analysis

`rw_press_low_close_jump` is the best row, but its signal is not robust. It ties
`rally_reference` on built-in (`0.3125`, `4-0-12`) and improves `improved-v4`
from `2.5625` to `2.6875`, changing that row from `15-0-1` to `16-0-0`.
However, the same rule regresses `improved-v5` from `1.1250` to `1.0000` and
`improved-v6` from `1.1875` to `1.0625`, each dropping one win into a draw.

`rw_press_brace_nojump` is not viable because it adds a built-in loss
(`0.2500`, `4-1-11`) while leaving the archived hard rows unchanged. The result
suggests that suppressing jump broadly inside `rear_wall_press` removes at least
one useful rescue.

`rw_press_two_step_macro` and `rw_bounce_conservative_home` both harm the
built-in row and the harder archived rows. The post-bounce/home recovery signal
appears too ambiguous at this short-history granularity.

`rw_press_wider_earlier` is strongly negative. It produced no counted wrapper
overrides because the behavior changed through config thresholds rather than an
outer override, but the score collapse indicates that widening the branch pulls
too many non-rear-wall states into the rear-wall controller.

## Promotion Recommendation

Do not promote any candidate from this run.

Best result: `rw_press_low_close_jump`, mean `0.3125`, W-L-D `4-0-12`, `48000`
steps against `builtin` on seeds `9000..9015`, with `8` overrides and `6`
action changes. It also scored `2.6875`, `16-0-0` against `improved-v4`, but it
regressed `improved-v5` and `improved-v6`, so it should not receive full-pool
follow-up or maintained-policy changes from this evidence.
