#!/bin/bash
set -e

BUNDLE_DIR=${1:-.}
echo "[INFO] Validating manifest..."
python3 - <<'PY'
import json, jsonschema, sys
schema=json.load(open("manifest.schema.json"))
manifest=json.load(open(f"{sys.argv[1]}/MANIFEST.json" if len(sys.argv)>1 else "MANIFEST.json"))
jsonschema.validate(instance=manifest, schema=schema)
print("[OK] Manifest validated successfully.")
PY $BUNDLE_DIR

echo "[INFO] Running inference on Raspberry Pi (if connected)..."
bash RUN_ON_PI.sh || echo "[WARN] Skipped device run (no Pi connected)."
echo "[INFO] Finished. Results under ./figures and ./logs."
