#!/usr/bin/env python3
"""Parse ryss.sql, fix latin1->utf8 mojibake, emit structured JSON."""
import re, json, sys
from pathlib import Path

SQL_PATH = Path(__file__).parent.parent.parent / "ros-sutrias-backup/extracted/tmp_databases_dump/ryss.sql"
OUT_PATH = Path(__file__).parent / "ryss.json"


def fix_mojibake(s):
    """Fix UTF8-stored-as-(latin1|cp1252)-then-encoded-as-UTF8 mojibake.

    Walks the string char-by-char. When a char that is the prefix of a
    UTF-8 multi-byte sequence (0xC2, 0xC3 for 2-byte; 0xE0..0xEF for 3-byte)
    is encountered, try to encode the next 2 or 3 chars as cp1252 (which
    is a strict superset of latin1 in the 0x80-0x9F range and reverses
    Windows-style smart-quote remapping) and decode the bytes as utf-8.
    If that yields a single valid character, splice it in. Robust to
    mixed encoding: leaves clean characters alone.
    """
    if s is None:
        return None
    out = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        co = ord(c)
        consumed = 0
        if co in (0xC2, 0xC3) and i + 1 < n:
            try:
                fixed = s[i : i + 2].encode("cp1252", errors="strict").decode("utf-8")
                if len(fixed) == 1:
                    out.append(fixed)
                    consumed = 2
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass
        elif 0xE0 <= co <= 0xEF and i + 2 < n:
            try:
                fixed = s[i : i + 3].encode("cp1252", errors="strict").decode("utf-8")
                if len(fixed) == 1:
                    out.append(fixed)
                    consumed = 3
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass
        if consumed == 0:
            out.append(c)
            i += 1
        else:
            i += consumed
    result = "".join(out)
    result = result.replace("â€", "”")
    return result


def parse_sql_values(values_str: str):
    """Tokenize a sequence of SQL row tuples like (1,'a','b'),(2,'c','d')... into list of lists."""
    rows = []
    i = 0
    n = len(values_str)
    while i < n:
        while i < n and values_str[i] != "(":
            i += 1
        if i >= n:
            break
        i += 1
        row = []
        while True:
            while i < n and values_str[i] in " \t\r\n":
                i += 1
            if i >= n:
                break
            c = values_str[i]
            if c == "'":
                i += 1
                start = i
                buf = []
                while i < n:
                    ch = values_str[i]
                    if ch == "\\" and i + 1 < n:
                        nxt = values_str[i + 1]
                        if nxt == "n":
                            buf.append("\n")
                        elif nxt == "r":
                            buf.append("\r")
                        elif nxt == "t":
                            buf.append("\t")
                        elif nxt == "0":
                            buf.append("\0")
                        elif nxt in ("'", '"', "\\"):
                            buf.append(nxt)
                        else:
                            buf.append(nxt)
                        i += 2
                        continue
                    if ch == "'":
                        if i + 1 < n and values_str[i + 1] == "'":
                            buf.append("'")
                            i += 2
                            continue
                        i += 1
                        break
                    buf.append(ch)
                    i += 1
                row.append("".join(buf))
            elif c == ")":
                i += 1
                break
            else:
                start = i
                while i < n and values_str[i] not in ",)":
                    i += 1
                tok = values_str[start:i].strip()
                if tok.upper() == "NULL":
                    row.append(None)
                else:
                    try:
                        row.append(int(tok))
                    except ValueError:
                        try:
                            row.append(float(tok))
                        except ValueError:
                            row.append(tok)
            while i < n and values_str[i] in " \t\r\n":
                i += 1
            if i < n and values_str[i] == ",":
                i += 1
                continue
            if i < n and values_str[i] == ")":
                i += 1
                break
        rows.append(row)
        while i < n and values_str[i] != ",":
            if values_str[i] == ";":
                return rows
            i += 1
        if i < n and values_str[i] == ",":
            i += 1
    return rows


def parse_table(sql: str, table: str):
    create = re.search(r"CREATE TABLE `" + table + r"` \((.+?)\) ENGINE=", sql, re.DOTALL)
    cols = []
    if create:
        for line in create.group(1).split("\n"):
            line = line.strip()
            m = re.match(r"`([^`]+)`", line)
            if m:
                cols.append(m.group(1))

    insert = re.search(
        r"INSERT INTO `" + table + r"` \(([^)]+)\) VALUES\s*(.+?);\s*\n",
        sql,
        re.DOTALL,
    )
    if not insert:
        return cols, []
    insert_cols = [c.strip().strip("`") for c in insert.group(1).split(",")]
    raw_rows = parse_sql_values(insert.group(2))
    out = []
    for row in raw_rows:
        d = {}
        for k, v in zip(insert_cols, row):
            if isinstance(v, str):
                v = fix_mojibake(v)
            d[k] = v
        out.append(d)
    return insert_cols, out


def main():
    sql = SQL_PATH.read_text(encoding="utf-8", errors="replace")
    tables = [
        "ACTIVIDAD_DOCENTE",
        "ACTIVIDAD_PROFESIONAL",
        "COLABORADORES",
        "COLABORADORES_EXTERNOS",
        "COLABORADORES_INTERNOS",
        "CUADROS",
        "EQUIPO",
        "OBRA_PREVIA",
        "OPCIONES",
    ]
    out = {}
    for t in tables:
        cols, rows = parse_table(sql, t)
        out[t] = {"columns": cols, "rows": rows}
        print(f"{t}: {len(rows)} rows", file=sys.stderr)
    OUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
