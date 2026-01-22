#!/usr/bin/env python3

import json
import sys

in_json = sys.argv[1] if len(sys.argv) > 1 else "datapackage.json"
out_qmd = sys.argv[2] if len(sys.argv) > 2 else "datapackage.qmd"

dp = json.load(open(in_json, "r", encoding="utf-8"))


def md_escape(s: str) -> str:
    return s.replace("|", r"\|")


def tex_escape(s: str) -> str:
    return (
        s.replace("\\", r"\textbackslash{}")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("$", r"\$")
        .replace("&", r"\&")
        .replace("#", r"\#")
        .replace("%", r"\%")
        .replace("_", r"\_")
        .replace("^", r"\^{}")
        .replace("~", r"\~{}")
    )


def field_row(f):
    name = f.get("name", "")
    ftype = f.get("type", "")
    desc = f.get("description", "") or ""
    desc = tex_escape(desc).replace("\n", r"\\")
    name = tex_escape(name)
    ftype = tex_escape(ftype)
    return (
        r"\textcolor{OrnamentDark}{\textbf{"
        + f"{name}"
        + r"}} & \textcolor{OrnamentDark}{"
        + f"{ftype}"
        + r"} & \textcolor{OrnamentDark}{"
        + f"{desc}"
        + r"} \\"
    )


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
    "    pdf-engine: lualatex",
    "    fontsize: 11pt",
    "    geometry: margin=1in",
    "    linestretch: 1.2",
    "    colorlinks: true",
    "    include-in-header:",
    "      - linea.tex",
    "---",
    "",
    r"\BrandRuleAccent",
    r"\begin{BrandMeta}",
    rf"\MetaItem{{Título}}{{{tex_escape(title)}}}",
    rf"\MetaItem{{Paquete}}{{{tex_escape(pkg_name)}}}",
    rf"\MetaItem{{Versión}}{{{tex_escape(version)}}}",
    r"\end{BrandMeta}",
    r"\BrandRuleAccent",
    "",
    "## Recursos",
    "",
]

for r in dp["resources"]:
    resource_title = tex_escape(r.get("title", r.get("name", "")))
    lines += [
        rf"\ResourceTitle{{{resource_title}}}",
        "",
        f"**Nombre:** `{r.get('name', '')}`  ",
        f"**Tipo:** `{r.get('type', '')}`  ",
        f"**Documento:** `{r.get('path', '')}`  ",
        f"**Formato:** `{r.get('format', '')}`  ",
        f"**Extensión:** `{r.get('mediatype', '')}`  ",
        f"**Codificación:** `{r.get('encoding', '')}`",
        "",
        r"\paragraph{Esquema}",
        "",
        r"\begin{longtable}{@{}p{0.26\linewidth}p{0.16\linewidth}p{0.52\linewidth}@{}}",
        r"\rowcolor{OrnamentLight}\sffamily\bfseries\small \textcolor{BaseText}{Campo} & \textcolor{BaseText}{Tipo} & \textcolor{BaseText}{Descripción} \\",
        r"\addlinespace[0.2em]",
        r"\midrule",
        r"\endfirsthead",
        r"\rowcolor{OrnamentLight}\sffamily\bfseries\small \textcolor{BaseText}{Campo} & \textcolor{BaseText}{Tipo} & \textcolor{BaseText}{Descripción} \\",
        r"\addlinespace[0.2em]",
        r"\midrule",
        r"\endhead",
        r"\normalfont\normalsize\rmfamily",
    ]
    for f in r["schema"]["fields"]:
        lines.append(field_row(f))
    lines.append(r"\end{longtable}")

open(out_qmd, "w", encoding="utf-8").write("\n".join(lines))
print(f"Escribí: {out_qmd}")
