# Generation-4 Grounded Low Receive Subagent V2

Date: 2026-05-27

Worker: 2

## Protocol

This was a development-only structural branch probe pass for
`grounded_low_receive`, focused on stacked-frame and temporal cues beyond raw
single-frame `ball_vx`/`ball_vy`.

No source, policy, test, ledger, summary, holdout, or audit files were edited or
written by the probe harness. Candidate classes were transient in-memory
subclasses in direct no-ledger commands from `heuristic_learning/` using:

```bash
PYTHONPATH=. .venv/bin/python <temporary inline probe harness>
```

Short screening used fixed generation-4 development seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

Full expansion used fixed generation-4 development seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

No holdout or audit seeds were used. In particular, no `10000..10049`,
`11000..11049`, `13000..13049`, or `14000..14049` ranges were run.

## Candidate Definitions

All heuristic probes wrap current `rally-serve` and only alter behavior around
low grounded receive or stacked low-ball conditions. No maintained policy module
was edited.

| Candidate | Structural label | Definition |
| --- | --- | --- |
| `rally_serve_reference` | reference | Current generation-4 `rally-serve` candidate unchanged. |
| `baseline_rnn_reference` | neural comparator reference | Packaged SlimeVolley RNN wrapper, included for context only. |
| `glr_stacked_low_detector` | structural/history: stacked-frame low-ball detector | When base `grounded_low_receive` fires, keep no-jump suppression only if a stacked window confirms monotone low descent: at least 5 frames, at least 4 low frames, at least 3 descending transitions, stacked `vy <= -0.012`, stacked time-to-floor `<= 18` frames, and no recent upward flip. Otherwise restore ordinary low-rescue jump-window behavior using stacked horizontal motion for the target. |
| `glr_delayed_jump_recovery` | structural/history: delayed jump suppression/recovery | When base `grounded_low_receive` fires, allow the current no-jump action but arm a 3-frame recovery window. During that window, force a low-rescue jump if the stacked trajectory still shows a reachable low falling ball. |
| `glr_low_incoming_fast_mode` | structural/history: low incoming fast ball mode | On base `grounded_low_receive`, or on any stacked low incoming fast ball (`low_frames >= 3`, stacked `vx >= 0.012`, stacked `vy <= -0.010`, time-to-floor `<= 22` frames), force low-rescue jump behavior keyed to stacked horizontal motion. |
| `glr_temporal_confidence_gate` | structural/history: temporal confidence gate | When base `grounded_low_receive` fires, keep suppression only if raw and stacked vertical motion agree, stacked descent is monotone, predicted floor x is reachable, and there is no recent opponent contact or upward flip. Otherwise restore low-rescue jump-window behavior. |

## Short Screen

Screen opponents were `builtin`, `improved-v4`, and `improved-v6`, using seeds
`9000..9015`.

| Candidate | Opponent | Mean | W-L-D | Steps | Probe notes |
| --- | --- | ---: | --- | ---: | --- |
| `rally_serve_reference` | `builtin` | `0.3125` | `4/0/12` | `48000` | reference |
| `baseline_rnn_reference` | `builtin` | `0.1250` | `6/4/6` | `48000` | reference |
| `glr_stacked_low_detector` | `builtin` | `0.3125` | `4/0/12` | `48000` | `base_glr=6`, kept suppression `6`, changed actions `0` |
| `glr_delayed_jump_recovery` | `builtin` | `0.3125` | `4/0/12` | `48000` | `base_glr=6`, armed `6`, recovery jumps `0` |
| `glr_low_incoming_fast_mode` | `builtin` | `-1.3750` | `2/11/3` | `48000` | changed actions `1074`, low incoming frames `1502` |
| `glr_temporal_confidence_gate` | `builtin` | `0.3125` | `4/0/12` | `48000` | `base_glr=6`, kept `2`, restored `4`, changed actions `4` |
| `rally_serve_reference` | `improved-v4` | `2.5625` | `15/0/1` | `44632` | reference |
| `baseline_rnn_reference` | `improved-v4` | `3.2500` | `16/0/0` | `40985` | reference |
| `glr_stacked_low_detector` | `improved-v4` | `2.5625` | `15/0/1` | `44632` | `base_glr=7`, kept suppression `7`, changed actions `0` |
| `glr_delayed_jump_recovery` | `improved-v4` | `2.5625` | `15/0/1` | `44632` | `base_glr=7`, armed `7`, recovery jumps `0` |
| `glr_low_incoming_fast_mode` | `improved-v4` | `0.8750` | `8/3/5` | `45732` | changed actions `854`, low incoming frames `1197` |
| `glr_temporal_confidence_gate` | `improved-v4` | `2.5625` | `15/0/1` | `44632` | `base_glr=7`, kept `6`, restored `1`, changed actions `1` |
| `rally_serve_reference` | `improved-v6` | `1.1875` | `9/3/4` | `48000` | reference |
| `baseline_rnn_reference` | `improved-v6` | `2.5625` | `14/1/1` | `45819` | reference |
| `glr_stacked_low_detector` | `improved-v6` | `1.1875` | `9/3/4` | `48000` | `base_glr=8`, kept `6`, restored `2`, changed actions `2` |
| `glr_delayed_jump_recovery` | `improved-v6` | `1.1875` | `9/3/4` | `48000` | `base_glr=8`, armed `8`, recovery jumps `0` |
| `glr_low_incoming_fast_mode` | `improved-v6` | `1.0625` | `8/4/4` | `44938` | changed actions `849`, low incoming frames `1178` |
| `glr_temporal_confidence_gate` | `improved-v6` | `1.1875` | `9/3/4` | `48000` | `base_glr=8`, kept `2`, restored `6`, changed actions `6` |

