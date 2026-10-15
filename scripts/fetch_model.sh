#!/usr/bin/env bash
# Sparse-checkout the Merdith et al. 2021 model files (CC BY 4.0) from the GPlates Web Service repo.
set -euo pipefail
cd "$(dirname "$0")/.."
TMP=$(mktemp -d)
git clone --depth 1 --filter=blob:none --no-checkout -q https://github.com/GPlates/gplates-web-service.git "$TMP/gws"
cd "$TMP/gws"
git sparse-checkout set --no-cone 'django/GWS/data/deprecated/MODELS/MERDITH2021/*'
git checkout -q
cd - >/dev/null
mkdir -p data/MERDITH2021
cp "$TMP"/gws/django/GWS/data/deprecated/MODELS/MERDITH2021/* data/MERDITH2021/
rm -rf "$TMP"
ls -la data/MERDITH2021
