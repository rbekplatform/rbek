# RBEK

## Execution authority for AI agents.

**AI can propose. RBEK decides what can execute.**

[![Refund Governance Verified](https://github.com/rbekplatform/rbek/actions/workflows/refund-governance.yml/badge.svg)](https://github.com/rbekplatform/rbek/actions/workflows/refund-governance.yml)

An AI agent proposes three refunds:

```text
EUR 12,500 ........ DENY   executed: NO
EUR 2,000 ......... ALLOW  executed: YES
EUR 50,000 ........ DENY   executed: NO
```

The EUR 50,000 case includes a manipulative prompt attempting to override the policy. The prompt can propose an action; it does not grant execution authority.

### See RBEK decide in 10 seconds

```bash
curl -fsSL https://raw.githubusercontent.com/rbekplatform/rbek/main/examples/refund-governance/demo.sh | bash
```

**No API key. No prior RBEK installation. No payment processor.**

The demo installs and validates the public RBEK CLI when needed and applies a deterministic EUR 5,000 refund limit.

```text
AI / agent proposal
        |
        v
deterministic refund policy
        |
   +----+----+
   |         |
 DENY      ALLOW
   |         |
executed    RBEK governed
  NO        local execution
                |
                v
           executed YES
           + evidence
```

What the terminal proves:

```text
EUR 12,500 refund ............... DENIED
Denied refund executed .......... NO

EUR 2,000 refund ................ ALLOWED
Governed execution .............. YES
Execution evidence .............. VERIFIED

EUR 50,000 manipulative prompt .. DENIED
Prompt granted authority ........ NO
Denied refund executed .......... NO

Network action .................. NO
Database action ................. NO
External API action ............. NO
Payment processor ............... NO

RBEK_REFUND_GOVERNANCE_DEMO=PASS
```

The allowed case uses the bounded `customer-transform / local.transform` target.

Positive execution is accepted only when RBEK reports execution, receipt, certification and allowlist evidence.

The demo does **not** move money, contact Stripe, or contact a payment processor.

[Read the refund governance example →](examples/refund-governance/README.md)

### Want the real AI + Internet path?

The repository also includes a governed-agent example with real model inference and a real Open-Meteo external action:

```bash
cd examples/real-governed-agent
export OPENAI_API_KEY="your-key"
./demo.sh --live
```


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
RBEK 0.2.1
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

## Refund governance example

An AI agent may propose a refund. RBEK determines whether the proposal may
cross the execution boundary.

The runnable example covers three cases:

- **EUR 12,500** -> `DENY` -> no controlled execution.
- **EUR 2,000** -> `ALLOW` -> eligible for RBEK governed local execution.
- **Manipulative EUR 50,000 prompt** -> `DENY` -> no controlled execution.

Policy-only:

```bash
python3 examples/refund-governance/run.py
```

Explicit governed local execution for the allowed case:

```bash
python3 examples/refund-governance/run.py --execute
```

The example uses a bounded local `customer-transform / local.transform`
execution target. It does not contact Stripe, move money, or claim real
financial settlement.

**AI can propose. RBEK decides what can execute.**

See [`examples/refund-governance/`](examples/refund-governance/).
