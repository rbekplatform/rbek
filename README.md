# RBEK

**Governed execution for AI agents, workflows and software.**

RBEK provides a governed execution boundary between AI agents or automated
workflows and the external actions they want to perform.

The Developer experience is CLI-first.

## Install

```bash
curl -fsSL https://releases.rbekplatform.com/cli/stable/install.sh | bash
```

Then verify:

```bash
rbek-cli --version
```

Current public stable:

```text
RBEK 0.2.0
```

## What RBEK does

A typical flow is:

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

RBEK does not replace your agent framework or model provider.

It governs whether real external execution is allowed to happen and records
evidence around that decision.

## Developer

The Developer tier is the public entry point for local development,
evaluation and integration.

It does not require a paid commercial entitlement.

Team and Enterprise commercial access are handled separately.

## Repository role

This repository is the public Developer entry point for RBEK.

It contains documentation, examples and installation guidance.

The RBEK runtime is distributed through the official release host:

`https://releases.rbekplatform.com`

The complete runtime source is not published in this repository.

## Website

`https://rbekplatform.com`

## Security

See [SECURITY.md](SECURITY.md).

## Quickstart

See [QUICKSTART.md](QUICKSTART.md).
