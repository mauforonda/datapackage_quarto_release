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
    r"\BrandRuleAccentTop",
    r"\begin{BrandMeta}",
    rf"\MetaItem{{Título}}{{{tex_escape(title)}}}",
    rf"\MetaItem{{Paquete}}{{{tex_escape(pkg_name)}}}",
    rf"\MetaItem{{Versión}}{{{tex_escape(version)}}}",
    r"\end{BrandMeta}",
    r"\BrandRuleAccentBottom",
    "",
    "## Recursos",
    "",
]

for r in dp["resources"]:
    resource_title = tex_escape(r.get("title", r.get("name", "")))
    res_name = tex_escape(r.get("name", ""))
    res_type = tex_escape(r.get("type", ""))
    res_path = tex_escape(r.get("path", ""))
    res_format = tex_escape(r.get("format", ""))
    res_mediatype = tex_escape(r.get("mediatype", ""))
    res_encoding = tex_escape(r.get("encoding", ""))
    lines += [
        r"\begin{ResourceBlock}",
        rf"\ResourceTitle{{{resource_title}}}",
        "",
        rf"\textbf{{Nombre:}} \texttt{{{res_name}}}\\",
        rf"\textbf{{Tipo:}} \texttt{{{res_type}}}\\",
        rf"\textbf{{Documento:}} \texttt{{{res_path}}}\\",
        rf"\textbf{{Formato:}} \texttt{{{res_format}}}\\",
        rf"\textbf{{Extensión:}} \texttt{{{res_mediatype}}}\\",
        rf"\textbf{{Codificación:}} \texttt{{{res_encoding}}}",
        "",
        r"\paragraph{Esquema}",
        "",
        r"\begin{longtable*}{@{}p{0.26\linewidth}p{0.16\linewidth}p{0.52\linewidth}@{}}",
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
    lines.append(r"\end{longtable*}")
    lines.append(r"\end{ResourceBlock}")

open(out_qmd, "w", encoding="utf-8").write("\n".join(lines))
print(f"Escribí: {out_qmd}")
