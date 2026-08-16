from __future__ import annotations

import sys
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from rbek import CLIExecutionBinding, GovernedAction, Policy


class WeatherState(TypedDict):
    latitude: float
    longitude: float
    live: bool
    status: str
    executed: bool


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


def governed_weather(state: WeatherState) -> dict[str, object]:
    inputs = {
        "latitude": state["latitude"],
        "longitude": state["longitude"],
    }

    result = (
        action.execute(**inputs)
        if state["live"]
        else action.evaluate(**inputs)
    )

    return {
        "status": result.status,
        "executed": result.executed,
    }


builder = StateGraph(WeatherState)
builder.add_node("weather", governed_weather)
builder.add_edge(START, "weather")
builder.add_edge("weather", END)
graph = builder.compile()


def main() -> None:
    denied = graph.invoke(
        {
            "latitude": 120.0,
            "longitude": -16.92,
            "live": False,
            "status": "",
            "executed": False,
        }
    )

    print("local_policy_status:", denied["status"])
    print("local_policy_executed:", denied["executed"])

    if "--live" not in sys.argv:
        return

    allowed = graph.invoke(
        {
            "latitude": 32.66,
            "longitude": -16.92,
            "live": True,
            "status": "",
            "executed": False,
        }
    )

    print("governed_execution_status:", allowed["status"])
    print("governed_execution_performed:", allowed["executed"])


if __name__ == "__main__":
    main()
