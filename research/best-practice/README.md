# <Project Name>

<One-sentence description of what this system does and for whom.>

## Status

> Example: Active development. Public interfaces may change before v1.0.

## Quick start

### Prerequisites

- `<runtime and version>`
- `<package manager>`
- Docker, if applicable

### Setup

```bash
git clone <repository>
cd <project-directory>
cp .env.example .env
make setup
make check
```

### Run locally

```bash
make run
```

The service will be available at `<local address>`.

## Common commands

| Command | Purpose |
|---|---|
| `make setup` | Install development dependencies |
| `make run` | Start the application |
| `make test` | Run deterministic tests |
| `make eval` | Run agent evaluations |
| `make check` | Run all required checks |
| `make clean` | Remove generated local artifacts |

## Repository structure

```text
src/              Application source
tests/            Deterministic automated tests
evals/            Agent behavior evaluations
docs/decisions/   Architecture decisions
docs/runbooks/    Operational procedures
```

## Configuration

Configuration is read from environment variables.

See `.env.example` for the complete list. Never commit `.env` or real
credentials.

## Development workflow

1. Create a focused branch.
2. Implement the smallest coherent change.
3. Add or update tests.
4. Run `make check`.
5. Run `make eval` if agent behavior changed.
6. Open a pull request using the repository template.

Coding agents must read [AGENTS.md](./AGENTS.md) before making changes.

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md).

Important architectural decisions are recorded in
[`docs/decisions/`](./docs/decisions/).

## Security

Report vulnerabilities according to [SECURITY.md](./SECURITY.md).
Do not open public issues for suspected vulnerabilities.

## License

<License and link to license file>
