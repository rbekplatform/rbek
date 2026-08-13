from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import tempfile

from crew import build_crewai_reference
from governed_tool import (
    RBEKExecutionContext,
    RBEKGovernedWeatherTool,
)


LATITUDE = 32.6500
LONGITUDE = -16.9080

OPEN_METEO_MODULE = (
    "rbek.cli.promoted_adapters.open_meteo.adapter:"
    "OpenMeteoAdapter"
)


def write_json(
    path: pathlib.Path,
    payload: dict,
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


def run_rbek(
    args: list[str],
) -> tuple[int, dict]:
    import subprocess

    completed = subprocess.run(
        [
            "rbek-cli",
            "--output",
            "json",
            *args,
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    raw = completed.stdout.strip()

    if not raw:
        raise RuntimeError(
            "RBEK returned no JSON output: "
            + completed.stderr.strip()
        )

    payload = json.loads(raw)

    if not isinstance(payload, dict):
        raise RuntimeError(
            "RBEK output was not a JSON object"
        )

    return completed.returncode, payload


def build_project(
    root: pathlib.Path,
) -> tuple[pathlib.Path, pathlib.Path]:
    project = root / "project"

    rc, payload = run_rbek(
        [
            "init",
            "--project-root",
            str(project),
        ]
    )

    if rc != 0:
        raise RuntimeError(
            "RBEK init failed: "
            + json.dumps(payload)
        )

    evidence = project / ".rbek" / "evidence"
    providers = project / ".rbek" / "providers"

    evidence.mkdir(
        parents=True,
        exist_ok=True,
    )

    providers.mkdir(
        parents=True,
        exist_ok=True,
    )

    provider = {
        "activation_mode": "external-controlled",
        "capabilities": [
            "weather.current",
        ],
        "configuration_version": 1,
        "enabled": True,
        "execution_boundary": "external-controlled",
        "external_api_allowed": True,
        "kind": "custom",
        "module": OPEN_METEO_MODULE,
        "name": "open-meteo",
        "network_allowed": True,
        "network_execution_performed": False,
        "product": "RBEK",
        "provider_invoked": False,
        "registration_mode": "external-controlled",
    }

    encoded = json.dumps(
        provider,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    provider["registration_digest"] = hashlib.sha256(
        encoded
    ).hexdigest()

    workflow = {
        "workflow_version": 1,
        "name": "crewai-open-meteo",
        "steps": [
            {
                "id": "current-weather",
                "capability": "weather.current",
                "provider": "open-meteo",
            }
        ],
    }

    policy = {
        "policy_version": 1,
        "name": "crewai-open-meteo-policy",
        "effect": "ALLOW",
        "allowed_providers": [
            "open-meteo",
        ],
        "allowed_capabilities": [
            "weather.current",
        ],
        "require_registered_providers": True,
    }

    write_json(
        providers / "open-meteo.json",
        provider,
    )

    write_json(
        project / "workflow.json",
        workflow,
    )

    write_json(
        project / "policy.json",
        policy,
    )

    plan = evidence / "execution-plan.json"
    dry = evidence / "dry-run.json"
    gate = evidence / "execution-gate.json"

    rc, payload = run_rbek(
        [
            "execution",
            "plan",
            "--project-root",
            str(project),
            "--workflow",
            str(project / "workflow.json"),
            "--policy",
            str(project / "policy.json"),
            "--plan-file",
            str(plan),
        ]
    )

    if rc != 0 or payload.get("status") != "READY":
        raise RuntimeError(
            "RBEK plan failed: "
            + json.dumps(payload)
        )

    rc, payload = run_rbek(
        [
            "execution",
            "dry-run",
            "--project-root",
            str(project),
            "--plan",
            str(plan),
            "--evidence-file",
            str(dry),
        ]
    )

    if rc != 0 or payload.get("status") != "PASS":
        raise RuntimeError(
            "RBEK dry-run failed: "
            + json.dumps(payload)
        )

    rc, payload = run_rbek(
        [
            "execution",
            "gate",
            "--project-root",
            str(project),
            "--plan",
            str(plan),
            "--evidence",
            str(dry),
            "--gate-file",
            str(gate),
        ]
    )

    if rc != 0 or payload.get("status") != "AUTHORIZED":
        raise RuntimeError(
            "RBEK gate failed: "
            + json.dumps(payload)
        )

    return plan, gate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--allow",
        action="store_true",
        help=(
            "Use the authorized gate instead of the "
            "deterministic deny gate."
        ),
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    mode = "ALLOW" if args.allow else "DENY"

    with tempfile.TemporaryDirectory(
        prefix="rbek_crewai_reference_"
    ) as temp:
        root = pathlib.Path(temp)
        project = root / "project"

        plan, allow_gate = build_project(
            root
        )

        evidence = project / ".rbek" / "evidence"

        if mode == "ALLOW":
            gate = allow_gate
        else:
            gate = evidence / "execution-gate-deny.json"

            payload = json.loads(
                allow_gate.read_text(
                    encoding="utf-8"
                )
            )

            payload["plan_digest"] = "0" * 64

            write_json(
                gate,
                payload,
            )

        execution_evidence = (
            evidence
            / f"crewai-{mode.lower()}-execution.json"
        )

        tool = RBEKGovernedWeatherTool(
            execution_context=RBEKExecutionContext(
                project_root=project,
                plan=plan,
                gate=gate,
                evidence_file=execution_evidence,
                mode=mode,
            )
        )

        agent, task, crew = build_crewai_reference(
            tool
        )

        assert len(agent.tools) == 1
        assert agent.tools[0].name == "rbek_governed_weather"
        assert len(task.tools) == 1
        assert task.tools[0].name == "rbek_governed_weather"
        assert len(crew.agents) == 1
        assert len(crew.tasks) == 1

        result = tool.run(
            latitude=LATITUDE,
            longitude=LONGITUDE,
        )

        payload = json.loads(result)

        print(
            json.dumps(
                {
                    "framework": "CrewAI",
                    "mode": mode,
                    "agent_class": type(agent).__name__,
                    "task_class": type(task).__name__,
                    "crew_class": type(crew).__name__,
                    "tool_class": type(tool).__name__,
                    "tool_name": tool.name,
                    "latitude": LATITUDE,
                    "longitude": LONGITUDE,
                    "payload": payload,
                },
                indent=2,
                sort_keys=True,
            )
        )

        if mode == "DENY":
            assert payload["status"] == "BLOCKED"
            assert payload["execution_performed"] is False
            assert payload["network_execution_performed"] is False
            assert (
                payload["external_api_execution_performed"]
                is False
            )

            print("REAL_CREWAI_REFERENCE_DENY=PASS")
            print("CREWAI_AGENT_OBJECT=PASS")
            print("CREWAI_TASK_OBJECT=PASS")
            print("CREWAI_CREW_OBJECT=PASS")
            print("CREWAI_BASETOOL_EXECUTION=PASS")
            print("RBEK_DENY_EXECUTION_PERFORMED=FALSE")
            print("RBEK_DENY_NETWORK_EXECUTION_PERFORMED=FALSE")
            print("RBEK_DENY_EXTERNAL_API_EXECUTION_PERFORMED=FALSE")
            print("LLM_INVOCATION_PERFORMED=FALSE")
            return 0

        assert payload["status"] == "PASS"
        assert payload["execution_performed"] is True

        print("REAL_CREWAI_REFERENCE_ALLOW=PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
