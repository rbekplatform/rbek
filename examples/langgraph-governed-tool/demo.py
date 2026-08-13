from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import tempfile
from dataclasses import dataclass

from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langgraph.graph import (
    END,
    START,
    MessagesState,
    StateGraph,
)
from langgraph.prebuilt import ToolNode


RBEK_CLI = "rbek-cli"

LATITUDE = 32.6500
LONGITUDE = -16.9080

OPEN_METEO_MODULE = (
    "rbek.cli.promoted_adapters.open_meteo.adapter:"
    "OpenMeteoAdapter"
)


@dataclass(frozen=True)
class ExecutionContext:
    project_root: pathlib.Path
    plan: pathlib.Path
    gate: pathlib.Path
    evidence: pathlib.Path
    mode: str


_context: ExecutionContext | None = None


def run_rbek(
    arguments: list[str],
) -> tuple[int, dict]:
    completed = subprocess.run(
        [
            RBEK_CLI,
            "--output",
            "json",
            *arguments,
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
            "RBEK response was not a JSON object"
        )

    return completed.returncode, payload


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


def configure(
    context: ExecutionContext,
) -> None:
    global _context
    _context = context


@tool
def governed_weather(
    latitude: float,
    longitude: float,
) -> str:
    """Get current weather through the RBEK governed execution boundary."""

    if _context is None:
        raise RuntimeError(
            "RBEK execution context not configured"
        )

    message = json.dumps(
        {
            "latitude": float(latitude),
            "longitude": float(longitude),
        },
        sort_keys=True,
        separators=(",", ":"),
    )

    rc, execution = run_rbek(
        [
            "execution",
            "external-run",
            "--project-root",
            str(_context.project_root),
            "--plan",
            str(_context.plan),
            "--gate",
            str(_context.gate),
            "--message",
            message,
            "--evidence-file",
            str(_context.evidence),
            "--acknowledge-external-execution",
        ]
    )

    result = {
        "mode": _context.mode,
        "cli_rc": rc,
        "status": execution.get("status"),
        "execution_performed": execution.get(
            "execution_performed"
        ),
        "network_execution_performed": execution.get(
            "network_execution_performed"
        ),
        "external_api_execution_performed": execution.get(
            "external_api_execution_performed"
        ),
        "execution_id": execution.get(
            "execution_id"
        ),
        "results": execution.get("results"),
        "blockers": execution.get("blockers"),
    }

    return json.dumps(
        result,
        sort_keys=True,
        separators=(",", ":"),
    )


def planner(
    state: MessagesState,
):
    del state

    return {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "governed_weather",
                        "args": {
                            "latitude": LATITUDE,
                            "longitude": LONGITUDE,
                        },
                        "id": "rbek-langgraph-weather-001",
                        "type": "tool_call",
                    }
                ],
            )
        ]
    }


def build_graph():
    builder = StateGraph(
        MessagesState
    )

    builder.add_node(
        "planner",
        planner,
    )

    builder.add_node(
        "tools",
        ToolNode(
            [governed_weather]
        ),
    )

    builder.add_edge(
        START,
        "planner",
    )

    builder.add_edge(
        "planner",
        "tools",
    )

    builder.add_edge(
        "tools",
        END,
    )

    return builder.compile()


def build_project(
    root: pathlib.Path,
) -> tuple[pathlib.Path, pathlib.Path]:
    project = root / "project"

    rc, init_payload = run_rbek(
        [
            "init",
            "--project-root",
            str(project),
        ]
    )

    if rc != 0:
        raise RuntimeError(
            "RBEK init failed: "
            + json.dumps(init_payload)
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
        "name": "langgraph-open-meteo",
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
        "name": "langgraph-open-meteo-policy",
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


def execute_mode(
    *,
    mode: str,
    project: pathlib.Path,
    plan: pathlib.Path,
    allow_gate: pathlib.Path,
) -> dict:
    evidence = project / ".rbek" / "evidence"

    if mode == "ALLOW":
        gate = allow_gate
    else:
        gate = (
            evidence
            / "execution-gate-deny.json"
        )

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
        / f"langgraph-{mode.lower()}-execution.json"
    )

    configure(
        ExecutionContext(
            project_root=project,
            plan=plan,
            gate=gate,
            evidence=execution_evidence,
            mode=mode,
        )
    )

    graph = build_graph()

    result = graph.invoke(
        {
            "messages": [],
        }
    )

    tool_message = result["messages"][-1]

    payload = json.loads(
        tool_message.content
    )

    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--live",
        action="store_true",
        help=(
            "Run the ALLOW path and make a real "
            "Open-Meteo request through RBEK."
        ),
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    with tempfile.TemporaryDirectory(
        prefix="rbek_langgraph_demo_"
    ) as temp:
        root = pathlib.Path(temp)

        plan, gate = build_project(
            root
        )

        project = root / "project"

        deny = execute_mode(
            mode="DENY",
            project=project,
            plan=plan,
            allow_gate=gate,
        )

        print("DENY")
        print(
            json.dumps(
                deny,
                indent=2,
                sort_keys=True,
            )
        )

        if deny.get("status") != "BLOCKED":
            raise RuntimeError(
                "DENY path was not blocked"
            )

        if deny.get(
            "network_execution_performed"
        ) is not False:
            raise RuntimeError(
                "DENY path performed network execution"
            )

        if not args.live:
            print()
            print(
                "Offline governance proof complete."
            )
            print(
                "DENY prevented the external action."
            )
            print(
                "Run with --live to execute the "
                "same tool through the authorized "
                "Open-Meteo path."
            )

            return 0

        allow = execute_mode(
            mode="ALLOW",
            project=project,
            plan=plan,
            allow_gate=gate,
        )

        print()
        print("ALLOW")
        print(
            json.dumps(
                allow,
                indent=2,
                sort_keys=True,
            )
        )

        if allow.get("status") != "PASS":
            raise RuntimeError(
                "ALLOW path failed"
            )

        if allow.get(
            "network_execution_performed"
        ) is not True:
            raise RuntimeError(
                "ALLOW path did not perform "
                "network execution"
            )

        if allow.get(
            "external_api_execution_performed"
        ) is not True:
            raise RuntimeError(
                "ALLOW path did not perform "
                "external API execution"
            )

        results = allow.get("results")

        if not isinstance(
            results,
            list,
        ) or len(results) != 1:
            raise RuntimeError(
                "Unexpected ALLOW result count"
            )

        output = results[0].get("output")

        if not isinstance(output, dict):
            raise RuntimeError(
                "Weather output missing"
            )

        if not isinstance(
            output.get("current"),
            dict,
        ):
            raise RuntimeError(
                "Current weather missing"
            )

        print()
        print(
            "Real governed Open-Meteo execution "
            "completed through RBEK."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
