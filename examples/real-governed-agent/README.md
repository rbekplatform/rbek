# Real Governed Agent Demo

This example shows an AI agent requesting a **real external action** through the
RBEK governed execution boundary.

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

The agent does not call the weather API directly. The tool binding delegates
the action to RBEK, which owns the governed external execution path.

## Requirements

- Python 3
- RBEK CLI 0.2.0
- network access
- an OpenAI API key supplied by you through `OPENAI_API_KEY`

No credential is stored in this repository.

## 1. Install RBEK

```bash
curl -fsSL https://releases.rbekplatform.com/cli/stable/install.sh | bash
rbek-cli --version
```

Expected:

```text
RBEK 0.2.0
```

## 2. Prepare the demo

```bash
./setup.sh
```

## 3. Supply your OpenAI credential

```bash
export OPENAI_API_KEY="your-key"
```

Do not commit credentials to Git.

## 4. Run

```bash
./run.sh
```

The demo uses `gpt-5-mini` by default. You can override the model:

```bash
export RBEK_DEMO_MODEL="gpt-5-mini"
```

## What this proves

The interesting part of the demo is the execution boundary:

```text
model decides to use a tool
          ↓
tool requests an action
          ↓
RBEK governs execution
          ↓
external API executes only through RBEK
```

RBEK remains independent of the agent framework and the external API.

## Security

This public example contains:

- no RBEK core runtime source;
- no private signing material;
- no commercial entitlement issuer;
- no customer data;
- no embedded API credentials;
- no RBEK Document product content.

The OpenAI credential remains in the caller's environment.
