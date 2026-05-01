# ROS & SUTRIAS — static site

Multilingual static portfolio site for the architecture studio Ros & Sutrias (Barcelona). Hosted on GitHub Pages, free.

## Editing the site

Just open the relevant `.html` file in GitHub's web editor (the pencil icon on any file page) and commit. Changes go live in ~1 minute.

- Per-language pages live under `ca/`, `es/`, `en/`.
- Project detail pages: `ca/proyecto-<id>.html` (mirrored in `es/` and `en/`).
- Project images: `assets/fotos/proyectos/<id>/`. Last image of the folder is used as the thumbnail on the projects index.
- Stylesheet: `assets/css/site.css`.
- The novaWeb (2019 photo gallery) lives at `novaWeb/`.

## Adding a new project

1. Add photos to `assets/fotos/proyectos/<new-id>/` (e.g. `37/1.jpg`, `37/2.jpg`, …).
2. Copy `ca/proyecto-1.html` to `ca/proyecto-37.html` (and same for `es/`, `en/`), edit the title, year, location, and description.
3. Add a link card in `ca/projectes.html`, `es/projectes.html`, `en/projectes.html`.

Or, easier: re-run the generator (`_build/build.py`) after adding a row to `_build/ryss.json`. See `_build/README.md`.

## Regenerating from sources (advanced)

If you ever need to regenerate everything from the original DB dump:

```bash
python3 _build/parse_ryss.py   # SQL → ryss.json (mojibake-fixed)
python3 _build/build.py        # ryss.json + photos → HTML pages
python3 _build/build_novaweb.py # novaWeb gallery
```

## Local preview

```bash
python3 -m http.server 8000 --directory .
# open http://localhost:8000
```

## Origin

This site was reconstructed in May 2026 from a backup of `ros-sutrias.com` after the original cdmon-hosted PHP site was compromised in December 2024. See `MISSING.md` for what couldn't be recovered.
