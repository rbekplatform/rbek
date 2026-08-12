#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

main() {
    local HERE
    HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local VENV="${RBEK_DEMO_VENV:-$HERE/.venv}"

    command -v python3 >/dev/null 2>&1 || {
        echo "Python 3 is required."
        return 20
    }

    python3 -m venv "$VENV"

    "$VENV/bin/python" -m pip install --upgrade pip
    "$VENV/bin/python" -m pip install -r "$HERE/requirements.txt"

    echo "SETUP_STATUS=PASS"
    echo "VENV=$VENV"
}

main "$@"
