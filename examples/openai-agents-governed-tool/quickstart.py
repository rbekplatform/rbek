from __future__ import annotations

import argparse
import os

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


def _governed_weather(
    latitude: float,
    longitude: float,
    *,
    live: bool,
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


def _run_local_policy() -> None:
    result = action.evaluate(
        latitude=120.0,
        longitude=-16.92,
    )

    print("local_policy_status:", result.status)
    print("local_policy_executed:", result.executed)


def _run_agent(*, live: bool) -> None:
    from agents import Agent, Runner, function_tool

    @function_tool
    def governed_weather(
        latitude: float,
        longitude: float,
    ) -> str:
        """Evaluate or execute weather through the RBEK boundary."""
        return _governed_weather(
            latitude,
            longitude,
            live=live,
        )

    agent = Agent(
        name="RBEK governed weather agent",
        instructions=(
            "Use the governed_weather tool exactly once. "
            "Do not invent weather data. "
            "Report the tool result clearly."
        ),
        tools=[governed_weather],
    )

    prompt = (
        "Use governed_weather exactly once with "
        "latitude 32.66 and longitude -16.92."
        if live
        else
        "Use governed_weather exactly once with "
        "latitude 120.0 and longitude -16.92."
    )

    result = Runner.run_sync(
        agent,
        prompt,
    )

    print("agent_output:", result.final_output)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "OpenAI Agents SDK + RBEK governed execution example."
        )
    )

    parser.add_argument(
        "--agent",
        action="store_true",
        help="Run a real OpenAI Agents SDK agent.",
    )

    parser.add_argument(
        "--live",
        action="store_true",
        help=(
            "Allow the agent tool to cross the RBEK governed "
            "execution boundary."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    if args.live and not args.agent:
        raise SystemExit(
            "--live requires --agent; "
            "live execution cannot be enabled by the default path."
        )

    if not args.agent:
        _run_local_policy()
        return

    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit(
            "OPENAI_API_KEY is required only for --agent mode."
        )

    _run_agent(
        live=args.live,
    )


if __name__ == "__main__":
    main()
