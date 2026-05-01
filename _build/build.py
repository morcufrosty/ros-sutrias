#!/usr/bin/env python3
"""Generate the static ros-sutrias site from ryss.json and copied photos."""
import json
import re
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = json.loads((ROOT / "_build/ryss.json").read_text(encoding="utf-8"))
SRC_FOTOS = ROOT.parent / "ros-sutrias-backup/extracted/fotos"

LANGS = ["ca", "es", "en"]
LANG_LABEL = {"ca": "Català", "es": "Español", "en": "English"}
LANG_FIELD = {"ca": "CAT", "es": "CAS", "en": "ENG"}

UI = {
    "ca": {
        "projectes": "Projectes",
        "obres": "Obres",
        "equip": "Equip",
        "docencia": "Docència",
        "contacte": "Contacte",
        "inici": "Inici",
        "totes_obres": "Totes les obres i projectes",
        "any": "Any",
        "tema": "Tema",
        "tipus": "Tipus",
        "obra": "Obra construïda",
        "proyecto": "Projecte",
        "membres_estudi": "Membres de l'estudi",
        "collaboradors": "Col·laboradors externs",
        "back_projects": "Tornar als projectes",
        "no_description": "Sense descripció disponible.",
        "site_intro": "Estudi d'arquitectura. Barcelona.",
        "novaWeb": "Notícies",
    },
    "es": {
        "projectes": "Proyectos",
        "obres": "Obras",
        "equip": "Equipo",
        "docencia": "Docencia",
        "contacte": "Contacto",
        "inici": "Inicio",
        "totes_obres": "Todas las obras y proyectos",
        "any": "Año",
        "tema": "Tema",
        "tipus": "Tipo",
        "obra": "Obra construida",
        "proyecto": "Proyecto",
        "membres_estudi": "Miembros del estudio",
        "collaboradors": "Colaboradores externos",
        "back_projects": "Volver a los proyectos",
        "no_description": "Sin descripción disponible.",
        "site_intro": "Estudio de arquitectura. Barcelona.",
        "novaWeb": "Noticias",
    },
    "en": {
        "projectes": "Projects",
        "obres": "Works",
        "equip": "Team",
        "docencia": "Teaching",
        "contacte": "Contact",
        "inici": "Home",
        "totes_obres": "All works and projects",
        "any": "Year",
        "tema": "Theme",
        "tipus": "Type",
        "obra": "Built work",
        "proyecto": "Project",
        "membres_estudi": "Studio members",
        "collaboradors": "External collaborators",
        "back_projects": "Back to projects",
        "no_description": "No description available.",
        "site_intro": "Architecture studio. Barcelona.",
        "novaWeb": "News",
    },
}


