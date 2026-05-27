# Generation-4 Parallel6 Archived-Opponent Robustness

Worker: E
Date: 2026-05-27

## Scope

This is a generation-4 development-only robustness note. It uses fixed
development seeds only and does not use holdout or audit results as evidence.
No maintained source, policy, test, ledger, summary, holdout, or audit artifact
is edited by this note.

Source rows are existing development-only fixed-pool rows:

- `results/generation_4_post_contact_gate_probe.json` for `baseline-rnn`,
  `rally-serve`, and `post-contact` / `pc_front_conversion`.
- `results/generation_4_net_pressure_noledger_probe.json` for `net-pressure`.
- `notes/parallel/20260527_g4_parallel3_rear_wall_press.md` for the prior
  built-in-promising transient `rw_press_forcejump` check.

The fixed development opponent pool here is `builtin`, `random`, `initial`,
`improved-v0`, `improved-v2`, `improved-v3`, `improved-v4`, `improved-v5`,
and `improved-v6`.

## Exact Seeds

All full fixed-pool rows use exactly these 50 generation-4 development seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

No holdout seeds `10000..10049` and no audit seeds `11000..11049` are used in
the recommendation.

## Candidate Definitions

| Candidate | Type | Definition |
| --- | --- | --- |
| `baseline-rnn` | neural comparator | Packaged `slimevolleygym.slimevolley.BaselinePolicy` wrapper. It is not a promotable heuristic candidate; it is the robustness comparator. |
| `rally-serve` | structural plus scalar/config | Registered generation-4 candidate. It keeps `late_contact_attack` and adds the point-reset serve detector: `abs(ball_x) <= 0.28`, `ball_y >= 1.45`, `abs(ball_vx) <= 0.50`, cooldown `> 12` policy steps, then 8 steps of action `101`. It uses the generation-4 rally scalar config: `high_arc_horizon=0.95`, `grounded_low_receive_airborne_margin=0.16`, `late_attack_vx=-0.45`, `late_attack_vy=-0.35`, `late_attack_y_min=0.24`, `low_ball_rescue_x_window=0.54`, `landing_horizon=0.38`, `overcommit_guard_x=0.18`. |
| `post-contact` | structural/history on scalar/config baseline | Registered development candidate layered on `rally-serve`. After a recent contact-like velocity flip within 2 policy steps, force action `101` in the front-court window `ball_x in [-0.08, 0.48]`, `ball_y in [0.24, 0.82]`, `ball_vx < -0.04`, `ball_vy <= 0.12`, and `agent_x - ball_x in [-0.05, 0.70]`. |
| `net-pressure` | structural on scalar/config baseline | Registered front-court pressure probe layered on `rally-serve`: if `ball_x in [-0.08, 0.55]`, `ball_y in [0.58, 1.30]`, `ball_vx <= -0.02`, `ball_vy <= 0.08`, and `agent_x - ball_x in [0.08, 0.72]`, force action `101`. |
| `rw_press_forcejump` | structural transient | Prior built-in-promising transient wrapper around `rally-serve`. When inherited `rear_wall_press` fires, force backward+jump action `011`. This was not promoted into maintained policy code and is not a registered policy name, but it has a prior full fixed-pool development check. |

## Fixed Development Pool Matrix

Cells are `mean; W-L-D; environment steps`.

