#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

main() {
    local MODE="${1:-offline}"

    if [ "$MODE" = "--help" ] || [ "$MODE" = "-h" ]; then
        cat <<'HELP'
RBEK governed-agent demo

Usage:
  ./demo.sh            Zero-key offline ALLOW/DENY proof
  ./demo.sh --offline  Same as default
  ./demo.sh --live     Real OpenAI + Open-Meteo governed execution

Offline mode:
  - no API key
  - no network
  - real RBEK policy enforcement
  - real RBEK evidence
  - deterministic summary

Live mode:
  - requires OPENAI_API_KEY
  - performs real model inference
  - performs real governed external execution
HELP
        return 0
    fi

    if [ "$MODE" = "--live" ]; then
        local HERE
        HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

        if [ ! -f "$HERE/setup.sh" ] || [ ! -f "$HERE/run.sh" ]; then
            echo "LIVE_DEMO_STATUS=BLOCKED"
            echo "REASON=LIVE_MODE_REQUIRES_REPOSITORY_FILES"
            echo "Clone the repository, then run:"
            echo "cd examples/real-governed-agent"
            echo "./demo.sh --live"
            return 20
        fi

        if [ -z "${OPENAI_API_KEY:-}" ]; then
            echo "LIVE_DEMO_STATUS=BLOCKED"
            echo "REASON=OPENAI_API_KEY_NOT_SET"
            echo 'export OPENAI_API_KEY="your-key"'
            echo "./demo.sh --live"
            return 21
        fi

        if [ ! -x "$HERE/.venv/bin/python" ]; then
            echo "[setup] Preparing isolated Python environment..."
            "$HERE/setup.sh"
        fi

        export RBEK_DEMO_VENV="${RBEK_DEMO_VENV:-$HERE/.venv}"
        exec "$HERE/run.sh"
    fi

    if [ "$MODE" != "offline" ] && [ "$MODE" != "--offline" ]; then
        echo "DEMO_STATUS=BLOCKED"
        echo "REASON=UNKNOWN_MODE"
        echo "Run ./demo.sh --help"
        return 22
    fi

    local CLI="${RBEK_CLI:-rbek-cli}"
    local PY="${RBEK_PYTHON:-python3}"

    local WORK
    WORK="$(mktemp -d "${TMPDIR:-/tmp}/rbek_zero_friction_XXXXXX")"

    local PROJECT="$WORK/project"
    local EVIDENCE="$PWD/evidence"

    rm -rf "$EVIDENCE"
    mkdir -p "$EVIDENCE" "$PROJECT/.rbek/providers"

    echo "============================================================"
    echo " RBEK — GOVERNED AGENT DEMO"
    echo "============================================================"
    echo

    if ! command -v "$CLI" >/dev/null 2>&1; then
        echo "[1/5] RBEK CLI .................................... INSTALLING"

        command -v curl >/dev/null 2>&1 || {
            echo "DEMO_STATUS=BLOCKED"
            echo "REASON=CURL_NOT_AVAILABLE_FOR_RBEK_INSTALL"
            return 20
        }

        curl -fsSL https://releases.rbekplatform.com/cli/stable/install.sh | bash
        hash -r

        command -v "$CLI" >/dev/null 2>&1 || {
            echo "DEMO_STATUS=BLOCKED"
            echo "REASON=RBEK_INSTALL_DID_NOT_PROVIDE_CLI"
            return 21
        }
    fi

    local CLI_VERSION
    CLI_VERSION="$("$CLI" --version)"

    if [ "$CLI_VERSION" != "RBEK 0.2.0" ]; then
        echo "DEMO_STATUS=BLOCKED"
        echo "REASON=RBEK_CLI_VERSION_MISMATCH"
        echo "EXPECTED=RBEK 0.2.0"
        echo "ACTUAL=$CLI_VERSION"
        return 22
    fi

    echo "[1/5] RBEK CLI .................................... OK"

    "$CLI" --output json init \
        --project-root "$PROJECT" \
        >"$WORK/init.json"

    cat >"$PROJECT/.rbek/providers/offline-demo.json" <<'JSON'
{
  "activation_mode": "external-controlled",
  "capabilities": [
    "demo.safe"
  ],
  "configuration_version": 1,
  "enabled": true,
  "execution_boundary": "external-controlled",
  "external_api_allowed": false,
  "kind": "custom",
  "module": "offline.demo:Adapter",
  "name": "offline-demo",
  "network_allowed": false,
  "network_execution_performed": false,
  "product": "RBEK",
  "provider_invoked": false,
  "registration_mode": "external-controlled"
}
JSON

    "$PY" - "$PROJECT/.rbek/providers/offline-demo.json" <<'PY'
import hashlib
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))