def html_decode(s):
    """Decode named HTML entities to their characters."""
    if not s:
        return ""
    repl = {
        "&aacute;": "á", "&eacute;": "é", "&iacute;": "í", "&oacute;": "ó", "&uacute;": "ú",
        "&Aacute;": "Á", "&Eacute;": "É", "&Iacute;": "Í", "&Oacute;": "Ó", "&Uacute;": "Ú",
        "&agrave;": "à", "&egrave;": "è", "&igrave;": "ì", "&ograve;": "ò", "&ugrave;": "ù",
        "&Agrave;": "À", "&Egrave;": "È", "&Igrave;": "Ì", "&Ograve;": "Ò", "&Ugrave;": "Ù",
        "&ntilde;": "ñ", "&Ntilde;": "Ñ", "&ccedil;": "ç", "&Ccedil;": "Ç",
        "&euro;": "€", "&amp;": "&", "&quot;": '"', "&apos;": "'",
        "&middot;": "·", "&ldquo;": "“", "&rdquo;": "”", "&lsquo;": "‘", "&rsquo;": "’",
        "&hellip;": "…", "&ndash;": "–", "&mdash;": "—", "&nbsp;": " ",
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    return s


def safe_html(s):
    """Sanitize a chunk that may already contain a small set of inline HTML tags (b, i, br) from the old DB."""
    if not s:
        return ""
    s = html_decode(s)
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    safe_tags = ["b", "i", "br", "strong", "em", "p"]
    for tag in safe_tags:
        s = re.sub(rf"<\s*{tag}\s*/?\s*>", f"<{tag}>", s, flags=re.IGNORECASE)
        s = re.sub(rf"<\s*/\s*{tag}\s*>", f"</{tag}>", s, flags=re.IGNORECASE)
    s = re.sub(r"<(?!/?(?:b|i|br|strong|em|p)\b)[^>]+>", "", s)
    return s


def text_for(lang, row, base):
    """Pull MEMORIA_CAT/CAS/ENG, NOMBRE/_CAS/_ENG etc. with sensible fallback."""
    field = LANG_FIELD[lang]
    if base == "NOMBRE":
        if lang == "ca":
            return row.get("NOMBRE", "") or ""
        if lang == "es":
            return row.get("NOMBRE_CAS") or row.get("NOMBRE", "")
        if lang == "en":
            return row.get("NOMBRE_ENG") or row.get("NOMBRE_CAS") or row.get("NOMBRE", "")
    key = f"{base}_{field}"
    val = row.get(key, "")
    if not val and field != "CAT":
        val = row.get(f"{base}_CAT", "")
    return val or ""


def render_layout(title, lang, body, depth=1, active=None, filename="index.html"):
    """depth = how many directories deep this file lives, used for relative asset paths.
    filename = the current page's filename, used so the language switch points to the same page in other langs."""
    css = "../" * depth + "assets/css/site.css"
    home_link = "../" * depth + (f"{lang}/" if lang else "")
    nav = ""
    if lang:
        u = UI[lang]
        prefix = "../" * (depth - 1) if depth > 0 else ""
        if depth == 1:
            base = ""
        else:
            base = prefix
        nav = f"""
        <nav class="topnav">
            <a href="{base}index.html"{' class="active"' if active=='inici' else ''}>{u['inici']}</a>
            <a href="{base}projectes.html"{' class="active"' if active=='projectes' else ''}>{u['projectes']}</a>
            <a href="{base}equip.html"{' class="active"' if active=='equip' else ''}>{u['equip']}</a>
            <a href="{base}docencia.html"{' class="active"' if active=='docencia' else ''}>{u['docencia']}</a>
            <span class="lang-switch">
                <a href="{prefix}../ca/{filename}" class="{'active' if lang=='ca' else ''}">CAT</a>
                <a href="{prefix}../es/{filename}" class="{'active' if lang=='es' else ''}">ESP</a>
                <a href="{prefix}../en/{filename}" class="{'active' if lang=='en' else ''}">ENG</a>
            </span>
        </nav>
        """
    return f"""<!doctype html>
<html lang="{lang or 'ca'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} — ROS & SUTRIAS</title>
<link rel="stylesheet" href="{css}">
</head>
<body>
<header class="site-header">
    <a class="brand" href="{home_link}">ROS &amp; SUTRIAS</a>
    {nav}
</header>
<main>
{body}
</main>
<footer class="site-footer">
    <p>&copy; ROS &amp; SUTRIAS — Estudi d'arquitectura, Barcelona — <a href="tel:+34670297979">670 297 979</a> · <a href="tel:+34655696777">655 696 777</a></p>
</footer>
</body>
</html>
"""


def slug(s):
    s = re.sub(r"[^A-Za-z0-9]+", "-", html_decode(s).lower())
    return s.strip("-")[:60] or "x"


def main():
    projects = sorted(DATA["ACTIVIDAD_PROFESIONAL"]["rows"], key=lambda r: (r.get("ANO") or "", r.get("ID")))
    bios = DATA["ACTIVIDAD_DOCENTE"]["rows"]
    int_team = DATA["COLABORADORES_INTERNOS"]["rows"]
    ext_team = DATA["COLABORADORES_EXTERNOS"]["rows"]

    site_dir = ROOT
    for sub in ["assets/fotos/proyectos", "assets/fotos/cuadros", "assets/fotos/premios", "assets/fotos/interfaz", "novaWeb"]:
        (site_dir / sub).mkdir(parents=True, exist_ok=True)

    print("=== Building root redirect → /ca/ ===")
    landing = """<!doctype html>
<html lang="ca">
<head>
<meta charset="utf-8">
<title>ROS &amp; SUTRIAS</title>
<link rel="canonical" href="https://ros-sutrias.com/ca/">
<meta http-equiv="refresh" content="0; url=ca/index.html">
<script>window.location.replace("ca/index.html");</script>
</head>
<body>
<p>Redirecting to <a href="ca/index.html">ros-sutrias.com</a>…</p>
</body>
</html>
"""
    (site_dir / "index.html").write_text(landing, encoding="utf-8")

    for lang in LANGS:
        u = UI[lang]
        ldir = site_dir / lang
        ldir.mkdir(exist_ok=True)

        print(f"=== Building /{lang}/ ===")
        intro_short = {
            "ca": "Estudi d'arquitectura amb seu a Barcelona, fundat per Jordi Ros i Jordi Sutrias. La pràctica professional combina la docència universitària amb una activitat centrada en l'obra pública: equipaments sanitaris, educatius, esportius i habitatge.",
            "es": "Estudio de arquitectura con sede en Barcelona, fundado por Jordi Ros y Jordi Sutrias. La práctica profesional combina la docencia universitaria con una actividad centrada en la obra pública: equipamientos sanitarios, educativos, deportivos y vivienda.",
            "en": "Architecture studio based in Barcelona, founded by Jordi Ros and Jordi Sutrias. Professional practice combines university teaching with a focus on public buildings: healthcare, educational, sports and housing facilities.",
        }[lang]

        nav_links = [
            ("projectes.html", u["projectes"]),
            ("equip.html", u["equip"]),
            ("docencia.html", u["docencia"]),
        ]
        nav_html = "".join(
            f'<a class="home-link" href="{h}">{escape(t)}</a>'
            for h, t in nav_links
        )
        body = f"""
        <section class="home-hero-plain">
            <h1 class="home-title">ROS &amp; SUTRIAS</h1>
            <p class="home-tagline">{escape(u['site_intro'])}</p>
            <nav class="home-nav-min">{nav_html}</nav>
        </section>
        <section class="home-intro">
            <p>{escape(intro_short)}</p>
        </section>
        """
        (ldir / "index.html").write_text(render_layout(u["inici"], lang, body, depth=1, active="inici", filename="index.html"), encoding="utf-8")

        print(f"  /{lang}/projectes.html (index)")
        force_first_image = {1, 7, 9, 10, 12, 18, 30}
        items = []
        for p in projects:
            pid = p["ID"]
            name = html_decode(text_for(lang, p, "NOMBRE")) or f"Project {pid}"
            year = p.get("ANO") or ""
            tema = (p.get("TEMA") or "").lower()
            tipus = (p.get("TIPO") or "").lower()
            premio_path = SRC_FOTOS / "premios" / f"{pid}.jpg"
            proj_dir = SRC_FOTOS / "proyectos" / str(pid)
            project_photos = []
            if proj_dir.is_dir():
                for f in sorted(proj_dir.iterdir()):
                    if f.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                        project_photos.append(f.name)
            if pid in force_first_image and project_photos:
                thumb = f"../assets/fotos/proyectos/{pid}/{project_photos[0]}"
            elif premio_path.is_file():
                thumb = f"../assets/fotos/premios/{pid}.jpg"
            elif project_photos:
                thumb = f"../assets/fotos/proyectos/{pid}/{project_photos[-1]}"
            else:
                thumb = f"../assets/fotos/cuadros/{pid}.jpg"
            year_html = f'<span class="proj-overlay-year">{escape(year)}</span>' if year else ""
            items.append(
                f"""
        <a class="proj-card tema-{escape(tema)} tipus-{escape(tipus)}" href="proyecto-{pid}.html">
            <img class="proj-thumb-img" src="{thumb}" alt="{escape(name)}" loading="lazy">
            <div class="proj-overlay">
                <h3>{escape(name)}</h3>
                {year_html}
            </div>
        </a>"""
            )
        body = f"""
        <section class="page-head">
            <h1>{escape(u['projectes'])}</h1>
            <p class="muted">{escape(u['totes_obres'])}</p>
        </section>
        <section class="proj-grid">
            {''.join(items)}
        </section>
        """
        (ldir / "projectes.html").write_text(render_layout(u["projectes"], lang, body, depth=1, active="projectes", filename="projectes.html"), encoding="utf-8")

        for p in projects:
            pid = p["ID"]
            name = html_decode(text_for(lang, p, "NOMBRE")) or f"Project {pid}"
            year = p.get("ANO") or ""
            tema = p.get("TEMA") or ""
            tipus = p.get("TIPO") or ""
            datos = safe_html(text_for(lang, p, "DATOS"))
            memoria = safe_html(text_for(lang, p, "MEMORIA"))
            label = u["obra"] if tipus == "OBRA" else (u["proyecto"] if tipus == "PROYECTO" else "")

            proj_dir = SRC_FOTOS / "proyectos" / str(pid)
            all_photos = []
            if proj_dir.is_dir():
                for img in sorted(proj_dir.iterdir()):
                    if img.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                        all_photos.append(img.name)
            premio_path = SRC_FOTOS / "premios" / f"{pid}.jpg"
            if not premio_path.is_file() and len(all_photos) > 1:
                gallery_photos = all_photos[:-1]
            else:
                gallery_photos = all_photos
            gallery = ""
            if gallery_photos:
                gallery = '<div class="proj-gallery">' + "".join(
                    f'<a class="gal-item" href="../assets/fotos/proyectos/{pid}/{name_}"><img src="../assets/fotos/proyectos/{pid}/{name_}" alt="" loading="lazy"></a>'
                    for name_ in gallery_photos
                ) + "</div>"
            premio_html = ""

            body = f"""
            <article class="project">
                <a class="back" href="projectes.html">← {escape(u['back_projects'])}</a>
                <header class="proj-header">
                    <p class="proj-tag">{escape(label)} · {escape(tema)}{(' · ' + escape(year)) if year else ''}</p>
                    <h1>{escape(name)}</h1>
                </header>
                {f'<aside class="proj-datos">{datos}</aside>' if datos else ''}
                {f'<section class="proj-memoria">{memoria}</section>' if memoria else ('<section class="proj-memoria"><p class="muted">' + escape(u['no_description']) + '</p></section>')}
                {gallery}
                {premio_html}
            </article>
            """
            (ldir / f"proyecto-{pid}.html").write_text(render_layout(name, lang, body, depth=1, active="projectes", filename=f"proyecto-{pid}.html"), encoding="utf-8")

        print(f"  /{lang}/equip.html")
        intern = "".join(
            f'<li><strong>{escape(html_decode(c["NOMBRE"]))}</strong>'
            f'{(" — " + escape(html_decode(text_for(lang, c, "CARGO")))) if text_for(lang, c, "CARGO") else ""}'
            f'{("<br><span class=\"muted\">" + escape(html_decode(text_for(lang, c, "TEXTO"))) + "</span>") if text_for(lang, c, "TEXTO") else ""}'
            f'</li>'
            for c in int_team if c.get("NOMBRE")
        )
        ext_groups = {}
        for c in ext_team:
            tema = c.get("TEMA", "OTROS") or "OTROS"
            ext_groups.setdefault(tema, []).append(c)
        ext_html = ""
        for tema, members in ext_groups.items():
            ext_html += f'<h3 class="tema-h3">{escape(tema)}</h3><ul class="ext-list">'
            for c in members:
                ext_html += (
                    f'<li><strong>{escape(html_decode(c.get("NOMBRE","")))}</strong>'
                    f'{(" — " + escape(html_decode(text_for(lang, c, "CARGO")))) if text_for(lang, c, "CARGO") else ""}'
                    f'</li>'
                )
            ext_html += "</ul>"

        equipo_intro = ""
        if DATA["EQUIPO"]["rows"]:
            equipo_intro = safe_html(text_for(lang, DATA["EQUIPO"]["rows"][0], "TEXTO"))

        body = f"""
        <section class="page-head">
            <h1>{escape(u['equip'])}</h1>
        </section>
        {f'<section class="equipo-intro"><p>{equipo_intro}</p></section>' if equipo_intro else ''}
        <section class="team-section">
            <h2>{escape(u['membres_estudi'])}</h2>
            <ul class="team-list">{intern}</ul>
        </section>
        <section class="team-section">
            <h2>{escape(u['collaboradors'])}</h2>
            {ext_html}
        </section>
        """
        (ldir / "equip.html").write_text(render_layout(u["equip"], lang, body, depth=1, active="equip", filename="equip.html"), encoding="utf-8")

        print(f"  /{lang}/docencia.html")
        items = []
        for b in bios:
            nombre = b.get("NOMBRE") or ""
            text = safe_html(text_for(lang, b, "TEXTO"))
            if not text:
                continue
            items.append(f'<article class="doc-item"><h3>{escape(nombre)}</h3><div class="doc-body">{text}</div></article>')
        body = f"""
        <section class="page-head"><h1>{escape(u['docencia'])}</h1></section>
        <section class="doc-list">{''.join(items) or '<p class="muted">No hi ha contingut disponible.</p>'}</section>
        """
        (ldir / "docencia.html").write_text(render_layout(u["docencia"], lang, body, depth=1, active="docencia", filename="docencia.html"), encoding="utf-8")

        old_contact = ldir / "contacte.html"
        if old_contact.exists():
            old_contact.unlink()

    print("Done.")


if __name__ == "__main__":
    main()
