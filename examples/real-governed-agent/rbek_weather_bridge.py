from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import tempfile
from typing import Any


RBEK_CLI = "rbek-cli"

MODULE_REFERENCE = (
    "rbek.cli.promoted_adapters."
    "open_meteo.adapter:"
    "OpenMeteoAdapter"
)


class GovernedWeatherError(
    RuntimeError
):
    pass


def _run_json(
    arguments: list[str],
) -> dict[str, Any]:
    completed = subprocess.run(
        [
            RBEK_CLI,
            "--output",
            "json",
            *arguments,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if completed.returncode != 0:
        raise GovernedWeatherError(
            json.dumps(
                {
                    "returncode": (
                        completed.returncode
                    ),
                    "stdout": (
                        completed.stdout
                    ),
                    "stderr": (
                        completed.stderr
                    ),
                },
                sort_keys=True,
            )
        )

    try:
        payload = json.loads(
            completed.stdout
        )
    except json.JSONDecodeError as exc:
        raise GovernedWeatherError(
            "RBEK_INVALID_JSON_OUTPUT"
        ) from exc

    if not isinstance(
        payload,
        dict,
    ):
        raise GovernedWeatherError(
            "RBEK_OUTPUT_NOT_OBJECT"
        )

    return payload


def _write_json(
    path: pathlib.Path,
    payload: dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def governed_current_weather(
    *,
    latitude: float,
    longitude: float,
) -> dict[str, Any]:
    if isinstance(
        latitude,
        bool,
    ) or not isinstance(
        latitude,
        (int, float),
    ):
        raise ValueError(
            "latitude must be numeric"
        )

    if isinstance(
        longitude,
        bool,
    ) or not isinstance(
        longitude,
        (int, float),
    ):
        raise ValueError(
            "longitude must be numeric"
        )

    if not (
        -90.0
        <= float(latitude)
        <= 90.0
    ):
        raise ValueError(
            "latitude out of range"
        )

    if not (
        -180.0
        <= float(longitude)
        <= 180.0
    ):
        raise ValueError(
            "longitude out of range"
        )

    workspace = pathlib.Path(
        tempfile.mkdtemp(
            prefix=(
                "rbek_weather_agent_"
            )
        )
    )

    project = (
        workspace
        / "project"
    )

    evidence = (
        project
        / ".rbek"
        / "evidence"
    )

    providers = (
        project
        / ".rbek"
        / "providers"
    )

    project.mkdir(
        parents=True,
        exist_ok=True,
    )

    _run_json(
        [
            "init",
            "--project-root",
            str(project),
        ]
    )

    evidence.mkdir(
        parents=True,
        exist_ok=True,
    )

    providers.mkdir(
        parents=True,
        exist_ok=True,
    )

    provider_payload: dict[str, Any] = {
        "activation_mode": (
            "external-controlled"
        ),

        "capabilities": [
            "weather.current",
        ],

        "configuration_version": 1,

        "enabled": True,

        "execution_boundary": (
            "external-controlled"
        ),

        "external_api_allowed": True,

        "kind": "custom",

        "module": MODULE_REFERENCE,

        "name": "open-meteo",

        "network_allowed": True,

        "network_execution_performed": False,

        "product": "RBEK",

        "provider_invoked": False,

        "registration_mode": (
            "external-controlled"
        ),
    }

    encoded = json.dumps(
        provider_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    provider_payload[
        "registration_digest"
    ] = hashlib.sha256(
        encoded
    ).hexdigest()

    _write_json(
        providers
        / "open-meteo.json",
        provider_payload,
    )

    workflow = {
        "workflow_version": 1,

        "name": (
            "real-agent-open-meteo-workflow"
        ),

        "steps": [
            {
                "id": "current-weather",

                "capability": (
                    "weather.current"
                ),

                "provider": (
                    "open-meteo"
                ),
            }
        ],
    }

    policy = {
        "policy_version": 1,

        "name": (
            "real-agent-open-meteo-policy"
        ),

        "effect": "ALLOW",

        "allowed_providers": [
            "open-meteo",
        ],

        "allowed_capabilities": [
            "weather.current",
        ],

        "require_registered_providers": True,
    }

    workflow_path = (
        project
        / "workflow.json"
    )

    policy_path = (
        project
        / "policy.json"
    )

    _write_json(
        workflow_path,
        workflow,
    )

    _write_json(
        policy_path,
        policy,
    )

    plan_path = (
        evidence
        / "execution-plan.json"
    )

    dry_path = (
        evidence
        / "dry-run.json"
    )

    gate_path = (
        evidence
        / "execution-gate.json"
    )

    execution_path = (
        evidence
        / "external-execution.json"
    )

    receipt_path = (
        evidence
        / "execution-receipt.json"
    )

    certification_path = (
        evidence
        / "promoted-execution-certification.json"
    )

    plan = _run_json(
        [
            "execution",
            "plan",

            "--project-root",
            str(project),

            "--workflow",
            str(workflow_path),

            "--policy",
            str(policy_path),

            "--plan-file",
            str(plan_path),
        ]
    )

    if plan.get(
        "status"
    ) != "READY":
        raise GovernedWeatherError(
            "PLAN_NOT_READY"
        )

    dry = _run_json(
        [
            "execution",
            "dry-run",

            "--project-root",
            str(project),

            "--plan",
            str(plan_path),

            "--evidence-file",
            str(dry_path),
        ]
    )

    if dry.get(
        "status"
    ) != "PASS":
        raise GovernedWeatherError(
            "DRY_RUN_FAILED"
        )

    gate = _run_json(
        [
            "execution",
            "gate",

            "--project-root",
            str(project),

            "--plan",
            str(plan_path),

            "--evidence",
            str(dry_path),

            "--gate-file",
            str(gate_path),
        ]
    )

    if gate.get(
        "status"
    ) != "AUTHORIZED":
        raise GovernedWeatherError(
            "GATE_NOT_AUTHORIZED"
        )

    message = json.dumps(
        {
            "latitude": float(
                latitude
            ),

            "longitude": float(
                longitude
            ),
        },
        sort_keys=True,
        separators=(",", ":"),
    )

    execution = _run_json(
        [
            "execution",
            "external-run",

            "--project-root",
            str(project),

            "--plan",
            str(plan_path),

            "--gate",
            str(gate_path),

            "--message",
            message,

            "--evidence-file",
            str(execution_path),

            "--acknowledge-external-execution",
        ]
    )

    if execution.get(
        "status"
    ) != "PASS":
        raise GovernedWeatherError(
            "EXECUTION_FAILED"
        )

    _run_json(
        [
            "receipt",
            "create",

            "--evidence",
            str(execution_path),

            "--receipt-file",
            str(receipt_path),
        ]
    )

    receipt_verify = _run_json(
        [
            "receipt",
            "verify",

            "--file",
            str(receipt_path),
        ]
    )

    if receipt_verify.get(
        "valid"
    ) is not True:
        raise GovernedWeatherError(
            "RECEIPT_INVALID"
        )

    certification = _run_json(
        [
            "execution",
            "certify-promoted",

            "--project-root",
            str(project),

            "--adapter",
            "open-meteo",

            "--plan",
            str(plan_path),

            "--gate",
            str(gate_path),

            "--execution-evidence",
            str(execution_path),

            "--receipt",
            str(receipt_path),

            "--certification-file",
            str(certification_path),
        ]
    )

    if certification.get(
        "status"
    ) != "CERTIFIED":
        raise GovernedWeatherError(
            "CERTIFICATION_FAILED"
        )

    cert_verify = _run_json(
        [
            "evidence",
            "verify-promoted",

            "--file",
            str(certification_path),
        ]
    )

    if cert_verify.get(
        "valid"
    ) is not True:
        raise GovernedWeatherError(
            "CERTIFICATION_INVALID"
        )

    results = execution.get(
        "results"
    )

    if not isinstance(
        results,
        list,
    ) or len(results) != 1:
        raise GovernedWeatherError(
            "RESULT_COUNT_INVALID"
        )

    result = results[0]

    if not isinstance(
        result,
        dict,
    ):
        raise GovernedWeatherError(
            "RESULT_INVALID"
        )

    output = result.get(
        "output"
    )

    if not isinstance(
        output,
        dict,
    ):
        raise GovernedWeatherError(
            "OUTPUT_INVALID"
        )

    current = output.get(
        "current"
    )

    if not isinstance(
        current,
        dict,
    ):
        raise GovernedWeatherError(
            "CURRENT_WEATHER_MISSING"
        )

    return {
        "product": "RBEK",

        "provider": "open-meteo",

        "third_party_host": (
            "api.open-meteo.com"
        ),

        "execution_id": (
            execution.get(
                "execution_id"
            )
        ),

        "execution_mode": (
            execution.get(
                "execution_mode"
            )
        ),

        "network_execution_performed": (
            execution.get(
                "network_execution_performed"
            )
        ),

        "external_api_execution_performed": (
            execution.get(
                "external_api_execution_performed"
            )
        ),

        "database_execution_performed": (
            execution.get(
                "database_execution_performed"
            )
        ),

        "current": current,

        "timezone": output.get(
            "timezone"
        ),

        "receipt_valid": True,

        "certification_valid": True,

        "evidence_workspace": str(
            workspace
        ),
    }


def governed_current_weather_json(
    latitude: float,
    longitude: float,
) -> str:
    return json.dumps(
        governed_current_weather(
            latitude=latitude,
            longitude=longitude,
        ),
        sort_keys=True,
        separators=(",", ":"),
    )
