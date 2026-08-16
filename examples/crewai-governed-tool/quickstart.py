from __future__ import annotations

import sys

from crewai.tools import BaseTool
from rbek import CLIExecutionBinding, GovernedAction, Policy


policy = Policy.allow_if(
    "latitude >= -90 and latitude <= 90 "
    "and longitude >= -180 and longitude <= 180"
)

action = GovernedAction(
    "weather",
    policy=policy,
    binding=CLIExecutionBinding(
        provider="open-meteo",
        capability="weather.current",
    ),
)


class RBEKWeatherTool(BaseTool):
    name: str = "governed_weather"
    description: str = (
        "Evaluate or execute a weather action through the RBEK boundary."
    )

    def _run(
        self,
        latitude: float,
        longitude: float,
        live: bool = False,
    ) -> str:
        inputs = {
            "latitude": latitude,
            "longitude": longitude,
        }

        result = (
            action.execute(**inputs)
            if live
            else action.evaluate(**inputs)
        )

        return (
            f"status={result.status} "
            f"executed={result.executed}"
        )


def main() -> None:
    tool = RBEKWeatherTool()

    # BaseTool.run belongs to CrewAI. The RBEK action uses evaluate/execute.
    denied = tool.run(
        latitude=120.0,
        longitude=-16.92,
        live=False,
    )
    print("local_policy:", denied)

    if "--live" not in sys.argv:
        return

    allowed = tool.run(
        latitude=32.66,
        longitude=-16.92,
        live=True,
    )
    print("governed_execution:", allowed)


if __name__ == "__main__":
    main()
