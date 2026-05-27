# Generation-5 Planner-Takeover Probe

Date: 2026-05-27

## Scope

This note records a development-only structural probe proposed by a sidecar
critic subagent after the position/posture screen. The hypothesis was that
`net-pressure` loses hard archived-opponent points because it reaches poor
intercept geometry before the terminal low-contact state. Instead of changing
the final action, the probe let the transparent physics planner briefly take
over on earlier intercept states.

Only generation-5 development seeds were used. The screen used exactly
`12000..12015`. No generation-5 holdout seeds `13000..13049` and no audit seeds
`14000..14049` were used. No canonical ledger row was appended and no maintained
policy/config/test edit was promoted.

Artifacts:

- Probe script: `experiments/slimevolley/probes/g5_planner_takeover_probe.py`
- JSON result: `experiments/slimevolley/results/generation_5_planner_takeover_probe.json`

## Candidate Definitions

All candidates wrap `SlimeVolleyNetPressurePolicy` and instantiate a separate
`SlimeVolleyPlannerPolicy` as a transparent advisor. When a candidate fires, it
uses the planner action for a short three-frame takeover; otherwise it keeps the
base `net-pressure` action.

| Candidate | Type | Definition |
| --- | --- | --- |
| `planner_takeover_safe` | structural/planner | Three-frame takeover on planner intercept/net-clearance states with `ball_vx > 0`, `time_to_floor <= 0.22`, no wall bounce, and predicted intercept in `[0.35, 1.75]`. |
| `planner_takeover_strict` | structural/planner | Stricter `time_to_floor <= 0.18`, predicted intercept in `[0.45, 1.55]`, and planner jump required. |
| `planner_takeover_netclear` | structural/planner | Takeover only for low predicted net-clearance guard states. |
| `planner_takeover_grounded` | structural/planner | Safe takeover plus grounded-agent requirement. |
| `planner_takeover_wide` | structural/planner | Wider `time_to_floor <= 0.30`, predicted intercept in `[0.24, 1.95]`. |

## Short Screen Results

Rows use seeds `12000..12015`.

| Candidate | Built-in | improved-v3 | improved-v4 | improved-v5 | improved-v6 | Fired / Changed | Recommendation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `net_pressure_reference` | `0.0625`, `3/4/9` | `2.8750`, `14/1/1` | `2.4375`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | `0 / 0` | reference |
| `baseline_rnn` | `0.2500`, `7/3/6` | `4.1875`, `16/0/0` | `3.7500`, `16/0/0` | `2.5625`, `14/0/2` | `2.5625`, `14/0/2` | `0 / 0` | comparator |
| `planner_takeover_safe` | `-2.1250`, `2/13/1` | `1.6250`, `9/4/3` | `1.3125`, `10/5/1` | `-0.6250`, `4/8/4` | `-0.6250`, `4/8/4` | built-in `15 / 14` | reject |
| `planner_takeover_strict` | `0.0625`, `3/4/9` | `2.8750`, `14/1/1` | `2.4375`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | `0 / 0` | reject; inert |
| `planner_takeover_netclear` | `0.0625`, `3/4/9` | `2.8750`, `14/1/1` | `2.4375`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | `0 / 0` | reject; inert |
| `planner_takeover_grounded` | `-2.1250`, `2/13/1` | `1.6250`, `9/4/3` | `1.3125`, `10/5/1` | `-0.6250`, `4/8/4` | `-0.6250`, `4/8/4` | built-in `15 / 14` | reject |
| `planner_takeover_wide` | `-4.5000`, `0/16/0` | `-2.2500`, `3/13/0` | `-2.3750`, `3/13/0` | `-4.1875`, `0/16/0` | `-4.1875`, `0/16/0` | built-in `41 / 37` | reject |

## Failure Analysis

The planner-takeover hypothesis failed strongly. The exact safe/grounded gates
were active but fired only a few opportunities and caused large score collapses.
The strict and net-clearance gates were outcome-neutral because they never
fired. The wide gate fired more often but catastrophically regressed every row.

This is useful negative evidence for the planner handoff interface: the planner
action is not a safe local substitute for `net-pressure` even when physics
features identify plausible early intercept geometry. The failure suggests that
the hard-opponent gap is not solved by briefly replacing the controller with the
existing planner. A future phase controller would need to be designed
holistically rather than inserted as a short takeover.

## Decision

Do not run a full development pool, holdout, or audit evaluation from this
screen. Do not promote a maintained policy/config/test edit.
