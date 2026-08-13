# CrewAI + RBEK governed tool

Keep CrewAI for agent orchestration. Put RBEK at the external execution boundary.

```text
CrewAI Agent / Task / Crew
          |
          v
       BaseTool
          |
          v
RBEKGovernedWeatherTool
          |
          v
rbek-cli execution external-run
          |
  TAMPERED_GATE / ALLOW
```

## Run the deterministic governance proof

```bash
./run.sh
```

The default path creates real CrewAI `Agent`, `Task`, `Crew`, and `BaseTool`
objects, then invokes the tool using a deliberately tampered RBEK execution
gate.

The gate was originally authorized for the execution plan. The proof changes
its `plan_digest`, breaking the authorization binding.

RBEK must reject that artifact before any external provider action is
performed.

Expected result:

```text
mode: TAMPERED_GATE
status: BLOCKED
execution_performed: false
network_execution_performed: false
external_api_execution_performed: false
```

This proves execution-gate integrity enforcement.

It is intentionally **not described as a policy DENY**.

The policy used to create the execution plan is `ALLOW`.

A policy denial and an invalid or tampered authorization artifact are
different governance cases and should be demonstrated separately.

## Run the real governed external action

```bash
./run.sh --allow
```

The `ALLOW` path uses the same CrewAI integration, same governed tool and same
input, but supplies the valid authorized gate.

RBEK then executes the `weather.current` action through the promoted
Open-Meteo adapter.

CrewAI does not call Open-Meteo directly.

The tool invokes the public RBEK CLI execution boundary.

## Install RBEK

```bash
curl -fsSL https://releases.rbekplatform.com/cli/stable/install.sh | bash
```

Expected runtime:

```text
RBEK 0.2.0
```

## Architecture

Your framework decides what to do.

RBEK decides what may execute.

More precisely:

> The agent proposes an action. RBEK controls whether that action may cross
> the external execution boundary.

This is a reference integration.

It does not publish RBEK core source and does not claim a public RBEK Python
SDK compatibility contract.

## Governance cases

| Case | Expected result | External action |
|---|---|---|
| `TAMPERED_GATE` | `BLOCKED` | No |
| `ALLOW` | `PASS` | Yes |

A true `POLICY_DENY` proof should be implemented separately against explicit
public CLI policy-rejection behavior.

It must not be represented by altering the digest of an already authorized
gate.
