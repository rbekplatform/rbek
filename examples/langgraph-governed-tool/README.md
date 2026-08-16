# LangGraph + RBEK

Keep LangGraph for orchestration. Put RBEK at the execution boundary.

## 60-second SDK quickstart

Install the framework and the published RBEK Python SDK:

```bash
python -m pip install -r requirements.txt
```

The example is built against:

```text
rbek==0.3.0a3
```

Run the default local business-policy proof:

```bash
python quickstart.py
```

The rule is intentionally readable:

```python
Policy.allow_if(
    "latitude >= -90 and latitude <= 90 "
    "and longitude >= -180 and longitude <= 180"
)
```

The default input uses latitude `120.0`, so `Policy.evaluate` returns `DENIED`
without performing provider execution.

Expected shape:

```text
local_policy_status: DENIED
local_policy_executed: False
```

`Policy.evaluate` is a local business-policy pre-check. It does not perform
provider execution and it should not be described as equivalent to the
canonical RBEK runtime gate.

## Real governed provider execution

Real governed provider execution requires the RBEK CLI:

```bash
curl -fsSL https://releases.rbekplatform.com/cli/stable/install.sh | bash
```

Then run:

```bash
python quickstart.py --live
```

The live path uses:

```python
CLIExecutionBinding(
    provider="open-meteo",
    capability="weather.current",
)
```

and crosses the RBEK execution boundary through:

```python
GovernedAction.execute(...)
```

LangGraph does not call Open-Meteo directly.

Your framework decides what to do. RBEK decides what may execute.

## Architecture

```text
LangGraph
   |
   v
GovernedAction
   |
   +--> Policy.evaluate      local business-policy check
   |
   +--> CLIExecutionBinding
            |
            v
        RBEK CLI
            |
            v
     governed execution
```

## Advanced governance proof

The original lower-level CLI reference remains available unchanged:

```bash
./demo.sh
```

For the real external path:

```bash
./demo.sh --live
```

That advanced example exercises lower-level RBEK project, plan, gate and
evidence behavior and remains useful for studying the governance boundary.

The Python SDK quickstart is now the recommended first developer entry point.