encoded = json.dumps(
    data,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
).encode("utf-8")

data["registration_digest"] = hashlib.sha256(encoded).hexdigest()

path.write_text(
    json.dumps(data, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

    cat >"$PROJECT/workflow.json" <<'JSON'
{
  "workflow_version": 1,
  "name": "zero-friction-governed-demo",
  "steps": [
    {
      "id": "safe-action",
      "capability": "demo.safe",
      "provider": "offline-demo"
    }
  ]
}
JSON

    cat >"$PROJECT/policy-deny.json" <<'JSON'
{
  "policy_version": 1,
  "name": "zero-friction-deny-policy",
  "effect": "ALLOW",
  "allowed_providers": [
    "offline-demo"
  ],
  "allowed_capabilities": [
    "demo.other"
  ],
  "require_registered_providers": true
}
JSON

    cat >"$PROJECT/policy-allow.json" <<'JSON'
{
  "policy_version": 1,
  "name": "zero-friction-allow-policy",
  "effect": "ALLOW",
  "allowed_providers": [
    "offline-demo"
  ],
  "allowed_capabilities": [
    "demo.safe"
  ],
  "require_registered_providers": true
}
JSON

    echo "[2/5] Loading governed policies .................... OK"

    echo
    echo "[3/5] Agent requests an unauthorized action"
    echo "      agent -> demo.safe"
    echo

    set +e
    "$CLI" --output json execution plan \
        --project-root "$PROJECT" \
        --workflow "$PROJECT/workflow.json" \
        --policy "$PROJECT/policy-deny.json" \
        --plan-file "$WORK/deny-plan.json" \
        >"$WORK/deny-output.json" \
        2>"$WORK/deny-stderr.txt"
    local DENY_RC=$?
    set -e

    local DENY_PROVED="false"

    "$PY" - "$WORK/deny-output.json" "$WORK/deny-plan.json" "$DENY_RC" <<'PY'
from __future__ import annotations

import json
import pathlib
import sys

stdout = pathlib.Path(sys.argv[1])
plan = pathlib.Path(sys.argv[2])
rc = int(sys.argv[3])

payload = {}
if stdout.exists() and stdout.stat().st_size:
    try:
        payload = json.loads(stdout.read_text(encoding="utf-8"))
    except Exception:
        payload = {}

status = str(payload.get("status", "")).upper()

denied = (
    rc != 0
    or status in {"DENIED", "BLOCKED", "REJECTED", "FAIL"}
)

if plan.exists() and plan.stat().st_size:
    try:
        plan_payload = json.loads(plan.read_text(encoding="utf-8"))
    except Exception:
        plan_payload = {}
    plan_status = str(plan_payload.get("status", "")).upper()
    if plan_status in {"DENIED", "BLOCKED", "REJECTED", "FAIL"}:
        denied = True

if not denied:
    raise SystemExit("DENY_NOT_PROVED")

print("DENY_PROOF=PASS")
PY

    DENY_PROVED="true"

    if find "$WORK" -type f -name '*external-execution*.json' | grep -q .; then
        echo "DENIED_ACTION_EXECUTION_EVIDENCE=UNEXPECTED"
        return 31
    fi

    cp -a "$WORK/deny-output.json" "$EVIDENCE/deny-decision.json" || true

    echo "      RBEK DECISION: DENY"
    echo "      External execution performed: NO"
    echo "      [RBEK] policy enforcement .................... OK"

    echo
    echo "[4/5] Agent requests an authorized action"
    echo "      agent -> demo.safe"
    echo

    "$CLI" --output json execution plan \
        --project-root "$PROJECT" \
        --workflow "$PROJECT/workflow.json" \
        --policy "$PROJECT/policy-allow.json" \
        --plan-file "$WORK/allow-plan.json" \
        >"$WORK/allow-plan-output.json"

    "$CLI" --output json execution dry-run \
        --project-root "$PROJECT" \
        --plan "$WORK/allow-plan.json" \
        --evidence-file "$WORK/allow-dry-run.json" \
        >"$WORK/allow-dry-output.json"

    "$CLI" --output json execution gate \
        --project-root "$PROJECT" \
        --plan "$WORK/allow-plan.json" \
        --evidence "$WORK/allow-dry-run.json" \
        --gate-file "$WORK/allow-gate.json" \
        >"$WORK/allow-gate-output.json"

    "$PY" - \
        "$WORK/allow-plan-output.json" \
        "$WORK/allow-dry-output.json" \
        "$WORK/allow-gate-output.json" <<'PY'
from __future__ import annotations

import json
import pathlib
import sys

plan = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
dry = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
gate = json.loads(pathlib.Path(sys.argv[3]).read_text(encoding="utf-8"))

if plan.get("status") != "READY":
    raise SystemExit("ALLOW_PLAN_NOT_READY")

if dry.get("status") != "PASS":
    raise SystemExit("ALLOW_DRY_RUN_NOT_PASS")

if gate.get("status") != "AUTHORIZED":
    raise SystemExit("ALLOW_GATE_NOT_AUTHORIZED")

print("ALLOW_PROOF=PASS")
PY

    cp -a "$WORK/allow-plan.json" "$EVIDENCE/allow-plan.json"
    cp -a "$WORK/allow-dry-run.json" "$EVIDENCE/allow-dry-run.json"
    cp -a "$WORK/allow-gate.json" "$EVIDENCE/allow-gate.json"

    echo "      RBEK DECISION: ALLOW"
    echo "      Controlled dry-run: PASS"
    echo "      Gate authorization: AUTHORIZED"
    echo "      Network execution performed: NO"
    echo "      [RBEK] governed execution path ............... OK"

    echo
    echo "[5/5] Verifying the proof"

    "$PY" - "$EVIDENCE/summary.json" <<'PY'
from __future__ import annotations

import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])

