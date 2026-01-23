#!/usr/bin/env python3

import argparse
import json
import sys

parser = argparse.ArgumentParser()
parser.add_argument("in_json", nargs="?", default="datapackage.json")
parser.add_argument("out_qmd", nargs="?", default="datapackage.qmd")
parser.add_argument("--identity", default="")
parser.add_argument("--project", default="")
args = parser.parse_args()

in_json = args.in_json
out_qmd = args.out_qmd

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
    categories = f.get("categories")
    desc = tex_escape(desc).replace("\n", r"\newline ")
    if categories:
        cat_text = format_categories(categories)
        if cat_text:
            cat_block = (
                r"\vspace{0.05em}\footnotesize"
                r"\begin{itemize}\setlength{\itemsep}{0.15em}\setlength{\parskip}{0pt}\setlength{\parsep}{0pt}\setlength{\topsep}{0pt}\setlength{\partopsep}{0pt}"
                + cat_text
                + r"\end{itemize}\normalsize"
            )
            desc = f"{desc} {cat_block}" if desc else cat_block
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


def format_categories(categories) -> str:
    parts = []
    if isinstance(categories, list):
        for c in categories:
            if isinstance(c, str):
                parts.append(r"\item " + tex_escape(c))
            elif isinstance(c, dict):
                value = (
                    tex_escape(str(c.get("value", "")))
                    if c.get("value") is not None
                    else ""
                )
                label = (
                    tex_escape(str(c.get("label", "")))
                    if c.get("label") is not None
                    else ""
                )
                desc = (
                    tex_escape(str(c.get("description", "")))
                    if c.get("description")
                    else ""
                )
                item = value
                if label:
                    if item:
                        item = f"{item}: \\textit{{{label}}}"
                    else:
                        item = f"\\textit{{{label}}}"
                if desc:
                    item = f"{item} — {desc}" if item else desc
                if item:
                    parts.append(r"\item " + item)
    return " ".join([p for p in parts if p])


def format_sources(sources) -> str:
    parts = []
    if isinstance(sources, list):
        for s in sources:
            if isinstance(s, str):
                parts.append(tex_escape(s))
            elif isinstance(s, dict):
                title = s.get("title") or s.get("name") or s.get("path") or s.get("url") or ""
                title = tex_escape(str(title)) if title is not None else ""
                if title:
                    parts.append(title)
    elif isinstance(sources, str):
        parts.append(tex_escape(sources))
    return "; ".join([p for p in parts if p])


title = dp.get("title", dp.get("name", "Data Package"))
pkg_name = dp.get("name", "")
version = dp.get("version", "")
identity = (args.identity or "").strip()
project = (args.project or "").strip()
sources = dp.get("sources")

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
]
if identity:
    header_path = f"assets/{identity}/header.png"
    lines.append(rf"\BrandHeader{{{header_path}}}")
if project:
    lines.append(rf"\ProjectTitle{{{tex_escape(project)}}}")
lines.append(rf"\PackageTitle{{{tex_escape(title)}}}")
lines += [
    "",
    r"\BrandRuleAccentTop",
    r"\begin{BrandMeta}",
    rf"\MetaItem{{Título}}{{{tex_escape(title)}}}",
    rf"\MetaItem{{Paquete}}{{{tex_escape(pkg_name)}}}",
    rf"\MetaItem{{Versión}}{{{tex_escape(version)}}}",
]
if sources:
    sources_text = format_sources(sources)
    if sources_text:
        lines.append(rf"\MetaItem{{Fuentes}}{{{sources_text}}}")
lines += [
    r"\end{BrandMeta}",
    r"\BrandRuleAccentBottom",
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
    res_desc = tex_escape(r.get("description", ""))
    lines += [
        r"\begin{ResourceBlock}",
        rf"\ResourceTitle{{{resource_title}}}",
        "",
        rf"\hyphenpenalty=10000\exhyphenpenalty=10000\textit{{{res_desc}}}" if res_desc else "",
        "",
        rf"\textbf{{Nombre:}} \texttt{{{res_name}}}\\",
        rf"\textbf{{Tipo:}} \texttt{{{res_type}}}\\",
        rf"\textbf{{Documento:}} \texttt{{{res_path}}}\\",
        rf"\textbf{{Formato:}} \texttt{{{res_format}}}\\",
        rf"\textbf{{Extensión:}} \texttt{{{res_mediatype}}}\\",
        rf"\textbf{{Codificación:}} \texttt{{{res_encoding}}}",
        "",
        r"\vspace{1.2em}",
        r"\begin{longtable*}{@{}p{0.26\linewidth}p{0.16\linewidth}p{0.52\linewidth}@{}}",
        r"\rowcolor{OrnamentLight} \textbf{Campo} & \textbf{Tipo} & \textbf{Descripción} \\",
        r"\addlinespace[0.6em]",
        r"\endfirsthead",
        r"\normalfont\normalsize\rmfamily",
    ]
    for f in r["schema"]["fields"]:
        lines.append(field_row(f))
    lines.append(r"\end{longtable*}")
    lines.append(r"\end{ResourceBlock}")

open(out_qmd, "w", encoding="utf-8").write("\n".join(lines))
print(f"Escribí: {out_qmd}")
