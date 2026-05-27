# Generation-5 Hard-Opponent Trace And Probe

Date: 2026-05-27

## Protocol

This note records development-only diagnostics after the generation-5 fixed-pool
check showed that `net-pressure` beats `baseline-rnn` on built-in development
mean but trails it on harder archived opponents.

Exact seeds used for all trace and probe rows in this note: `12000..12015`.
These are a fixed short subset of generation-5 development seeds. No holdout or
audit seeds were used. No ledger rows were appended for these exploratory trace
screens; the machine-readable diagnostic artifacts are:

- `experiments/slimevolley/results/generation_5_hard_opponent_trace_diagnostics.json`
- `experiments/slimevolley/results/generation_5_front_net_probe_screen.json`
- `experiments/slimevolley/results/generation_5_brace_action_probe_screen.json`
- `experiments/slimevolley/results/generation_5_contact_quality_probe_screen.json`

No policy, config, or test edit was made from these screens.

## Trace Diagnostic

The trace comparison used `trace_window=16` for `net-pressure` and
`baseline-rnn` against the hard archived opponents where the full generation-5
fixed-pool gap was largest.

| Policy | Opponent | Mean | W-L-D | Steps | Jump rate | Forward rate |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| `net-pressure` | `improved-v3` | `2.8750` | `14/1/1` | `42839` | `0.096` | `0.275` |
| `baseline-rnn` | `improved-v3` | `4.1875` | `16/0/0` | `34476` | `0.506` | `0.822` |
| `net-pressure` | `improved-v4` | `2.4375` | `12/1/3` | `42767` | `0.093` | `0.270` |
| `baseline-rnn` | `improved-v4` | `3.7500` | `16/0/0` | `40472` | `0.518` | `0.837` |
| `net-pressure` | `improved-v5` | `1.5625` | `12/3/1` | `48000` | `0.106` | `0.265` |
| `baseline-rnn` | `improved-v5` | `2.5625` | `14/0/2` | `45666` | `0.480` | `0.806` |
| `net-pressure` | `improved-v6` | `1.5625` | `12/3/1` | `48000` | `0.106` | `0.265` |
| `baseline-rnn` | `improved-v6` | `2.5625` | `14/0/2` | `45666` | `0.480` | `0.806` |

Terminal point buckets were similar in one important way: both policies mostly
win points with low front/net terminal states. The difference is conversion
rate. On this short subset, `baseline-rnn` won `74`, `67`, `45`, and `45`
points against `improved-v3..v6`, while `net-pressure` won `53`, `47`, `29`,
and `29`.

`net-pressure` terminal losses clustered in low-receive modes:

- against `improved-v3`: `grounded_low_receive=4`, `low_ball_rescue=2`,
  `late_contact_attack=1`;
- against `improved-v4`: `low_ball_rescue=4`, `grounded_low_receive=2`,
  `late_contact_attack=1`, `rear_wall_low_jump=1`;
- against `improved-v5/v6`: `low_ball_rescue=2`, `grounded_low_receive=1`,
  `late_contact_attack=1`.

Interpretation: the hard-opponent gap is not mainly that `net-pressure` loses
many more points. It wins too few points and remains much less active than the
RNN comparator. The obvious one-step fixes are risky because previous
front-net/low-receive probes already showed that broad jump overrides often
make built-in performance worse.

## Front-Net Conversion Probe

The first structural probe family tried narrower front-net and low-receive
conversion rules, all layered over `net-pressure`. These were no-ledger short
screens on `12000..12015`.

| Candidate | Built-in | improved-v3 | improved-v4 | improved-v5 | improved-v6 | Recommendation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `net-pressure` reference | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | reference |
| `front-net-guarded-drive` | `-0.4375` | `2.6250` | `2.0625` | `1.0625` | `1.0625` | reject |
| `front-net-rightward-block` | `-0.3750` | `1.6250` | `1.5000` | `-0.6250` | `-0.6250` | reject |
| `front-net-split-convert` | `-0.5000` | `1.4375` | `1.1875` | `-0.4375` | `-0.4375` | reject |
| `low-receive-floor-drive` | `0.0625` | `2.8750` | `2.4375` | `1.4375` | `1.4375` | reject; no gain |
| `post-attack-low-block` | `-0.0625` | `2.6250` | `2.3750` | `1.7500` | `1.7500` | reject; mixed and built-in regression |
| `baseline-rnn` comparator | `0.2500` | `4.1875` | `3.7500` | `2.5625` | `2.5625` | comparator |

