# Real Governed Agent Demo

This example gives you two ways to see RBEK govern agent execution.

## Fastest proof — no API key

If RBEK is not installed yet:

```bash
curl -fsSL https://releases.rbekplatform.com/cli/stable/install.sh | bash
```

Then run:

```bash
./demo.sh
```

The default mode is offline and zero-key. It uses the real RBEK policy and
evidence path to prove:

```text
unauthorized action → DENY → not executed
authorized action   → ALLOW → governed dry-run → AUTHORIZED
```

At the end, `evidence/summary.json` shows exactly what RBEK decided and what did
or did not execute.

No OpenAI key is required. No external network action is performed by the demo.

## Browser-only — GitHub Codespaces

Open the repository in Codespaces:

https://codespaces.new/rbekplatform/rbek?quickstart=1

The environment installs RBEK and prepares the demo automatically.

Run:

```bash
cd examples/real-governed-agent
./demo.sh
```

## Live AI + Internet proof

To execute the real agent and external action:

```bash
export OPENAI_API_KEY="your-key"
./demo.sh --live
```

Live mode performs:

```text
OpenAI agent
   ↓
requests weather.current
   ↓
RBEK policy admission
   ↓
controlled external execution
   ↓
Open-Meteo
   ↓
receipt + certification
```

The agent does not call the weather API directly. The tool binding delegates the
action to RBEK, which owns the governed external execution path.

The demo uses `gpt-5-mini` by default. You can override the model:

```bash
export RBEK_DEMO_MODEL="gpt-5-mini"
```

## What this proves

Docker controls where software runs.

RBEK controls whether an action may run, how it is governed, and what evidence
proves the result.

## Security

This public example contains:

- no RBEK core runtime source;
- no private signing material;
- no commercial entitlement issuer;
- no customer data;
- no embedded API credentials.

The OpenAI credential remains in the caller's environment.
