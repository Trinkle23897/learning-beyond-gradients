# Generation-5 Stacked Followthrough And Posture Probe

Date: 2026-05-27

## Scope

This note records development-only probes after the generation-5 fixed-pool rows showed that `net-pressure` beats `baseline-rnn` on the built-in development row but remains behind on hard archived opponents.

All screens used generation-5 development seeds only. Short screens used `12000..12015`; the single best posture-gated candidate was then checked on the full development fixed pool `12000..12049`. No generation-5 holdout seeds `13000..13049` and no audit seeds `14000..14049` were used. No canonical ledger rows were appended and no maintained policy/config/test edit was promoted.

## Diagnosis

Ledger analysis of `net-pressure` against `improved-v3` through `improved-v6` showed most point losses in low front-court states, while trace inspection of seed `12025` against `improved-v5` showed the RNN repeatedly staying near the net and issuing `101` on low opponent-side states before winning points. This suggested two hypotheses:

1. A narrow front-low recovery override might prevent overcommitted `100/101` losses.
2. A stacked-frame followthrough or opponent-posture gate might add only the safe part of the RNN-like low opponent-side pressure.

## Front-Low Recovery Screen

Transient wrappers around `net-pressure` replaced overcommitted low front-court actions with hold or rearward actions when the ball was already low near the net.

| Candidate family | Seeds | Result | Recommendation |
| --- | --- | --- | --- |
| `front_low_hold_jump`, `front_low_hold_nojump`, `front_low_rear_jump`, `front_low_rear_nojump` | `12000..12015` | Built-in stayed at `0.0625`, but hard rows were unchanged or slightly worse; `improved-v3` fell from `2.8750` to `2.7500` for several variants. | Reject. |
| `stacked_front_low_hold_jump`, `stacked_front_low_rear_jump` | `12000..12015` | Stacked gates reduced trigger count but did not improve `improved-v5` or `improved-v6`; both stayed at `1.5625`. | Reject. |

Failure analysis: the terminal low front-court state is too late to repair by changing only the final local action. The issue is earlier contact quality and positioning, not a simple final-frame action replacement.

## Opponent-Side Low Pressure Screen

Transient wrappers then forced `101` for low balls already on the opponent side. Broad versions were unsafe, but one direction was partially useful.

| Candidate | Built-in | improved-v3 | improved-v4 | improved-v5 | improved-v6 | Recommendation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `net-pressure` reference | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | reference |
| `baseline-rnn` reference | `0.2500` | `4.1875` | `3.7500` | `2.5625` | `2.5625` | comparator |
| broad opponent-low pressure | `-0.0625` | `2.0000` | `1.8750` | `0.5625` | `0.5625` | reject |
| continuing-ball pressure (`ball_vx < -0.15`) | `-0.2500` | `2.7500` | `2.6250` | `2.0000` | `2.0000` | mixed; hard gain with built-in regression |
| low-height preserving gate (`ball_y <= 0.42`) | `0.0625` | not screened | `2.4375` | `1.6875` | `1.6875` | too small |

Failure analysis: forcing `101` after the ball is already on the opponent side can improve the hard archived rows, but broad gates damage the built-in row and narrow gates produce only small gains.

## Stacked Followthrough Screen

The next probe used stacked-frame event detectors: a crossing detector, a velocity-flip detector, and an either-detector started a short followthrough timer, then issued `101` only while the ball was low on the opponent side.

All variants preserved the reference short-screen table exactly: built-in `0.0625`, `improved-v3` `2.8750`, `improved-v4` `2.4375`, `improved-v5` `1.5625`, and `improved-v6` `1.5625`. Trigger counts changed, but scores did not. This is negative evidence for a timer-only followthrough macro.

## Opponent-Posture Gate

The best short-screen posture gate used the continuing-ball pressure rule only when the opponent was low (`opponent_y <= 0.20`) and the ball was below `0.54`.

Short-screen result on `12000..12015`:

| Candidate | Built-in | improved-v4 | improved-v5 | improved-v6 |
| --- | ---: | ---: | ---: | ---: |
| `net-pressure` reference | `0.0625` | `2.4375` | `1.5625` | `1.5625` |
| posture-gated continuing low pressure | `0.0625` | `2.6250` | `1.8125` | `1.8125` |

Full development fixed-pool no-ledger check on `12000..12049`:

| Opponent | Mean | W/L/D | Steps | Overrides |
| --- | ---: | --- | ---: | ---: |
| built-in | `-0.0200` | `11/14/25` | `150000` | `166` |
| random | `4.9000` | `50/0/0` | `38968` | `58` |
| initial | `4.8600` | `50/0/0` | `46153` | `367` |
| improved-v0 | `4.8400` | `50/0/0` | `45461` | `369` |
| improved-v2 | `4.5600` | `50/0/0` | `71811` | `319` |
| improved-v3 | `3.0600` | `47/1/2` | `140453` | `514` |
| improved-v4 | `2.5600` | `45/3/2` | `142940` | `537` |
| improved-v5 | `1.3200` | `34/5/11` | `149883` | `633` |
| improved-v6 | `1.3600` | `34/5/11` | `149011` | `640` |

Compared with the existing full-development `net-pressure` rows, this candidate only improved `improved-v5` by `+0.12` and `improved-v6` by `+0.14`, while regressing `improved-v2` by `-0.12` and `improved-v3` by `-0.02`. It still remained far below `baseline-rnn` on the hard archived rows.

## Decision

Do not promote a policy/config/test edit from this pass. The useful signal is that opponent-side continuing low pressure can move the hard archived rows, but the current gates are too weak and too opponent-pool fragile. The next credible direction should model earlier contact setup or a higher-level rally phase, not final-frame front-low recovery, timer-only followthrough, or broad opponent-side pressure.
