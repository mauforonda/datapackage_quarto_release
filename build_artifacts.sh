#!/usr/bin/env bash
set -euo pipefail

datapackage_path="${1:-datapackage.json}"
identity="${2:-}"
project="${3:-}"
build_root="${4:-build}"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

qmd_dir="${build_root}/qmd"
pdf_dir="${build_root}/pdf"
dist_dir="${build_root}/dist"

rm -rf "$build_root"
mkdir -p "$qmd_dir" "$pdf_dir" "$dist_dir"

cp "${script_dir}/linea.tex" "$qmd_dir/"
if [ -d "${script_dir}/fonts" ]; then
  cp -R "${script_dir}/fonts" "$qmd_dir/"
fi
if [ -d "${script_dir}/assets" ]; then
  cp -R "${script_dir}/assets" "$qmd_dir/"
fi

python "${script_dir}/datapackage2md.py" "$datapackage_path" "$qmd_dir" --identity "$identity" --project "$project"

python - "$datapackage_path" <<'PY' | while IFS=$'\t' read -r name path; do
import json
import sys

dp = json.load(open(sys.argv[1], "r", encoding="utf-8"))
for r in dp.get("resources", []):
    name = r.get("name", "")
    path = r.get("path", "")
    if name and path:
        print(f"{name}\t{path}")
PY
  qmd="${qmd_dir}/${name}.qmd"
  if [ ! -f "$qmd" ]; then
    echo "Missing QMD for resource ${name}: ${qmd}" >&2
    exit 1
  fi

  (cd "$qmd_dir" && quarto render "${name}.qmd" --to pdf)

  pdf="${qmd%.qmd}.pdf"
  if [ ! -f "$pdf" ]; then
    echo "Missing PDF for resource ${name}: ${pdf}" >&2
    exit 1
  fi

  mv "$pdf" "${pdf_dir}/${name}.pdf"
  zip -j "${dist_dir}/${name}.zip" "${pdf_dir}/${name}.pdf" "${path}"
done
