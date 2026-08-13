# RBEK

**Governed execution for AI agents, workflows and software.**

[![Deterministic Execution Verified](https://github.com/rbekplatform/rbek/actions/workflows/real-governed-agent.yml/badge.svg)](https://github.com/rbekplatform/rbek/actions/workflows/real-governed-agent.yml)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/rbekplatform/rbek?quickstart=1)

RBEK separates what an agent **wants to do** from what it is **authorized to execute**.

## See RBEK govern an action in 10 seconds

```bash
curl -fsSL https://raw.githubusercontent.com/rbekplatform/rbek/main/examples/real-governed-agent/demo.sh | bash
```

**No API key. No prior RBEK installation. No configuration.**

The demo installs and validates the public RBEK CLI when needed, then runs an
offline governed proof:

```text
Agent requests an action
        |
        +-- unauthorized -> DENY  -> executed: NO
        |
        +-- authorized   -> ALLOW -> governed dry-run -> AUTHORIZED
                                                |
                                                +-- evidence
```

What you see in the terminal:

```text
Unauthorized action ............ DENIED
Denied action executed ......... NO
Authorized action .............. ALLOWED
Governed dry-run ............... PASS
Gate authorization ............. AUTHORIZED
RBEK policy enforcement ........ REAL
RBEK evidence .................. REAL
```

The default proof performs **no external network action**. Policy enforcement
and evidence generation are real RBEK behavior.

The public GitHub Actions workflow executes the proof twice and verifies that
the deterministic evidence summary is identical across both runs.

### Prefer zero-install in the browser?

Use **Open in GitHub Codespaces** above, then run:

```bash
cd examples/real-governed-agent
./demo.sh
```

### Want the real AI + Internet path?

```bash
cd examples/real-governed-agent
export OPENAI_API_KEY="your-key"
./demo.sh --live
```

Live mode performs real model inference and a real Open-Meteo external action
through the RBEK governed execution boundary.

## Why RBEK?

AI agents can decide what they want to do. Production systems still need a
controlled boundary for what is actually allowed to execute.

RBEK puts that boundary between application logic and real external actions:

```text
agent / workflow
      ↓
execution request
      ↓
RBEK policy admission
   ↙             ↘
 DENY            ALLOW
                   ↓
               execute
                   ↓
               evidence
```

This keeps execution governance separate from the agent framework, model
provider or workflow engine.

## Install

```bash
curl -fsSL https://releases.rbekplatform.com/cli/stable/install.sh | bash
```

Verify:

```bash
rbek-cli --version
```

Current public stable:

```text
RBEK 0.2.0
```

## 5-minute quickstart

Create and run a minimal local RBEK project:

```bash
rbek-cli init ./rbek-demo
rbek-cli run ./rbek-demo
```

Or run the repository example:

```bash
bash examples/5-minute-quickstart/run.sh
```

The goal of the first five minutes is simple: install RBEK, create a governed
local project and execute it through the RBEK CLI.

See [QUICKSTART.md](QUICKSTART.md) for the complete first-run walkthrough.

## Run the live AI + Internet version

After the zero-key proof, you can run the real agent path:

```bash
cd examples/real-governed-agent
export OPENAI_API_KEY="your-key"
./demo.sh --live
```

In live mode:

```text
OpenAI agent
     ↓
weather.current
     ↓
RBEK policy admission
     ↓
controlled external execution
     ↓
Open-Meteo
     ↓
receipt + certification
```

The agent does not call Open-Meteo directly. The external action goes through
the RBEK governed execution boundary.

See
[examples/real-governed-agent/README.md](examples/real-governed-agent/README.md)
for details.

## Developer

Developer is the public CLI entry point for local development, evaluation and
integration.

It does not require a paid commercial entitlement.

Team and Enterprise commercial access are handled separately.

## Repository role

This repository contains Developer documentation, examples and installation
guidance.

The RBEK runtime is distributed through the official release host:

`https://releases.rbekplatform.com`

The complete runtime source is not published in this repository.

## Website

`https://rbekplatform.com`

## Security

See [SECURITY.md](SECURITY.md).
