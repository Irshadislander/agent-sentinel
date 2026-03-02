# Plugin API

## Registering a Capability

Capabilities can be registered in two ways:

1. Decorator (`register_capability`)
2. Direct registry call (`registry.register`)

Example with decorator:

```python
from agent_sentinel.capabilities import register_capability
from agent_sentinel.capabilities.base import Capability, Result
from agent_sentinel.cli_exit_codes import ExitCode


@register_capability(
    id="demo.echo",
    name="echo",
    namespace="demo.plugins",
    version="1.0.0",
    description="Echo payload fields",
    tags=["demo", "example"],
    schema={
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
    },
)
class EchoCapability(Capability):
    name = "echo"

    def execute(self, payload: dict[str, object]) -> Result:
        return Result(ok=True, code=ExitCode.OK, data={"echo": payload.get("text")})
```

## Metadata Requirements

Each capability must provide:
- `id` (unique, non-empty, no whitespace)
- `name`
- `namespace`
- `version` (semver)
- `description`
- `tags` (list of non-empty strings)

Duplicate IDs are rejected at registration time.

## Payload Schema Expectations

- `schema` must be JSONSchema-like (`dict`) and must not be empty.
- Pydantic-style models are accepted if they provide `model_json_schema()` or `schema()`.
- Runtime payload validation uses the registered schema before execution.

## Packaging Plugins via Entry Points

Plugins are discovered via the `agent_sentinel.capabilities` entry-point group.

Example in plugin package `pyproject.toml`:

```toml
[project.entry-points."agent_sentinel.capabilities"]
echo = "my_plugin_pkg.echo:EchoCapability"
```

## Runtime Loading Modes

- default: load all discovered plugins (warn and continue on failures)
- `--no-plugins`: core-only mode
- `--plugins allowlist.txt`: load only names in the file
- `--strict-plugins`: fail fast on plugin load errors
