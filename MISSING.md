# What was lost in the December 2024 compromise

Documenting the gaps in the recovered content so future maintainers know what is and isn't original.

## Lost beyond recovery

The original 2010-era PHP files of `ros-sutrias.com` were deleted by an attacker on **2024-12-10** and replaced with malware. Cdmon's automatic backup retention (~30 days) was already past by the time we started the migration in May 2026. The Internet Archive (archive.org Wayback Machine) had **never crawled the site**, so no rendered HTML snapshots exist.

**Files we no longer have:**

- `index.php`, `conexion.php` (DB connection script).
- `CAT/0.0.php`, `CAS/0.0.php`, `ENG/0.0.php` and all the inner-page PHP templates that rendered project lists, bios, equipment, etc.
- The `administrador/A.0.0.php` admin panel (and we wouldn't restore it on a static site anyway).

## Reconstructed from the database

The `ryss.sql` dump (rescued via FTP) preserved all the actual *content*:

- 36 architecture project records (`ACTIVIDAD_PROFESIONAL`) with names, year, location, surface, budget, description in CAT/CAS/ENG.
- Architect bios (`ACTIVIDAD_DOCENTE`).
- Internal team members (`COLABORADORES_INTERNOS`).
- External collaborators by category (`COLABORADORES_EXTERNOS`).
- Studio intro text (`EQUIPO`).

These were used to regenerate the HTML pages. **Only the visual presentation is new** — every word of text on the rebuilt site comes from the original database.

## Known content gaps

Some database rows were already incomplete in the dump:

- A few projects lack a description in English (`MEMORIA_ENG` empty) — they fall back to the Catalan text.
- A few projects lack a year (`ANO` empty).
- One project (`OBRA_PREVIA` ID 7) had only an empty placeholder row in the original DB.
- The novaWeb (2019 WordPress) had only 2 actual posts. One was a "we're back online" announcement (preserved on the site), the other was a 2024 SEO spam injection (discarded).

## Encoding fix

The DB dump had **mixed encoding**: most rows were clean UTF-8, but `EQUIPO`, `ACTIVIDAD_DOCENTE`, and a few `COLABORADORES_INTERNOS` rows were partially mojibake'd (UTF-8 stored as Windows-1252 then re-encoded as UTF-8). The parser at `_build/parse_ryss.py` reverses this char-by-char.

## What's gone forever

Any change made to `ros-sutrias.com` between the date of the SQL dump (visible in the dump) and December 2024 that wasn't covered by the dump is lost.
