#!/usr/bin/env bash
# Run the same checks CI runs (.github/workflows/ci.yml), from any cwd.
#
# Suites whose dependencies aren't installed are SKIPPED with a loud notice
# instead of failing — CI always runs everything, so a local skip is a gap
# in your confidence, not a pass.
#
#   deps: pip install -r src/crystal-core/requirements-starline.txt   # starline
#         pip install -r src/apps/lumina/requirements.txt pytest      # test suites

set -u
cd "$(dirname "$0")/../.."

PY="${PYTHON:-python3}"
failed=0
skipped=0

run() { # run <label> <command...>
  local label="$1"; shift
  echo "==> ${label}"
  if "$@"; then echo "    OK"; else echo "    FAILED: ${label}"; failed=1; fi
}

skip() { # skip <label> <how to enable>
  echo "==> ${label}"
  echo "    SKIPPED — $2 (CI will run this)"
  skipped=1
}

run "compileall (src tests archive)" "$PY" -m compileall -q src tests archive

( cd src/crystal-core
  run "Starline Weaver self-test" "$PY" -m clementine.bridge.selftest
  run "pipeline self-test"        "$PY" -m services.selftest
  run "RDP self-test"             "$PY" -m rdp.selftest
) || failed=1

if "$PY" -c "import cryptography" 2>/dev/null; then
  ( cd src/crystal-core && run "Starline self-test" "$PY" -m starline.selftest ) || failed=1
else
  skip "Starline self-test" "needs: pip install -r src/crystal-core/requirements-starline.txt"
fi

if "$PY" -c "import pytest" 2>/dev/null; then
  if "$PY" -c "import flask, requests" 2>/dev/null; then
    run "Lumina core tests" "$PY" -m pytest src/apps/lumina/tests -q
  else
    skip "Lumina core tests" "needs: pip install -r src/apps/lumina/requirements.txt"
  fi
  run "mesh stub tests" "$PY" -m pytest tests -q
else
  skip "Lumina core tests" "needs: pip install pytest"
  skip "mesh stub tests"   "needs: pip install pytest"
fi

echo
if [ "$failed" -ne 0 ]; then
  echo "RESULT: checks FAILED — fix before pushing."
  exit 1
elif [ "$skipped" -ne 0 ]; then
  echo "RESULT: checks passed, with skips — install the deps above for full local confidence."
else
  echo "RESULT: all checks passed."
fi
