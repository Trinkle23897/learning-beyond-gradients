# Generation-4 Stacked Low-Receive Probe

Date: 2026-05-27

## Scope

This was a development-only probe for a narrow stacked-frame low-receive
classifier after the parallel4 synthesis identified low own-side contact-like
states as the most plausible remaining structural direction.

No maintained policy was changed. No canonical ledger row was appended. No
holdout, audit, or final-eval seeds were used.

Artifacts:

- Probe script: `experiments/slimevolley/probes/g4_stacked_low_receive_probe.py`
- JSON result: `experiments/slimevolley/results/generation_4_stacked_low_receive_probe.json`

Seed use:

- Short screen: `9000..9015`
- Full fixed-pool check: `9000..9049`
- Holdout `10000..10049`: not used
- Audit `11000..11049`: not used

## Candidate Definitions

All candidates were structural/history probes layered on the existing
`post-contact` development candidate. They used 2-5 recent observations to
detect own-contact-like velocity flips and low own-side geometry before
overriding the current action.

The screen included:

- `stacked_front_101_tight`: tight low-front post-contact gate, force `101`.
- `stacked_low_101_wide`: wider low own-side post-contact gate, force `101`.
- `stacked_front_111_tight`: same tight gate, force `111`.
- `stacked_front_110_tight`: same tight gate, force `110`.
- `stacked_mode_rewrite_101`: rewrite existing low-receive modes to `101`.
- `stacked_split_front_rear`: front `101` conversion plus rear `110` brace.

The first run failed before candidate rows because the probe helper method
collided with the inherited `SlimeVolleyPostContactPolicy._recent_own_contact`
integer field. The probe script was fixed by renaming the helper to
`_has_recent_own_contact`, then the same development-only screen was rerun.

## Short Screen

Seeds: `9000..9015`. Opponents: `builtin`, `improved-v4`, `improved-v5`,
`improved-v6`.

| Candidate | Built-in | improved-v4 | improved-v5 | improved-v6 | Decision |
| --- | --- | --- | --- | --- | --- |
| `post_contact_reference` | `0.3125`, `4/0/12`, `48000` | `2.7500`, `15/0/1`, `44527` | `1.3125`, `9/3/4`, `47686` | `1.3750`, `9/3/4`, `47686` | reference |
| `baseline_rnn` | `0.1250`, `6/4/6`, `48000` | `3.2500`, `16/0/0`, `40985` | `2.3125`, `14/1/1`, `46353` | `2.5625`, `14/1/1`, `45819` | neural comparator |
| `stacked_front_101_tight` | `0.3125`, `4/0/12`, `48000` | `2.7500`, `15/0/1`, `44527` | `1.3125`, `9/3/4`, `47686` | `1.3750`, `9/3/4`, `47686` | inert |
| `stacked_low_101_wide` | `0.3125`, `4/0/12`, `48000` | `2.7500`, `15/0/1`, `44527` | `1.4375`, `10/3/3`, `47686` | `1.5000`, `10/3/3`, `47686` | full check |
| `stacked_front_111_tight` | `0.2500`, `4/1/11`, `48000` | `2.5625`, `15/0/1`, `44633` | `1.1250`, `9/3/4`, `48000` | `1.1875`, `9/3/4`, `48000` | reject |
| `stacked_front_110_tight` | `0.2500`, `4/1/11`, `48000` | `2.5625`, `15/0/1`, `44633` | `1.1250`, `9/3/4`, `48000` | `1.1875`, `9/3/4`, `48000` | reject |
| `stacked_mode_rewrite_101` | `0.3125`, `4/0/12`, `48000` | `2.7500`, `15/0/1`, `44527` | `1.3125`, `9/3/4`, `47686` | `1.3750`, `9/3/4`, `47686` | inert |
| `stacked_split_front_rear` | `0.1250`, `3/2/11`, `48000` | `2.5000`, `13/0/3`, `44644` | `1.0625`, `8/4/4`, `47686` | `1.1250`, `8/4/4`, `47686` | reject |

`stacked_low_101_wide` was the only screened candidate that preserved built-in
and improved the hard-tail archived rows, so it was expanded to the full fixed
development pool.

## Full Fixed-Pool Check

Seeds: `9000..9049`. Opponents: `builtin`, `random`, `initial`,
`improved-v0`, `improved-v2`, `improved-v3`, `improved-v4`, `improved-v5`,
`improved-v6`.

| Opponent | `post-contact` | `baseline-rnn` | `stacked_low_101_wide` | Candidate delta vs post-contact |
| --- | ---: | ---: | ---: | ---: |
| `builtin` | `0.14`, `13/8/29`, `150000` | `0.12`, `18/12/20`, `150000` | `0.04`, `12/10/28`, `150000` | `-0.10` |
| `random` | `4.74`, `50/0/0`, `38217` | `4.80`, `50/0/0`, `30603` | `4.74`, `50/0/0`, `38217` | `0.00` |
| `initial` | `4.68`, `50/0/0`, `44634` | `4.76`, `50/0/0`, `34004` | `4.68`, `50/0/0`, `44634` | `0.00` |
| `improved-v0` | `4.70`, `50/0/0`, `43242` | `4.82`, `50/0/0`, `32843` | `4.70`, `50/0/0`, `43242` | `0.00` |
| `improved-v2` | `4.38`, `49/1/0`, `76391` | `4.80`, `50/0/0`, `54551` | `4.38`, `49/1/0`, `76391` | `0.00` |
| `improved-v3` | `3.04`, `48/0/2`, `137816` | `3.84`, `50/0/0`, `118182` | `3.04`, `48/0/2`, `137816` | `0.00` |
| `improved-v4` | `2.40`, `44/0/6`, `143709` | `3.26`, `48/0/2`, `132511` | `2.40`, `44/0/6`, `143709` | `0.00` |
| `improved-v5` | `1.22`, `32/7/11`, `149402` | `2.10`, `42/2/6`, `145370` | `1.26`, `33/7/10`, `149402` | `+0.04` |
| `improved-v6` | `1.28`, `32/7/11`, `149402` | `2.18`, `42/2/6`, `144837` | `1.32`, `33/7/10`, `149402` | `+0.04` |

## Failure Analysis

The short-screen hard-tail gain did not survive the full-pool promotion gate.
`stacked_low_101_wide` slightly improved `improved-v5` and `improved-v6`, but
it regressed the built-in row from `0.14` to `0.04` and fell below
`baseline-rnn` on the same built-in development seeds (`0.12`).

The candidate also remained far below `baseline-rnn` on every hard archived
row. Its extra `101` conversions are too broad: they rescue a few late
archived exchanges but add enough built-in losses to fail the main comparator
condition.

The `110` and `111` variants were worse on the short screen. The RNN's use of
those actions is therefore not directly transferable as a local action-copying
rule.

## Decision

Do not promote `stacked_low_101_wide` or any screened stacked low-receive
candidate.

This is useful negative evidence. The remaining gap is more likely a higher
level rally-phase or setup problem than a terminal low-receive action override.
Any further work should predeclare a fresh development protocol or use
generation-5 development context, because generation-4 holdout has already
been consumed as final-only evidence.
