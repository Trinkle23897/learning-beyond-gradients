# Generation-5 Context-Reset Probe

Date: 2026-05-27

## Scope

This note records a development-only structural probe that tried to make the
teacher-derived reset macro context-sensitive. The prior fixed `serve_110_10`
macro helped some hard archived opponents but regressed the built-in row. This
probe asked whether a transparent previous-point phase detector could choose
when to use the `110` reset macro and keep the normal `net-pressure` reset
behavior elsewhere.

No maintained policy/config/test edit was promoted. No canonical ledger row was
appended. No generation-5 holdout seeds `13000..13049` and no generation-5
audit seeds `14000..14049` were used.

Artifacts:

- Probe script: `experiments/slimevolley/probes/g5_context_reset_probe.py`
- JSON result: `experiments/slimevolley/results/generation_5_context_reset_probe.json`

Seed use:

- Short screens: `12000..12015`
- Full fixed-pool checks: `12000..12049`

## Candidate Family

All candidates wrapped `net-pressure` and used a recent observation window to
classify the previous point context before a reset. The context labels were
`own_low_or_rear`, `rear_wall_terminal`, `opponent_low`, `any_low_terminal`, and
`non_terminal_high`.

The first screen is preserved as a failed attempt: the classifier only looked at
the last pre-reset frame, classified all reset events as `non_terminal_high`,
and therefore fired no macros. The corrected screen scanned the recent non-reset
window and produced active candidates.

## Corrected Short Screen

Seeds: `12000..12015`.

| Candidate | Built-in | improved-v3 | improved-v4 | improved-v5 | improved-v6 | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `net-pressure` reference | `0.0625`, `3/4/9` | `2.8750`, `14/1/1` | `2.4375`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | reference |
| `baseline-rnn` | `0.2500`, `7/3/6` | `4.1875`, `16/0/0` | `3.7500`, `16/0/0` | `2.5625`, `14/0/2` | `2.5625`, `14/0/2` | comparator |
| `ctx_own_low_110_10` | `0.1250`, `4/4/8` | `2.8125`, `14/1/1` | `2.4375`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | mixed |
| `ctx_own_low_110_6` | `0.0000`, `3/4/9` | `2.9375`, `15/1/0` | `2.5000`, `13/1/2` | `1.6250`, `12/3/1` | `1.6250`, `12/3/1` | mixed |
| `ctx_own_low_110_14` | `0.0000`, `3/5/8` | `2.8125`, `14/1/1` | `2.4375`, `12/1/3` | `1.5000`, `12/3/1` | `1.5000`, `12/3/1` | reject |
| `ctx_own_low_110_6_101_4` | `-0.0625`, `3/4/9` | `2.8750`, `15/1/0` | `2.5000`, `13/1/2` | `1.7500`, `13/2/1` | `1.7500`, `13/2/1` | full check |
| `ctx_opponent_low_110_10` | `0.0625`, `3/4/9` | `2.7500`, `13/1/2` | `2.8125`, `13/1/2` | `1.7500`, `13/2/1` | `1.7500`, `13/2/1` | mixed |
| `ctx_any_low_110_10` | `0.1875`, `5/4/7` | `2.7500`, `13/1/2` | `2.8125`, `13/1/2` | `1.7500`, `13/2/1` | `1.7500`, `13/2/1` | full check |
| `ctx_rear_wall_110_10` | `0.0625`, `3/4/9` | `2.8750`, `14/1/1` | `2.4375`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | inert |

## Full Development Check

Seeds: `12000..12049`.

| Opponent | `net-pressure` | `baseline-rnn` | `ctx_any_low_110_10` | `ctx_own_low_110_6_101_4` |
| --- | ---: | ---: | ---: | ---: |
| `builtin` | `-0.06`, `11/14/25` | `-0.18`, `18/19/13` | `-0.02`, `13/13/24` | `-0.10`, `10/13/27` |
| `random` | `4.90`, `50/0/0` | `4.88`, `50/0/0` | `4.90`, `50/0/0` | `4.90`, `50/0/0` |
| `initial` | `4.86`, `50/0/0` | `4.86`, `50/0/0` | `4.82`, `50/0/0` | `4.86`, `50/0/0` |
| `improved-v0` | `4.84`, `50/0/0` | `4.86`, `50/0/0` | `4.82`, `50/0/0` | `4.84`, `50/0/0` |
| `improved-v2` | `4.68`, `50/0/0` | `4.80`, `50/0/0` | `4.64`, `50/0/0` | `4.68`, `50/0/0` |
| `improved-v3` | `3.08`, `48/1/1` | `4.24`, `49/0/1` | `3.00`, `46/2/2` | `3.08`, `48/1/1` |
| `improved-v4` | `2.56`, `45/2/3` | `3.70`, `48/0/2` | `2.56`, `44/3/3` | `2.56`, `45/2/3` |
| `improved-v5` | `1.20`, `34/7/9` | `2.38`, `43/1/6` | `1.16`, `34/5/11` | `1.24`, `35/7/8` |
| `improved-v6` | `1.22`, `34/7/9` | `2.40`, `43/1/6` | `1.20`, `34/5/11` | `1.26`, `35/7/8` |

## Failure Analysis

The context detector is active after the window fix, and it produced a real but
mixed signal. `ctx_any_low_110_10` improved the built-in full-development mean
from `-0.06` to `-0.02`, the best generation-5 built-in development row so far
among the transparent probes. It also still beat `baseline-rnn` on the built-in
mean (`-0.02` versus `-0.18`).

The fixed-pool result rejects promotion. `ctx_any_low_110_10` regressed
`initial`, `improved-v0`, `improved-v2`, `improved-v3`, `improved-v5`, and
`improved-v6` relative to `net-pressure`, tied only `random` and `improved-v4`,
and remained far below `baseline-rnn` on the hard archived rows.

`ctx_own_low_110_6_101_4` preserved most reference rows and improved
`improved-v5/v6` by `+0.04`, but it regressed built-in to `-0.10` and did not
close the hard-opponent neural gap. This makes it useful as a local diagnostic,
not as a maintained policy candidate.

The failed first screen is also informative: context tied to only the last
pre-reset frame was too weak because the environment presents high reset-like
frames before the detector fires. Any future reset phase must use a short
history window or explicit episode diagnostics, not a single previous frame.

## Decision

Do not promote a maintained policy/config/test edit from this pass. Do not open
generation-5 holdout or audit seeds.

The next direction should move beyond reset macros and model rally setup over a
longer horizon. The evidence suggests that reset behavior can trade built-in and
hard archived performance, but it does not explain the large `baseline-rnn`
advantage against `improved-v3` through `improved-v6`.
