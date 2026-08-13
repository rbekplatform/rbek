from __future__ import annotations

import json
import pathlib
import subprocess
from dataclasses import dataclass
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


RBEK_CLI = "rbek-cli"


class WeatherInput(BaseModel):
    latitude: float = Field(
        description="Latitude in decimal degrees"
    )

    longitude: float = Field(
        description="Longitude in decimal degrees"
    )


@dataclass(frozen=True)
class RBEKExecutionContext:
    project_root: pathlib.Path
    plan: pathlib.Path
    gate: pathlib.Path
    evidence_file: pathlib.Path
    mode: str


class RBEKGovernedWeatherTool(BaseTool):
    name: str = "rbek_governed_weather"

    description: str = (
        "Get current weather through the RBEK "
        "governed execution boundary."
    )

    args_schema: Type[BaseModel] = WeatherInput

    execution_context: RBEKExecutionContext

    model_config = {
        "arbitrary_types_allowed": True,
    }

    def _run(
        self,
        latitude: float,
        longitude: float,
    ) -> str:
        message = json.dumps(
            {
                "latitude": float(latitude),
                "longitude": float(longitude),
            },
            sort_keys=True,
            separators=(",", ":"),
        )

        completed = subprocess.run(
            [
                RBEK_CLI,
                "--output",
                "json",
                "execution",
                "external-run",
                "--project-root",
                str(self.execution_context.project_root),
                "--plan",
                str(self.execution_context.plan),
                "--gate",
                str(self.execution_context.gate),
                "--message",
                message,
                "--evidence-file",
                str(self.execution_context.evidence_file),
                "--acknowledge-external-execution",
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

        result = {
            "mode": self.execution_context.mode,
            "cli_rc": completed.returncode,
            "status": payload.get("status"),
            "execution_id": payload.get("execution_id"),
            "execution_performed": payload.get(
                "execution_performed"
            ),
            "network_execution_performed": payload.get(
                "network_execution_performed"
            ),
            "external_api_execution_performed": payload.get(
                "external_api_execution_performed"
            ),
            "results": payload.get("results"),
            "blockers": payload.get("blockers"),
        }

        return json.dumps(
            result,
            sort_keys=True,
            separators=(",", ":"),
        )
