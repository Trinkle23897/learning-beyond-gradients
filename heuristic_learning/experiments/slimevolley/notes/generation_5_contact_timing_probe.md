# Generation-5 Contact-Timing Probe

Date: 2026-05-27

## Scope

This note records a development-only diagnostic and structural probe after the
rally-setup attempt failed. The question was whether the hard-opponent gap to
`baseline-rnn` is caused by local jump/contact timing in low front-court
terminal windows.

No maintained policy/config/test edit was promoted. No canonical ledger row was
appended. No generation-5 holdout seeds `13000..13049` and no generation-5
audit seeds `14000..14049` were used.

Artifacts:

- Probe script: `experiments/slimevolley/probes/g5_contact_timing_probe.py`
- JSON result: `experiments/slimevolley/results/generation_5_contact_timing_probe.json`

Seed use:

- Diagnostics: `12000..12015`
- Short screen: `12000..12015`
- Full fixed-pool check: not run, because all contact-timing candidates tied
  the reference short-screen table.

## Trace Diagnostic

The diagnostic scanned the last 32 frames before point events and counted low
front-court contact windows (`ball_x` near the agent side/front court,
`ball_y <= 0.40`, descending quickly, and agent within contact distance).

| Policy | Opponent | Low-contact events | Low-contact frames | Actions | Mean dx/vx/vy |
| --- | --- | --- | --- | --- | --- |
| `net_pressure_reference` | `improved-v3` | `{'point_lost': 6}` | `{'point_lost:frames': 19, 'point_lost:jump_frames': 15}` | `{'000': 1, '100': 3, '101': 15}` | `0.229/-0.178/-1.433` |
| `net_pressure_reference` | `improved-v4` | `{'point_lost': 6}` | `{'point_lost:frames': 16, 'point_lost:jump_frames': 14}` | `{'000': 1, '100': 1, '101': 14}` | `0.228/0.144/-1.471` |
| `net_pressure_reference` | `improved-v5` | `{'point_lost': 4, 'point_won': 1}` | `{'point_lost:frames': 15, 'point_lost:jump_frames': 14, 'point_won:frames': 1, 'point_won:jump_frames': 1}` | `{'100': 1, '101': 15}` | `0.255/-0.963/-1.326` |
| `net_pressure_reference` | `improved-v6` | `{'point_lost': 4, 'point_won': 1}` | `{'point_lost:frames': 15, 'point_lost:jump_frames': 14, 'point_won:frames': 1, 'point_won:jump_frames': 1}` | `{'100': 1, '101': 15}` | `0.255/-0.963/-1.326` |
| `baseline_rnn` | `improved-v3` | `{'point_lost': 4}` | `{'point_lost:frames': 13, 'point_lost:jump_frames': 13}` | `{'001': 4, '101': 9}` | `0.203/-0.540/-1.564` |
| `baseline_rnn` | `improved-v4` | `{'point_lost': 4}` | `{'point_lost:frames': 13, 'point_lost:jump_frames': 13}` | `{'001': 4, '101': 9}` | `0.203/-0.540/-1.564` |
| `baseline_rnn` | `improved-v5` | `{'point_lost': 2}` | `{'point_lost:frames': 6, 'point_lost:jump_frames': 6}` | `{'001': 3, '101': 3}` | `0.158/-0.043/-1.843` |
| `baseline_rnn` | `improved-v6` | `{'point_lost': 2}` | `{'point_lost:frames': 6, 'point_lost:jump_frames': 6}` | `{'001': 3, '101': 3}` | `0.158/-0.043/-1.843` |

Diagnostic interpretation: the transparent heuristic is not simply failing to
jump in these windows. It already emits `101` on most low-contact terminal
frames. The RNN loses fewer such points and mixes vertical `001` with `101`,
which suggests a contact-angle/timing issue rather than a missing jump bit.

## Short Screen

The structural candidates were narrow overrides around `net-pressure`:

- `low_commit_jump`: keep base movement but force jump on very low descending
  front receive.
- `low_back_jump`: issue backward+jump on the same detector.
- `low_noop_jump`: issue vertical jump on the same detector.
- `low_positive_vx_jump`: only force base+jump when the ball is still moving
  rearward.
- `low_positive_vx_back_jump`: only force backward+jump when the ball is still
  moving rearward.

Seeds: `12000..12015`.

| Candidate | Built-in | improved-v3 | improved-v4 | improved-v5 | improved-v6 | Overrides |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `net_pressure_reference` | `0.0625`, `3/4/9` | `2.8750`, `14/1/1` | `2.4375`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | `0` |
| `baseline_rnn` | `0.2500`, `7/3/6` | `4.1875`, `16/0/0` | `3.7500`, `16/0/0` | `2.5625`, `14/0/2` | `2.5625`, `14/0/2` | `0` |
| `low_commit_jump` | `0.0625`, `3/4/9` | `2.8750`, `14/1/1` | `2.4375`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | `4` |
| `low_back_jump` | `0.0625`, `3/4/9` | `2.8750`, `14/1/1` | `2.4375`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | `4` |
| `low_noop_jump` | `0.0625`, `3/4/9` | `2.8750`, `14/1/1` | `2.4375`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | `4` |
| `low_positive_vx_jump` | `0.0625`, `3/4/9` | `2.8750`, `14/1/1` | `2.4375`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | `4` |
| `low_positive_vx_back_jump` | `0.0625`, `3/4/9` | `2.8750`, `14/1/1` | `2.4375`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | `4` |

## Failure Analysis

Every contact-timing candidate tied the reference table. The stricter detectors
were aligned with the trace diagnosis but fired only four frames across the
whole short screen, because `net-pressure` already uses jump actions in the
dominant low-contact loss windows. Widening the detector would repeat the
previous broad front-net/brace-action failure modes, so no wider policy edit is
justified from this evidence.

This narrows the remaining gap: it is not explained by a missing final jump bit
or a simple replacement of `101` with `001` on very low terminal frames. The
next useful diagnostic should model pre-contact approach quality: where the
agent is several frames before the low terminal window, whether its horizontal
velocity is converging toward the ball, and whether earlier jumps are creating
bad contact angles.

## Decision

Do not promote any contact-timing candidate. Do not run full fixed-pool or
holdout checks for this family.
