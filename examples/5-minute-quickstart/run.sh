#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="${1:-./rbek-demo}"

if ! command -v rbek-cli >/dev/null 2>&1; then
    echo "RBEK CLI is not installed."
    echo "Install it with:"
    echo "curl -fsSL https://releases.rbekplatform.com/cli/stable/install.sh | bash"
    exit 1
fi

echo "== RBEK version =="
rbek-cli --version

echo
echo "== RBEK doctor =="
rbek-cli doctor

echo
echo "== Initialize project =="
rbek-cli init "$PROJECT_DIR"

echo
echo "== Run project =="
rbek-cli run "$PROJECT_DIR"

echo
echo "RBEK 5-minute Developer quickstart completed."
