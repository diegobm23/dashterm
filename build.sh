#!/usr/bin/env bash
# Build a single-file, dependency-free executable using the stdlib `zipapp`
# module. The result, dist/dashterm, runs anywhere with python3 on PATH.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

mkdir -p dist
python3 -m zipapp src \
    --output dist/dashterm \
    --python "/usr/bin/env python3" \
    --main "dashterm.cli:main"
chmod +x dist/dashterm

echo "✓ Built dist/dashterm"