`post-attack-low-block` is the only variant with a visible gain on the nearest
archives (`improved-v5/v6`), but it regressed built-in and `improved-v3`, and it
remained far below `baseline-rnn`. No policy edit is justified.

## Legal Brace-Action Probe

The RNN uses legal dual-horizontal actions such as `110` and `111` frequently,
while the transparent heuristic never emits them. A second probe tested whether
small, explicit brace-action macros could close the hard-opponent gap.

| Candidate | Built-in | improved-v3 | improved-v4 | improved-v5 | improved-v6 | Recommendation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `net-pressure` reference | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | reference |
| `brace-net-pressure` | `-0.3750` | `3.0000` | `2.2500` | `1.5000` | `1.5000` | reject; built-in regression |
| `brace-rally-serve` | `-0.1875` | `3.0625` | `2.5000` | `1.6250` | `1.6250` | reject; mixed and below RNN |
| `brace-low-front-contact` | `-1.8125` | `0.6875` | `0.1250` | `-1.7500` | `-1.5000` | reject |
| `brace-low-front-nojump` | `-0.6250` | `1.0625` | `0.5625` | `-0.6875` | `-0.6875` | reject |
| `brace-attack-pressure` | `-0.5000` | `2.1875` | `1.9375` | `1.1875` | `1.1875` | reject |
| `baseline-rnn` comparator | `0.2500` | `4.1875` | `3.7500` | `2.5625` | `2.5625` | comparator |

The best brace result was `brace-rally-serve`, which improved the short subset
against `improved-v3`, `improved-v4`, `improved-v5`, and `improved-v6`, but it
regressed built-in from `0.0625` to `-0.1875` and still trailed `baseline-rnn`
by a large margin on every hard archived opponent. This is not promotable.

## Contact-Quality Probe

The third probe family tested whether simple post-contact quality detectors
could recover low front/net opportunities without copying the RNN's broad jump
rate. These were also no-ledger short screens on `12000..12015`.

| Candidate | Built-in | improved-v3 | improved-v4 | improved-v5 | improved-v6 | Recommendation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `net-pressure` reference | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | reference |
| `outbound-clear-jump` | `0.0625` | `2.8750` | `2.4375` | `1.5000` | `1.5000` | reject; no gain |
| `outbound-recover-home` | `-1.5625` | `2.0000` | `1.6875` | `1.0625` | `1.0625` | reject |
| `outbound-forward-nojump` | `0.0625` | `2.8750` | `2.5625` | `1.3125` | `1.3125` | reject; mixed |
| `outbound-noop` | `-0.3750` | `2.6875` | `2.3750` | `1.8750` | `1.8750` | reject; built-in regression |
| `above-ball-clear-jump` | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | reject; no-op |
| `fast-outbound-clear-jump` | `-0.1250` | `2.8750` | `2.4375` | `1.5000` | `1.5000` | reject |
| `opponent-contact-aggressive` | `-0.5625` | `2.4375` | `2.1875` | `1.5000` | `1.5000` | reject |
| `baseline-rnn` comparator | `0.2500` | `4.1875` | `3.7500` | `2.5625` | `2.5625` | comparator |

`outbound-noop` improved the short subset against `improved-v5/v6`, and
`outbound-forward-nojump` slightly improved `improved-v4`, but both remained
below `baseline-rnn` and either regressed built-in or regressed nearby archived
opponents. The apparently more specific contact-quality signals are still not
specific enough for a kept policy edit.

## Failure Analysis

The trace data correctly identified a real behavior gap: the RNN is much more
active, especially with forward and jump actions, and converts more low
front/net opportunities into points. The tested one-step conversions and
contact-quality rules were too coarse. They often changed only a handful of
frames when narrowly guarded, or collapsed performance when broadened.

This reinforces earlier generation-4 evidence against naive front-net scoops
and single-branch low-receive overrides. The useful future direction is not to
copy the RNN's high jump rate directly. It needs a more specific multi-frame
contact-quality detector, likely using recent own-contact, ball velocity flip,
agent airborne state, and opponent recovery position to decide when a second
contact attempt is actually safe.

## Decision

Do not edit policy code from this diagnostic pass. Do not open generation-5
holdout. Keep `net-pressure` as a development-only probe and record these
front-net/brace attempts as failed or mixed directions.
