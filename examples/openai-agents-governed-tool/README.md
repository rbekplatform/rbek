# OpenAI Agents SDK + RBEK

Keep the OpenAI Agents SDK for agent orchestration and tool selection.
Put RBEK at the external execution boundary.

Your framework decides what to do. RBEK decides what may execute.

## 60-second SDK quickstart

Install the OpenAI Agents SDK and published RBEK Python SDK:

~~~bash
python -m pip install -r requirements.txt
~~~

This example is built against:

~~~text
openai-agents==0.21.1
rbek==0.3.0a3
~~~

## 1. Zero-key local policy proof

The default path does not run an OpenAI agent and does not require an
OpenAI API key:

~~~bash
python quickstart.py
~~~

It evaluates an intentionally invalid latitude against:

~~~python
Policy.allow_if(
    "latitude >= -90 and latitude <= 90 "
    "and longitude >= -180 and longitude <= 180"
)
~~~

The default latitude is 120.0, so the expected shape is:

~~~text
local_policy_status: DENIED
local_policy_executed: False
~~~

Policy.evaluate is a local business-policy pre-check.

It does not perform provider execution and must not be described as
equivalent to the canonical RBEK runtime gate.

## 2. Real OpenAI agent, no provider effect

Set an OpenAI API key and run:

~~~bash
export OPENAI_API_KEY=...
python quickstart.py --agent
~~~

This runs a real OpenAI Agents SDK Agent through Runner.run_sync.

The agent can select the governed_weather function tool, but this mode
uses:

~~~python
Policy.evaluate(...)
~~~

No external weather-provider action is performed by this mode.

## 3. Real agent with governed provider execution

Real governed provider execution additionally requires the RBEK CLI.

Then run:

~~~bash
python quickstart.py --agent --live
~~~

The live path crosses the RBEK execution boundary through:

~~~python
GovernedAction.execute(...)
~~~

using:

~~~python
CLIExecutionBinding(
    provider="open-meteo",
    capability="weather.current",
)
~~~

The OpenAI agent does not call Open-Meteo directly.

## Execution authority

The model-visible function tool accepts only:

~~~text
latitude
longitude
~~~

The model cannot select live mode.

Whether the tool uses Policy.evaluate or GovernedAction.execute is
selected by the process-level --live flag.

live is deliberately not exposed as a function-tool argument.

~~~text
OpenAI Agent
     |
     | chooses tool + business inputs
     v
governed_weather(latitude, longitude)
     |
     v
RBEK governed helper
     |
     +--> --agent
     |       Policy.evaluate
     |
     +--> --agent --live
             GovernedAction.execute
                    |
                    v
             CLIExecutionBinding
                    |
                    v
                 RBEK CLI
                    |
                    v
          governed provider execution
~~~

## Governance semantics

A local business-policy rejection is a normal DENIED result.

It is not a TAMPERED_GATE.

An invalid or tampered execution authorization is a separate integrity
failure and must not be represented as a policy denial.

An OpenAI API failure, missing API key, or an agent choosing not to use
the tool is not an RBEK denial.
