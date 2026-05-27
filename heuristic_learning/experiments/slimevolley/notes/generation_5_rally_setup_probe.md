# Generation-5 Rally-Setup Probe

Date: 2026-05-27

## Scope

This note records a development-only structural/history probe that tested
whether the `net-pressure` gap to `baseline-rnn` on hard archived opponents is
caused by pre-contact positioning rather than final-frame action choice.

The candidates wrapped `net-pressure` with an explicit post-own-contact setup
phase. After a detected ball velocity flip near the agent, the policy briefly
held a front-court anchor (`x=0.35` or `x=0.50`) while the ball was still moving
away from the agent. Two variants also allowed a low opponent-side `101`
pressure action during that setup phase.

No maintained policy/config/test edit was promoted. No canonical ledger row was
appended. No generation-5 holdout seeds `13000..13049` and no generation-5
audit seeds `14000..14049` were used.

Artifacts:

- Probe script: `experiments/slimevolley/probes/g5_rally_setup_probe.py`
- JSON result: `experiments/slimevolley/results/generation_5_rally_setup_probe.json`

Seed use:

- Short screen: `12000..12015`
- Full fixed-pool check: not run, because no candidate improved the hard
  archived short-screen rows while preserving the reference.

## Candidate Family

All candidates are structural/history probes because they add a named phase
detector and front-court setup mode:

- `setup_anchor_035_10`: after own contact, move toward front anchor `x=0.35`
  for up to `10` frames.
- `setup_anchor_050_14`: after own contact, move toward safer front anchor
  `x=0.50` for up to `14` frames.
- `setup_anchor_035_pressure`: `setup_anchor_035_10` plus low opponent-side
  pressure.
- `setup_anchor_050_pressure`: `setup_anchor_050_14` plus low opponent-side
  pressure.

## Short Screen

Seeds: `12000..12015`.

| Candidate | Built-in | improved-v3 | improved-v4 | improved-v5 | improved-v6 | Aggregate steps | Anchor/pressure frames |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `net_pressure_reference` | `0.0625`, `3/4/9` | `2.8750`, `14/1/1` | `2.4375`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | `229606` | `0/0` |
| `baseline_rnn` | `0.2500`, `7/3/6` | `4.1875`, `16/0/0` | `3.7500`, `16/0/0` | `2.5625`, `14/0/2` | `2.5625`, `14/0/2` | `214280` | `0/0` |
| `setup_anchor_035_10` | `0.0625`, `3/4/9` | `2.7500`, `13/1/2` | `2.3750`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | `229606` | `153/0` |
| `setup_anchor_050_14` | `0.0625`, `3/4/9` | `2.6875`, `13/1/2` | `2.3125`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | `229606` | `308/0` |
| `setup_anchor_035_pressure` | `0.0625`, `3/4/9` | `2.7500`, `13/1/2` | `2.3750`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | `229606` | `137/16` |
| `setup_anchor_050_pressure` | `0.0625`, `3/4/9` | `2.4375`, `13/1/2` | `2.3750`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | `230050` | `288/20` |

## Failure Analysis

The setup phase was active, but it did not improve the target hard rows. The
front anchor preserved the built-in short screen but regressed `improved-v3`
and `improved-v4`, while leaving `improved-v5/v6` unchanged. Adding low
opponent-side pressure during the setup phase fired only a few frames and did
not improve any hard archived score.

This weakens the hypothesis that a simple post-contact front anchor is enough
to reproduce the RNN's hard-opponent advantage. The RNN likely benefits from a
more continuous controller over approach, jump timing, and contact angle rather
than from only being closer to the net after own contact.

## Decision

Do not promote any rally-setup candidate. Do not run full fixed-pool or holdout
checks for this family.

The next direction should use paired traces to identify contact setup earlier
than the velocity-flip event, or explicitly model jump timing/contact geometry
over several frames instead of adding another short post-contact macro.
