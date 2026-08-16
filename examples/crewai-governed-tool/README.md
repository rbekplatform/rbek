# CrewAI + RBEK

Keep CrewAI for agent orchestration. Put RBEK at the external execution
boundary.

## 60-second SDK quickstart

Install CrewAI and the published RBEK Python SDK:

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

The business rule is visible before the governance plumbing:

```python
Policy.allow_if(
    "latitude >= -90 and latitude <= 90 "
    "and longitude >= -180 and longitude <= 180"
)
```

The quickstart wraps the governed action in a normal CrewAI `BaseTool`.

The default input uses latitude `120.0`, so `Policy.evaluate` returns `DENIED`
without performing provider execution.

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

and the RBEK action crosses the execution boundary through:

```python
GovernedAction.execute(...)
```

CrewAI does not call Open-Meteo directly.

`tool.run(...)` in `quickstart.py` is CrewAI's `BaseTool.run` method. It is
not an RBEK SDK `.run()` method. The RBEK SDK action uses only
`evaluate()` and `execute()`.

Your framework decides what to do. RBEK decides what may execute.

## Architecture

```text
CrewAI BaseTool
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

The original lower-level CrewAI governance proof remains available unchanged:

```bash
./run.sh
```

It creates real CrewAI `Agent`, `Task`, `Crew`, and `BaseTool` objects and
demonstrates execution-gate integrity with the `TAMPERED_GATE` case.

Run its authorized external path with:

```bash
./run.sh --allow
```

That advanced proof intentionally works at a lower level than the Python SDK
quickstart and remains useful for studying gate integrity, execution evidence
and the CLI boundary.

The Python SDK quickstart is now the recommended first developer entry point.
