# Classic Control Heuristic Policies

This folder collects small reproducible heuristic-policy scripts for Classic
Control environments.

## MountainCarContinuous-v0: scalar energy-pump policy

Entrypoint:

```bash
python classic_control/mountain_car_continuous/heuristic_mountain_car_continuous.py \
  --episodes 100 \
  --seed 10000
```

The policy uses only the native observation `(position, velocity)`. It applies a
continuous force in the direction of travel to build energy and keeps pushing
right on the goal hill. It does not use gradients, reward-model training,
environment internals, or seed-specific routes.

Local 100-seed validation from Arthur Yau's independent EnvPool heuristic
harness, using EnvPool 1.2.2 and seeds 10000..10099:

```text
mean = 93.69343671277166
std = 0.9122827223292292
min = 92.38399665057659
max = 94.75199676305056
```

This first contribution is intentionally small: one simple Classic Control
script with a reported validation window, so it can fit the existing artifact
style before adding broader Classic Control / Box2D benchmark reporting.
