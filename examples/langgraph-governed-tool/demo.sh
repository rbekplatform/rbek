#!/usr/bin/env bash
set -Eeuo pipefail

HERE="$(
    cd "$(dirname "${BASH_SOURCE[0]}")"
    pwd
)"

if ! command -v rbek-cli >/dev/null 2>&1; then
    echo "RBEK CLI is required."
    echo
    echo "Install the official RBEK CLI first:"
    echo "curl -fsSL https://releases.rbekplatform.com/cli/stable/install.sh | bash"
    exit 20
fi

if [ "$(rbek-cli --version)" != "RBEK 0.2.0" ]; then
    echo "Expected RBEK 0.2.0."
    exit 21
fi

VENV="${RBEK_LANGGRAPH_VENV:-$HERE/.venv}"

if [ ! -x "$VENV/bin/python" ]; then
    python3 -m venv "$VENV"
fi

"$VENV/bin/pip" \
    --disable-pip-version-check \
    install \
    -r "$HERE/requirements.txt"

PYTHONPATH="${PYTHONPATH:-}" \
"$VENV/bin/python" \
    "$HERE/demo.py" \
    "$@"
