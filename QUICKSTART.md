# RBEK Developer Quickstart

This is the shortest path from a clean machine to a running local RBEK project.

## 1. Install

```bash
curl -fsSL https://releases.rbekplatform.com/cli/stable/install.sh | bash
```

## 2. Verify

```bash
rbek-cli --version
```

Expected current stable:

```text
RBEK 0.2.0
```

## 3. Check local readiness

```bash
rbek-cli doctor
```

For a strict readiness check:

```bash
rbek-cli doctor --strict
```

## 4. Create a minimal project

```bash
rbek-cli init ./rbek-demo
```

## 5. Run it through RBEK

```bash
rbek-cli run ./rbek-demo
```

That is the first complete Developer flow:

```text
install
  ↓
doctor
  ↓
init
  ↓
run
```

## What happens conceptually?

RBEK is designed to sit between application logic and real execution:

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

The first local project demonstrates the CLI workflow without requiring you to
change agent frameworks or model providers.

## Next step

After the local flow works, move one real external action behind RBEK and make
its execution explicit, governed and observable.

Developer is the public entry point. Team and Enterprise add separate
commercial organization and deployment entitlement controls.
