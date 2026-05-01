#!/usr/bin/env python3
"""Build /novaWeb/ as a simple static gallery of the 2019 WordPress uploads."""
import re
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent.parent
UPLOADS_SRC = ROOT.parent / "ros-sutrias-backup/extracted/novaWeb/wp-content/uploads/2019"
UPLOADS_DST = ROOT / "novaWeb/uploads"


def is_resized(name: str) -> bool:
    return bool(re.search(r"-\d+x\d+\.(jpe?g|png)$", name, re.IGNORECASE))


def project_key(name: str) -> str:
    """Extract a stable project group name from the filename."""
    stem = Path(name).stem
    stem = re.sub(r"_\d+(_.+)?$", "", stem)
    stem = re.sub(r"_\d+x\d+$", "", stem)
    stem = re.sub(r"_(PB|PT|PP|SC|Aèria|Foto|Plànols|Alçats|Alçat|Alát|Secció|Emplaçament|Habitatge.*)$", "", stem)
    stem = re.sub(r"-\d+x\d+$", "", stem)
    if not stem:
        return "Altres"
    return stem.replace("_", " ").replace("-", " ")


def main():
    UPLOADS_DST.mkdir(parents=True, exist_ok=True)
    for f in UPLOADS_DST.iterdir():
        if f.is_file():
            f.unlink()

    originals = []
    for src in sorted(UPLOADS_SRC.rglob("*")):
        if not src.is_file():
            continue
        if src.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue
        if is_resized(src.name):
            continue
        if "100x100" in src.name:
            continue
        originals.append(src)

    print(f"Copying {len(originals)} originals to novaWeb/uploads/")
    for src in originals:
        dst = UPLOADS_DST / src.name
        if not dst.exists():
            shutil.copy2(src, dst)

    groups = {}
    for src in originals:
        k = project_key(src.name)
        groups.setdefault(k, []).append(src.name)

    print(f"Grouped into {len(groups)} projects:")
    for k, files in sorted(groups.items()):
        print(f"  {k}: {len(files)} images")

    sections_html = ""
    for proj, files in sorted(groups.items()):
        items = "".join(
            f'<a class="nova-item" href="uploads/{escape(name)}"><img src="uploads/{escape(name)}" alt="{escape(name)}" loading="lazy"></a>'
            for name in sorted(files)
        )
        sections_html += f"""
        <section class="nova-project">
            <h2>{escape(proj)}</h2>
            <div class="nova-gallery">{items}</div>
        </section>
        """

    html = f"""<!doctype html>
<html lang="ca">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>novaWeb — ROS &amp; SUTRIAS</title>
<link rel="stylesheet" href="../assets/css/site.css">
<style>
.nova-project {{ margin-bottom: 56px; }}
.nova-project h2 {{ font-size: 18px; letter-spacing: 0.12em; color: var(--accent); border-bottom: 1px solid var(--line); padding-bottom: 8px; margin-bottom: 12px; }}
</style>
</head>
<body>
<header class="site-header">
    <a class="brand" href="../index.html">ROS &amp; SUTRIAS</a>
    <nav class="topnav">
        <a href="../ca/index.html">← Inici</a>
    </nav>
</header>
<main>
    <section class="page-head">
        <h1>novaWeb</h1>
        <p class="muted">Galeria fotogràfica dels projectes (2019). Aquesta era la versió WordPress de la web; el contingut original ha estat preservat aquí com a galeria estàtica.</p>
    </section>
    <article class="news-item">
        <p class="news-date">2019-03-13</p>
        <h2>Web de Ros-Sutrias</h2>
        <p>La web de l'estudi Ros-Sutrias torna a estar operativa. Estigueu connectats per a veure totes les novetats. En els següents dies anirem pujant els projectes més destacats.</p>
    </article>
    {sections_html}
</main>
<footer class="site-footer">
    <p>&copy; ROS &amp; SUTRIAS — <a href="mailto:ros-sutrias@coac.net">ros-sutrias@coac.net</a></p>
</footer>
</body>
</html>
"""
    (ROOT / "novaWeb/index.html").write_text(html, encoding="utf-8")
    print(f"\nWrote {ROOT / 'novaWeb/index.html'}")


if __name__ == "__main__":
    main()