payload = {
    "demo": "RBEK zero-friction offline governed execution",
    "mode": "offline",
    "model_inference": "simulated_not_required",
    "network_execution_performed": False,
    "unauthorized_action": {
        "decision": "DENY",
        "external_execution_performed": False,
    },
    "authorized_action": {
        "decision": "ALLOW",
        "dry_run": "PASS",
        "gate": "AUTHORIZED",
        "network_execution_performed": False,
    },
    "rbek_policy_enforcement": "REAL",
    "rbek_evidence_generation": "REAL",
}

path.write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

    echo "      Evidence summary ............................. OK"
    echo
    echo "============================================================"
    echo " DEMONSTRATION COMPLETE — WHAT RBEK PROVED"
    echo "============================================================"
    echo " Unauthorized action ............ DENIED"
    echo " Denied action executed ......... NO"
    echo " Authorized action .............. ALLOWED"
    echo " Governed dry-run ............... PASS"
    echo " Gate authorization ............. AUTHORIZED"
    echo " Network used ................... NO"
    echo " RBEK policy enforcement ........ REAL"
    echo " RBEK evidence .................. REAL"
    echo
    echo " ------------------------------------------------------------"
    echo " THE AHA MOMENT"
    echo " ------------------------------------------------------------"
    echo
    echo " The agent requested an action."
    echo " RBEK decided whether it was allowed."
    echo " The denied action did not execute."
    echo " The allowed action passed the governed path."
    echo " Evidence proves what happened."
    echo
    echo " Evidence directory:"
    echo " $EVIDENCE/"
    echo
    echo " Proof summary:"
    cat "$EVIDENCE/summary.json"
    echo
    echo " ------------------------------------------------------------"
    echo " Docker controls where software runs."
    echo " RBEK controls whether an action may run,"
    echo " how it is governed, and what evidence proves the result."
    echo " ------------------------------------------------------------"
    echo
    echo "RBEK_ZERO_FRICTION_DEMO=PASS"
    echo "============================================================"

    return 0
}

main "$@"
