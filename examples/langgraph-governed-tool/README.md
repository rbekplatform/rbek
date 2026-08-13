# LangGraph + RBEK governed tool

Use LangGraph for orchestration. Use RBEK for the execution boundary.

```text
LangGraph
   |
   v
ToolNode
   |
   v
RBEK governed tool
   |
   v
RBEK policy / gate
   |          |
 DENY       ALLOW
   |          |
 no action    external action
              |
              v
          evidence
```

## Run the deterministic governance proof

```bash
./demo.sh
```

The default proof uses a real LangGraph `StateGraph` and real `ToolNode`.
It proves the DENY path without performing the external Open-Meteo action.

## Run the real external action

```bash
./demo.sh --live
```

The live path uses the same LangGraph graph, same tool and same input, then
executes the authorized `weather.current` action through RBEK and the promoted
Open-Meteo adapter.

LangGraph does not call Open-Meteo directly. The tool invokes the public RBEK
CLI execution boundary.

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

This example is a reference integration. It does not publish RBEK core source
and does not claim a public RBEK Python SDK compatibility contract.
