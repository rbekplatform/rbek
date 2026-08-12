# RBEK Developer Quickstart

## 1. Install

```bash
curl -fsSL https://releases.rbekplatform.com/cli/stable/install.sh | bash
```

## 2. Verify

```bash
rbek-cli --version
```

Expected:

```text
RBEK 0.2.0
```

## 3. Understand the execution model

RBEK sits between application logic and real external execution:

```text
AI agent / workflow
        ↓
   execution request
        ↓
       RBEK
   policy decision
     ↙       ↘
   deny      allow
               ↓
           execution
               ↓
            evidence
```

## 4. Start with one real action

For evaluation, choose one agent or workflow action that calls an external
tool or API.

The goal is to make that action explicit, governed and observable through
RBEK rather than leaving execution embedded directly inside application logic.

## 5. Production and commercial use

Developer is the entry point.

When an organization needs Team or Enterprise commercial operation, RBEK adds
organization-level entitlement controls, and Enterprise can additionally bind
authorization to a deployment.
