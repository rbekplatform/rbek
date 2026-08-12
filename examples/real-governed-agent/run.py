from __future__ import annotations

import json
import os
import pathlib
import sys

try:
    from agents import Runner
except Exception as exc:
    raise SystemExit(
        "OpenAI Agents SDK is not available. "
        "Run ./setup.sh first."
    ) from exc

from openai_weather_binding import build_weather_agent


def main() -> int:
    if not os.environ.get("OPENAI_API_KEY"):
        print("DEMO_STATUS=BLOCKED")
        print("REASON=OPENAI_API_KEY_NOT_SET")
        print(
            "Set OPENAI_API_KEY in your shell before running this demo."
        )
        return 20

    result_path = pathlib.Path(
        os.environ.get(
            "RBEK_DEMO_RESULT",
            "./rbek-real-agent-result.json",
        )
    ).resolve()

    agent = build_weather_agent(
        model=os.environ.get(
            "RBEK_DEMO_MODEL",
            "gpt-5-mini",
        )
    )

    request = os.environ.get(
        "RBEK_DEMO_REQUEST",
        (
            "What is the current weather in Funchal, Madeira? "
            "Use the RBEK governed weather tool. "
            "Use latitude 32.6500 and longitude -16.9080. "
            "Tell me the temperature and whether the governed "
            "execution completed successfully."
        ),
    )

    print("============================================================")
    print(" RBEK — Real Governed Agent Demo")
    print("============================================================")
    print("Agent model:", os.environ.get("RBEK_DEMO_MODEL", "gpt-5-mini"))
    print("Action: current weather")
    print("External API: api.open-meteo.com")
    print("Governance boundary: RBEK")
    print()

    result = Runner.run_sync(
        agent,
        request,
        max_turns=6,
    )

    payload = {
        "product": "RBEK",
        "model": os.environ.get(
            "RBEK_DEMO_MODEL",
            "gpt-5-mini",
        ),
        "request": request,
        "final_output": str(result.final_output),
        "model_inference_performed": True,
        "real_external_action_requested": True,
        "execution_boundary": "RBEK",
    }

    result_path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(str(result.final_output))
    print()
    print("DEMO_STATUS=PASS")
    print("MODEL_INFERENCE_PERFORMED=TRUE")
    print("REAL_EXTERNAL_ACTION_REQUESTED=TRUE")
    print("EXECUTION_BOUNDARY=RBEK")
    print("RESULT_FILE=" + str(result_path))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
