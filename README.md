# RBEK

**Governed execution for AI agents, workflows and software.**

RBEK provides a governed execution boundary between AI agents or automated
workflows and the external actions they want to perform.

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

## See RBEK govern a real agent action

The repository also includes a real governed-agent demo:

```text
AI agent
   ↓
requests weather.current
   ↓
RBEK policy admission
   ↓
controlled external execution
   ↓
Open-Meteo
   ↓
execution evidence
```

Run it from:

```bash
cd examples/real-governed-agent
./setup.sh
export OPENAI_API_KEY="your-key"
./run.sh
```

This example performs a real model inference and a real external API action
through the RBEK governed execution boundary.

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
