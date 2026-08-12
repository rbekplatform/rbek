#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

main() {
    local HERE
    HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    local VENV="${RBEK_DEMO_VENV:-$HERE/.venv}"
    local PY="$VENV/bin/python"

    if ! command -v rbek-cli >/dev/null 2>&1; then
        echo "DEMO_STATUS=BLOCKED"
        echo "REASON=RBEK_CLI_NOT_INSTALLED"
        echo
        echo "Install RBEK first:"
        echo "curl -fsSL https://releases.rbekplatform.com/cli/stable/install.sh | bash"
        return 20
    fi

    if [ ! -x "$PY" ]; then
        echo "DEMO_STATUS=BLOCKED"
        echo "REASON=DEMO_VENV_NOT_READY"
        echo "Run: ./setup.sh"
        return 21
    fi

    if [ -z "${OPENAI_API_KEY:-}" ]; then
        echo "DEMO_STATUS=BLOCKED"
        echo "REASON=OPENAI_API_KEY_NOT_SET"
        echo "Export OPENAI_API_KEY in your shell before running."
        return 22
    fi

    export PYTHONPATH="$HERE${PYTHONPATH:+:$PYTHONPATH}"

    exec "$PY" "$HERE/run.py"
}

main "$@"
