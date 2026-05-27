# Generation-4 Post-Contact Gate Probe

Date: 2026-05-27

## Scope

This was a development-only follow-up to the generation-4 v2 parallel synthesis
hypothesis. A transient probe script evaluated short-history post-contact gates
around the current `rally-serve` policy. No maintained policy, test, ledger,
summary, holdout, or audit behavior was edited during the run. After the run,
the front-conversion candidate was preserved as the explicit `post-contact`
policy for auditability. It is labeled development-only, is not the promoted
policy, and has no holdout or audit validation.

Artifacts:

- Probe script: `experiments/slimevolley/probes/g4_post_contact_gate_probe.py`
- Result JSON: `experiments/slimevolley/results/generation_4_post_contact_gate_probe.json`

Seed usage:

- Screen: fixed development seeds `9000..9015`
- Full development pool: fixed development seeds `9000..9049`
- No generation-4 holdout `10000..10049` or audit `11000..11049` seeds were used.
- No generation-5 holdout `13000..13049` or audit `14000..14049` seeds were used.

Cost accounting from the JSON artifact:

| Phase | Rows | Episodes | Environment steps |
| --- | ---: | ---: | ---: |
| Screen | 21 | 336 | 977758 |
| Full development pool | 63 | 3150 | 6443935 |
| Total | 84 | 3486 | 7421693 |

The probe script did not instrument wall-clock time. Based on local artifact
monitoring, the script was written at `2026-05-27 01:02:40 -0400` and the final
JSON write occurred at `2026-05-27 01:14:01 -0400`; exact subprocess start time
was not recorded.

## Candidate Definitions

All structural candidates wrapped `rally-serve` and used short ball-history
signals. They were intentionally kept outside the maintained policy module.

| Candidate | Type | Definition |
| --- | --- | --- |
| `rally_reference` | reference | Current `rally-serve` behavior. |
| `baseline_rnn` | neural comparator | Packaged SlimeVolley RNN comparator. |
| `pc_gate_grounded_low_receive` | structural/history | Restore the low-rescue jump gate when `grounded_low_receive` fires without two-frame post-contact low evidence. |
| `pc_gate_low_receive_and_late_guard` | structural/history | Apply the same gate to both `grounded_low_receive` and `late_low_ball_guard`. |
| `pc_front_conversion` | structural/history | Near-net post-contact detector that tries forward+jump conversion after recent contact-like velocity flips. |
| `pc_outbound_recover` | structural/history | Recover toward defensive home after recent own-contact outbound low balls. |
| `pc_conservative_combined` | structural/history | Conservative grounded-low gate plus a narrower front-conversion detector. |

## Screen Results

Screen opponents were `builtin`, `improved-v4`, and `improved-v6` on seeds
`9000..9015`.

| Candidate | Built-in mean / W-L-D | Improved-v4 mean / W-L-D | Improved-v6 mean / W-L-D | Override frames |
| --- | --- | --- | --- | ---: |
| `rally_reference` | `0.3125` / `4-0-12` | `2.5625` / `15-0-1` | `1.1875` / `9-3-4` | 0 |
| `baseline_rnn` | `0.1250` / `6-4-6` | `3.2500` / `16-0-0` | `2.5625` / `14-1-1` | 0 |
| `pc_gate_grounded_low_receive` | `0.3125` / `4-0-12` | `2.5625` / `15-0-1` | `1.1875` / `9-3-4` | 19 |
| `pc_gate_low_receive_and_late_guard` | `0.3125` / `4-0-12` | `2.5625` / `15-0-1` | `1.1875` / `9-3-4` | 21 |
| `pc_front_conversion` | `0.3125` / `4-0-12` | `2.7500` / `15-0-1` | `1.3750` / `9-3-4` | 38 |
| `pc_outbound_recover` | `0.2500` / `4-1-11` | `2.5625` / `15-0-1` | `1.1875` / `9-3-4` | 19 |
| `pc_conservative_combined` | `0.3125` / `4-0-12` | `2.7500` / `15-0-1` | `1.3750` / `9-3-4` | 39 |

The front-conversion variants looked promising on archived short screens, but
neither improved the built-in short screen and both remained well below
`baseline_rnn` on `improved-v4` and `improved-v6`.

## Full Development Results

Full-pool rows used seeds `9000..9049` against `builtin`, `random`, `initial`,
`improved-v0`, `improved-v2`, `improved-v3`, `improved-v4`, `improved-v5`, and
`improved-v6`. The table below shows the built-in row and the harder archived
tail where the RNN gap matters most.

| Candidate | Built-in | Improved-v3 | Improved-v4 | Improved-v5 | Improved-v6 | Override frames on shown rows |
| --- | --- | --- | --- | --- | --- | ---: |
| `rally_reference` | `0.1400`, `13-8-29` | `2.9800`, `48-0-2` | `2.3400`, `44-0-6` | `1.1600`, `32-7-11` | `1.2200`, `32-7-11` | 0 |
| `baseline_rnn` | `0.1200`, `18-12-20` | `3.8400`, `50-0-0` | `3.2600`, `48-0-2` | `2.1000`, `42-2-6` | `2.1800`, `42-2-6` | 0 |
| `pc_gate_grounded_low_receive` | `0.1400`, `13-8-29` | `2.9800`, `48-0-2` | `2.3400`, `44-0-6` | `1.1600`, `32-7-11` | `1.2200`, `32-7-11` | 94 |
| `pc_gate_low_receive_and_late_guard` | `0.1400`, `13-8-29` | `2.9800`, `48-0-2` | `2.3400`, `44-0-6` | `1.1600`, `32-7-11` | `1.2200`, `32-7-11` | 100 |
| `pc_front_conversion` | `0.1400`, `13-8-29` | `3.0400`, `48-0-2` | `2.4000`, `44-0-6` | `1.2200`, `32-7-11` | `1.2800`, `32-7-11` | 184 |
| `pc_outbound_recover` | `0.1200`, `13-9-28` | `2.9800`, `48-0-2` | `2.3400`, `44-0-6` | `1.1600`, `32-7-11` | `1.2200`, `32-7-11` | 65 |
| `pc_conservative_combined` | `0.1400`, `13-8-29` | `3.0400`, `48-0-2` | `2.4000`, `44-0-6` | `1.2200`, `32-7-11` | `1.2800`, `32-7-11` | 166 |

## Failure Analysis

The post-contact gates were auditable and interpretable, but they did not clear
the promotion bar. The grounded-low gates changed actions without moving any
reported score row. `pc_outbound_recover` regressed the built-in row from
`0.1400` to `0.1200` by adding one loss.

The two front-conversion variants produced the only positive signal: they tied
built-in development performance and improved the harder archived tail by
`+0.06` mean on `improved-v3`, `improved-v4`, `improved-v5`, and
`improved-v6`. However, those gains did not change W-L-D counts on the shown
archived rows, did not improve the built-in comparator row, and still trailed
`baseline_rnn` by a large margin on every hard archived opponent. Promoting from
that pattern would overstate the evidence.

## Decision

Do not promote any post-contact gate candidate.

The result is useful negative evidence. Short-history contact signals can find
a small point-differential improvement against archived heuristic opponents,
but this implementation does not improve the primary built-in development row
and does not close the neural-comparator gap on the harder fixed pool.

Next hypothesis, if continued: trace the exact point events changed by
`pc_front_conversion` and `pc_conservative_combined` to determine whether the
`+0.06` archived mean comes from repeatable contact conversion or incidental
point-differential noise. Keep that as development-only analysis unless it
improves the built-in row and the hard archived rows together.
