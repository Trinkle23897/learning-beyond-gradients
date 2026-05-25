# Learning Beyond Gradients Blog Artifacts

This repository contains the public artifacts for:

**Learning Beyond Gradients**

Published article:

- https://trinkle23897.github.io/learning-beyond-gradients/

Artifact repository:

- https://github.com/Trinkle23897/learning-beyond-gradients

The article is bilingual. The rendered HTML defaults to English and includes a Chinese switcher.

## Source Files

- `learning-beyond-gradient.en.md`: English article source.
- `learning-beyond-gradient.md`: Chinese article source.
- `learning-beyond-gradient.html`: rendered bilingual HTML.
- `render_learning_beyond_gradient.py`: local renderer.

The deployed article is `learning-beyond-gradient.html`.

## Local Preview

From the repository root:

```bash
python3 -m http.server 8000
```

Then open:

```text
http://127.0.0.1:8000/learning-beyond-gradient.html
```

Opening the HTML file directly also works in most browsers, but using `http.server` is closer to how the page is served.

## Re-render The HTML

Install the rendering dependency:

```bash
python3 -m pip install -r requirements.txt
```

Then run:

```bash
python3 render_learning_beyond_gradient.py
```

The renderer reads the English and Chinese Markdown files and rewrites `learning-beyond-gradient.html` in place.

## GitHub Pages

The site is deployed by `.github/workflows/deploy-pages.yml` on every push to `main`.

The workflow does not publish the whole repository as the website root. It builds a small `_site` directory containing:

- `index.html`, copied from `learning-beyond-gradient.html`.
- `.nojekyll`.
- Local files referenced by the article through `src` or `href`, such as figures, videos, scripts, CSVs, and prompt files.

## Included Artifacts

The repository includes the files needed to inspect and reproduce the article's representative results:

- `atari/pong/`: Pong policy script.
- `atari/breakout/`: Breakout policy, trial summaries, sample-efficiency figure, and checkpoint videos.
- `atari/montezuma/`: Montezuma exploratory policies, state/archive search scripts, summaries, probe images, and replay artifacts.
- `atari/atari57/`: Atari57 aggregate/per-game figures, CSV summaries, and the batch prompt template used for unattended Codex CLI runs.
- `mujoco/ant/`: Ant policy, minimal extracted Ant policy, trial summaries, MuJoCo XML, sample-efficiency figure, and final-policy video.
- `mujoco/halfcheetah/`: HalfCheetah policy script, iteration log, and sample-efficiency figure.
- `vizdoom/`: D1/D3 VizDoom heuristic scripts plus 35fps 10-seed render videos.

The article appendix contains reproduction commands for several representative results. Those commands assume they are run from the repository root after cloning this repo.

## Community Efforts

- [HL-ImageNet](https://github.com/xisen-w/hl-imagenet) explores Heuristic Learning in symbolic visual classification, using a non-neural code pipeline to test how far code-based heuristic updates can go on a constrained ImageNet-style perception task. The project is intended as a perception-domain boundary case for HL: train-only optimization over symbolic code can still become a memorizer, so the central problem becomes reusable visual representation and generalization rather than fitting alone.

## Runtime Notes

The experiments were written against EnvPool `1.1.1`. The article commands assume the relevant Python environment already has EnvPool and the Atari/MuJoCo runtime dependencies installed.

For Ant, `ant_envpool.xml` stays next to `heuristic_ant.py` under `mujoco/ant/`. The reproduction command references it as:

```bash
--mujoco-xml-path mujoco/ant/ant_envpool.xml
```

## Citation

```bibtex
@misc{weng2026learning_beyond_gradients,
  title = {Learning Beyond Gradients},
  author = {Weng, Jiayi},
  year = {2026},
  month = may,
  howpublished = {\url{https://trinkle23897.github.io/learning-beyond-gradients/}},
  note = {Blog post}
}
```
