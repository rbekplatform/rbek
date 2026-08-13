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
      DENY / ALLOW
```

## Run the deterministic governance proof

```bash
./run.sh
```

The default path creates real CrewAI `Agent`, `Task`, `Crew`, and `BaseTool`
objects, then runs the tool against a deterministic RBEK DENY gate.

The external provider action is not performed.

## Run the real governed external action

```bash
./run.sh --allow
```

The ALLOW path uses the same CrewAI integration and executes the
`weather.current` action through RBEK and the promoted Open-Meteo adapter.

CrewAI does not call Open-Meteo directly. The tool invokes the public RBEK CLI
execution boundary.

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

This is a reference integration. It does not publish RBEK core source and does
not claim a public RBEK Python SDK compatibility contract.
