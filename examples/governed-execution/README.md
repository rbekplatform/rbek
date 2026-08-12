# Governed Execution Example

This repository intentionally does not duplicate the private runtime source.

Use this example as a conceptual starting point for integrating one external
action behind RBEK.

```text
application / agent
       ↓
 governed request
       ↓
      RBEK
       ↓
 policy admission
   ↙         ↘
 deny        allow
               ↓
        external action
               ↓
            evidence
```

Install RBEK first:

```bash
curl -fsSL https://releases.rbekplatform.com/cli/stable/install.sh | bash
```

Then verify:

```bash
rbek-cli --version
```

Current stable:

```text
RBEK 0.2.0
```