Short-screen interpretation: no candidate beat `rally_serve_reference` on any
screen opponent. `glr_low_incoming_fast_mode` was actively harmful, especially
against `builtin`, because the broader stacked detector fired hundreds of times
outside the sparse base GLR branch. The only probe worth expanding was
`glr_temporal_confidence_gate`: it changed actual GLR actions without a screen
regression.

## Full Development Fixed Pool

Expanded candidate: `glr_temporal_confidence_gate`.

Seeds: `9000..9049`. Opponents: `builtin`, `random`, `initial`,
`improved-v0`, `improved-v2`, `improved-v3`, `improved-v4`, `improved-v5`,
`improved-v6`.

| Candidate | Opponent | Mean | W-L-D | Steps | GLR frames | Changed actions | Gate kept/restored |
| --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| `glr_temporal_confidence_gate` | `builtin` | `0.14` | `13/8/29` | `150000` | `30` | `17` | `13/17` |
| `glr_temporal_confidence_gate` | `random` | `4.74` | `50/0/0` | `38217` | `13` | `0` | `13/0` |
| `glr_temporal_confidence_gate` | `initial` | `4.68` | `50/0/0` | `44634` | `13` | `0` | `13/0` |
| `glr_temporal_confidence_gate` | `improved-v0` | `4.70` | `50/0/0` | `43242` | `15` | `2` | `13/2` |
| `glr_temporal_confidence_gate` | `improved-v2` | `4.38` | `49/1/0` | `76391` | `21` | `2` | `19/2` |
| `glr_temporal_confidence_gate` | `improved-v3` | `2.98` | `48/0/2` | `138122` | `18` | `3` | `15/3` |
| `glr_temporal_confidence_gate` | `improved-v4` | `2.34` | `44/0/6` | `143814` | `16` | `1` | `15/1` |
| `glr_temporal_confidence_gate` | `improved-v5` | `1.16` | `32/7/11` | `149716` | `19` | `8` | `11/8` |
| `glr_temporal_confidence_gate` | `improved-v6` | `1.22` | `32/7/11` | `149716` | `17` | `6` | `11/6` |

These rows match the existing `rally-serve` fixed-pool development matrix:
`builtin 0.14`, `random 4.74`, `initial 4.68`, `improved-v0 4.70`,
`improved-v2 4.38`, `improved-v3 2.98`, `improved-v4 2.34`,
`improved-v5 1.16`, and `improved-v6 1.22`.

## Failure Analysis

The branch-local `grounded_low_receive` signal remains too sparse to provide a
useful promotion path. On the full `builtin` run, the confidence gate touched 30
GLR frames out of 150000 steps and changed only 17 actions. That was enough to
exercise the structural idea, but not enough to move any episode outcome.

The stacked-frame low-ball signals are abundant but not selective. On full
`builtin`, the confidence-gate wrapper counted 11545 stacked-low-detector
frames and 27619 recent-upward-flip frames, while base GLR occurred only 30
times. The broad `glr_low_incoming_fast_mode` demonstrates the risk: expanding
from GLR into the larger stacked-low region produced 1074 action changes on the
short `builtin` screen and collapsed score from `0.3125` to `-1.3750`.

The delayed recovery rule did not fire a recovery jump on the short screen. It
armed on every base GLR frame, but the follow-up reachability gate did not find
a later safe jump opportunity. That suggests the current no-jump GLR frames are
not typically followed by a missed obvious recovery contact in this seed slice.

The temporal confidence gate is the cleanest branch-local probe because it
changed GLR actions while avoiding screen regressions. However, its full
fixed-pool scores exactly match `rally-serve`; it is behavioral churn without
measured score gain. It also does not address the larger known gap versus the
neural comparator on hard archived opponents such as `improved-v4` and
`improved-v6`.

## Promotion Recommendation

Do not promote any generation-4 `grounded_low_receive` temporal/stacked-frame
candidate from this pass.

Best candidate by interpretability is `glr_temporal_confidence_gate`, but it is
only a tie with current `rally-serve`: full development `builtin` mean `0.14`,
W-L-D `13/8/29`, `150000` steps, and the fixed archived opponent pool exactly
matches the current `rally-serve` matrix. The broader stacked low-incoming mode
is a clear negative result and should not be pursued without a much narrower
contact-quality discriminator.
