from __future__ import annotations

from typing import Any

from rbek_weather_bridge import (
    governed_current_weather_json,
)


TOOL_NAME = (
    "governed_current_weather"
)


def _weather_tool(
    latitude: float,
    longitude: float,
) -> str:
    """
    Get current weather through RBEK governed execution.

    Args:
        latitude: Latitude in decimal degrees.
        longitude: Longitude in decimal degrees.

    Returns:
        RBEK governed JSON weather result.
    """

    return governed_current_weather_json(
        latitude=latitude,
        longitude=longitude,
    )


def build_weather_agent(
    *,
    model: str = "gpt-5-mini",
) -> Any:
    from agents import (
        Agent,
        function_tool,
    )

    tool = function_tool(
        name_override=TOOL_NAME,
        description_override=(
            "Get current weather through "
            "the RBEK governed execution layer. "
            "The external Internet API call must "
            "be executed by RBEK."
        ),
        use_docstring_info=True,
        strict_mode=True,
    )(
        _weather_tool
    )

    return Agent(
        name=(
            "RBEK Governed Weather Agent"
        ),

        instructions=(
            "You are a weather assistant operating "
            "under RBEK governance. "
            "When asked for current weather, use "
            "governed_current_weather. "
            "Never claim external weather data unless "
            "the RBEK governed tool returns it. "
            "Report the temperature and mention whether "
            "the receipt and certification are valid."
        ),

        model=model,

        tools=[
            tool,
        ],
    )
