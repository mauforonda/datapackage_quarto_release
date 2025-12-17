#!/usr/bin/env python3

import json
import sys

in_json = sys.argv[1] if len(sys.argv) > 1 else "datapackage.json"
out_qmd = sys.argv[2] if len(sys.argv) > 2 else "datapackage.qmd"

dp = json.load(open(in_json, "r", encoding="utf-8"))


def md_escape(s: str) -> str:
    return s.replace("|", r"\|")


def field_row(f):
    name = f.get("name", "")
    ftype = f.get("type", "")
    desc = f.get("description", "") or ""
    desc = md_escape(desc).replace("\n", "<br>")
    return f"| `{name}` | `{ftype}` | {desc} |"


title = dp.get("title", dp.get("name", "Data Package"))
pkg_name = dp.get("name", "")
version = dp.get("version", "")

lines = []
lines += [
    "---",
    f'title: "{title}"',
    "format:",
    "  pdf:",
    "    toc: false",
    "    number-sections: false",
    "    documentclass: scrartcl",
    "    fontsize: 11pt",
    "    geometry: margin=1in",
    "    linestretch: 1.2",
    "---",
    "",
    f"**Título:** `{title}`  ",
    f"**Paquete:** `{pkg_name}`  ",
    f"**Versión:** `{version}`",
    "",
    "## Recursos",
    "",
]

for r in dp["resources"]:
    lines += [
        f"### {r.get('title', r.get('name', ''))}",
        "",
        f"**Nombre:** `{r.get('name', '')}`  ",
        f"**Tipo:** `{r.get('type', '')}`  ",
        f"**Documento:** `{r.get('path', '')}`  ",
        f"**Formato:** `{r.get('format', '')}`  ",
        f"**Extensión:** `{r.get('mediatype', '')}`  ",
        f"**Codificación:** `{r.get('encoding', '')}`",
        "",
        "#### Esquema",
        "",
        "| Campo | Tipo | Descripción |",
        "|:---|:---:|:---|",
    ]
    for f in r["schema"]["fields"]:
        lines.append(field_row(f))

open(out_qmd, "w", encoding="utf-8").write("\n".join(lines))
print(f"Escribí: {out_qmd}")
