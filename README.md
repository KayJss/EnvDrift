# EnvDrift

EnvDrift is a tiny CLI that catches **environment configuration drift** before it becomes a deployment problem.

It compares a reference file such as `.env.example` with a real `.env` file and reports:

- missing environment variables,
- required variables that are empty,
- unexpected variables,
- duplicate declarations,
- invalid `.env` syntax.

**Secret values are never printed in reports.** That makes EnvDrift suitable for local checks and CI pipelines.

## Why?

A project often works locally but fails in staging or production because one environment variable was forgotten, renamed, duplicated, or left empty. Manually comparing `.env` files is error-prone and can expose secrets in logs.

EnvDrift focuses on one job: verify that the expected configuration shape is present without leaking values.

## Features

- Zero runtime dependencies
- Human-readable output
- JSON output for CI/automation
- Safe reporting: keys only, never secret values
- Supports `export KEY=value`
- Handles quoted values
- Detects duplicate keys
- Detects malformed lines
- Optional allowance for target-only variables
- Useful exit codes

## Installation

Requires Python 3.10+.

```bash
git clone https://github.com/KayJss/EnvDrift.git
cd EnvDrift
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

Install:

```bash
pip install -e .
```

## Usage

By default EnvDrift compares `.env.example` and `.env`:

```bash
envdrift
```

Or choose files explicitly:

```bash
envdrift examples/.env.example examples/.env
```

Example result:

```text
Required variables with empty values:
  - REDIS_URL
Unexpected variables:
  - DEBUG
```

Machine-readable report:

```bash
envdrift examples/.env.example examples/.env --json
```

Allow environment-specific extra variables:

```bash
envdrift .env.example .env.production --allow-unexpected
```

You can also run it without installing the CLI entrypoint:

```bash
python -m envdrift examples/.env.example examples/.env
```

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Required configuration is valid |
| `1` | Missing, empty, duplicate, or malformed configuration detected |
| `2` | Input file could not be read |

Unexpected variables are warnings by default and do not fail the check.

## CI example

```yaml
- name: Check environment contract
  run: envdrift .env.example .env.ci
```

Because reports contain variable names only, CI logs do not reveal environment values.

## Project structure

```text
EnvDrift/
├── envdrift/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   └── core.py
├── examples/
│   ├── .env
│   └── .env.example
├── tests/
│   ├── test_cli.py
│   └── test_core.py
├── .gitignore
├── LICENSE
├── pyproject.toml
└── README.md
```

## Tests

No third-party test dependency is required:

```bash
python -m unittest discover -s tests -v
```

## Design choices

EnvDrift intentionally does **not** print or persist environment values. It parses files in memory, compares only their key structure and whether required values are empty, then returns a sanitized report.

This keeps the MVP small enough to understand quickly while still solving a real deployment problem.

## License

MIT
