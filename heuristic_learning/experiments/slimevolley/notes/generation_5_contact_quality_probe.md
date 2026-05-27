# Generation-5 Contact-Quality Probe

Date: 2026-05-27

## Protocol

This was a development-only structural/history probe around the current
`net-pressure` candidate. It tested whether short-history contact-quality gates
or RNN-like brace actions could improve hard archived-opponent robustness
without losing the built-in advantage.

Only generation-5 development seeds were used. The short screen used exactly
`12000..12015`. No generation-5 holdout seeds `13000..13049` and no
generation-5 audit seeds `14000..14049` were used.

The probe script is:

`experiments/slimevolley/probes/g5_contact_quality_probe.py`

The JSON artifact is:

`experiments/slimevolley/results/generation_5_contact_quality_probe.json`

No maintained policy, config, test, canonical ledger, holdout, or audit artifact
was changed by the probe.

## Candidate Definitions

All probe candidates wrap `SlimeVolleyNetPressurePolicy`.

| Candidate | Type | Definition |
| --- | --- | --- |
| `net_pressure_reference` | reference | Current generation-5 `net-pressure` structural probe. |
| `baseline_rnn` | neural comparator | Packaged SlimeVolley RNN comparator; not a maintained heuristic. |
| `quality_gate_recent_opp` | structural/history | Apply front pressure only when a short-history opponent-contact detector fired. |
| `quality_gate_no_recent_own` | structural/history | Suppress front pressure immediately after own-contact evidence. |
| `quality_two_frame_descent` | structural/history | Apply front pressure only after a stricter two-frame front-court descent. |
| `quality_brace_110` | structural/history/action | Replace risky pressure with both-direction no-jump `110` when quality is low. |
| `quality_brace_111` | structural/history/action | Replace risky pressure with both-direction jump `111` when quality is low. |
| `quality_recover_noop` | structural/history/action | Suppress risky pressure after own contact and hold `000`. |

## Short Screen Results

Rows use seeds `12000..12015`.

| Candidate | Built-in | improved-v3 | improved-v4 | improved-v5 | improved-v6 | Frames / overrides / suppressed |
| --- | --- | --- | --- | --- | --- | --- |
| `net_pressure_reference` | `0.0625`, `3/4/9` | `2.8750`, `14/1/1` | `2.4375`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | `0 / 0 / 0` |
| `baseline_rnn` | `0.2500`, `7/3/6` | `4.1875`, `16/0/0` | `3.7500`, `16/0/0` | `2.5625`, `14/0/2` | `2.5625`, `14/0/2` | comparator |
| `quality_gate_recent_opp` | `-0.3125`, `1/6/9` | `2.9375`, `15/0/1` | `2.4375`, `14/1/1` | `1.5625`, `13/1/2` | `1.5625`, `13/1/2` | built-in `49 / 0 / 49` |
| `quality_gate_no_recent_own` | `0.1250`, `4/4/8` | `2.6250`, `13/2/1` | `2.1250`, `11/2/3` | `1.6875`, `13/2/1` | `1.6875`, `13/2/1` | built-in `58 / 52 / 6` |
| `quality_two_frame_descent` | `-0.1250`, `4/4/8` | `2.4375`, `12/2/2` | `2.1875`, `12/2/2` | `1.5625`, `12/2/2` | `1.5625`, `12/2/2` | built-in `52 / 44 / 8` |
| `quality_brace_110` | `-0.0625`, `4/4/8` | `2.3125`, `12/2/2` | `2.1250`, `12/2/2` | `1.5625`, `12/2/2` | `1.5625`, `12/2/2` | built-in `51 / 51 / 0` |
| `quality_brace_111` | `-0.1875`, `3/4/9` | `2.3125`, `12/2/2` | `2.1250`, `12/2/2` | `1.6875`, `13/1/2` | `1.6875`, `13/1/2` | built-in `51 / 51 / 0` |
| `quality_recover_noop` | `-0.0625`, `4/4/8` | `2.3125`, `12/2/2` | `2.1250`, `12/2/2` | `1.5625`, `12/2/2` | `1.5625`, `12/2/2` | built-in `51 / 51 / 0` |

## Failure Analysis

The contact-quality gates were active enough to matter but not precise enough
to promote. `quality_gate_recent_opp` showed that suppressing all pressure
without recent opponent-contact evidence can improve `improved-v3` slightly,
but it collapsed the built-in row from `0.0625` to `-0.3125`.

The two best hard-tail nudges were `quality_gate_no_recent_own` and
`quality_brace_111`, each moving `improved-v5/v6` from `1.5625` to `1.6875`.
Both still remained far below the `baseline_rnn` short-screen value `2.5625`
and both regressed other rows. `quality_gate_no_recent_own` regressed
`improved-v3` and `improved-v4`; `quality_brace_111` regressed built-in,
`improved-v3`, and `improved-v4`.

The `110`/`111` brace actions were not enough by themselves. They changed
around fifty built-in frames, but mostly traded robust front pressure for extra
loss exposure. This weakens the hypothesis that the hard-opponent gap can be
closed by copying RNN-like brace actions under a simple contact-quality gate.

## Promotion Recommendation

Do not promote any candidate from this pass and do not run a full development
pool or holdout/audit evaluation from these rows.

This is useful negative evidence: a contact-quality detector is still a
plausible direction, but it needs a more specific state model than recent
contact, descent count, or raw `110`/`111` action substitution.