| Opponent | `baseline-rnn` | `rally-serve` | `post-contact` | `net-pressure` | `rw_press_forcejump` |
| --- | ---: | ---: | ---: | ---: | ---: |
| `builtin` | `0.12; 18-12-20; 150000` | `0.14; 13-8-29; 150000` | `0.14; 13-8-29; 150000` | `-0.22; 7-14-29; 150000` | `0.16; 13-8-29; 150000` |
| `random` | `4.80; 50-0-0; 30603` | `4.74; 50-0-0; 38217` | `4.74; 50-0-0; 38217` | `4.74; 50-0-0; 38647` | `4.72; 50-0-0; 38814` |
| `initial` | `4.76; 50-0-0; 34004` | `4.68; 50-0-0; 44634` | `4.68; 50-0-0; 44634` | `4.72; 50-0-0; 45600` | `4.66; 50-0-0; 45025` |
| `improved-v0` | `4.82; 50-0-0; 32843` | `4.70; 50-0-0; 43242` | `4.70; 50-0-0; 43242` | `4.72; 50-0-0; 43696` | `4.68; 50-0-0; 43629` |
| `improved-v2` | `4.80; 50-0-0; 54551` | `4.38; 49-1-0; 76391` | `4.38; 49-1-0; 76391` | `4.56; 50-0-0; 76772` | `4.46; 49-1-0; 75883` |
| `improved-v3` | `3.84; 50-0-0; 118182` | `2.98; 48-0-2; 138122` | `3.04; 48-0-2; 137816` | `2.86; 48-1-1; 139090` | `2.88; 47-1-2; 137642` |
| `improved-v4` | `3.26; 48-0-2; 132511` | `2.34; 44-0-6; 143814` | `2.40; 44-0-6; 143709` | `2.38; 46-1-3; 143083` | `2.30; 43-1-6; 143603` |
| `improved-v5` | `2.10; 42-2-6; 145370` | `1.16; 32-7-11; 149716` | `1.22; 32-7-11; 149402` | `1.34; 33-7-10; 149563` | `1.14; 32-7-11; 150000` |
| `improved-v6` | `2.18; 42-2-6; 144837` | `1.22; 32-7-11; 149716` | `1.28; 32-7-11; 149402` | `1.36; 33-7-10; 149563` | `1.20; 32-7-11; 150000` |

## Failure Analysis

The built-in row is not sufficient for promotion. `rally-serve` and
`post-contact` score `0.14` against `builtin`, narrowly above the `baseline-rnn`
mean `0.12`, but their W-L-D is weaker: `13-8-29` versus `18-12-20`. The mean
edge comes from point differential and draws, not stronger win conversion.

`post-contact` is the best registered structural follow-up to `rally-serve` on
the hard archived tail. It preserves the built-in row and improves
`improved-v3` through `improved-v6` by `+0.06` mean versus `rally-serve`.
However, it still trails `baseline-rnn` by `0.80`, `0.86`, `0.88`, and `0.90`
mean on `improved-v3` through `improved-v6`.

`net-pressure` shows why archived checks are necessary in both directions. It
improves the hardest heuristic rows versus `rally-serve` and `post-contact` on
`improved-v5` and `improved-v6`, but it collapses the built-in row to `-0.22`
and is worse than `baseline-rnn` on every fixed-pool opponent.

`rw_press_forcejump` is the strongest prior built-in-only signal: `0.16` mean
against `builtin`, above `rally-serve`, `post-contact`, and `baseline-rnn`.
The fixed-pool check rejects it. It regresses `random`, `initial`,
`improved-v0`, `improved-v3`, `improved-v4`, `improved-v5`, and `improved-v6`
relative to `rally-serve`, adding losses on `improved-v3` and `improved-v4`.
Only `improved-v2` improves meaningfully.

The common failure mode is narrow action pressure that can move one built-in
point pattern while worsening archived robustness. The registered transparent
policies still lack the robust conversion profile of the RNN comparator on
archived heuristic opponents.

## Promotion Recommendation

Do not promote any candidate from this robustness pass.

`post-contact` is the best registered development reference among the checked
heuristics because it preserves the `rally-serve` built-in row and improves the
hard archived tail slightly. It is still development-only and does not clear the
robustness bar versus `baseline-rnn`.

Do not promote `rw_press_forcejump` from its `0.16` built-in mean, and do not
promote `net-pressure` from hard-tail gains. Both fail the fixed-pool
robustness check. No holdout or audit seed range should be opened or used for
these candidates based on this evidence.
