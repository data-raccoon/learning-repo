# Project Start agent pack

Project Start is a model- and IDE-neutral workflow pack that turns human-owned
intent into a minimal, reviewable initial project architecture. It supplies
three agent definitions, typed contracts, an admitted archetype catalog, one
versioned stack pack, deterministic rendering, independent review, and
hash-bound human approval.

The pack declares capabilities rather than model names. The root controller
chooses an admitted execution profile explicitly. The pack itself does not
access credentials or invoke models.

## What it creates

After approval, a target contains:

```text
project-intent.json              human authority
discovery.json                   normalized requirements and archetype candidates
project-design.json              single typed architecture source of truth
architecture-review.json         independent review
README.md                        deterministic rendering
AGENTS.md                        project-local implementation boundaries
bootstrap-plan.json              trusted-generator handoff
docs/
  PRODUCT.md
  ARCHITECTURE.md
  ACCEPTANCE.md
  decisions/ADR-0001-initial-architecture.md
.projectstart/                   lifecycle state, frozen context, tasks, evidence
```

The generic stack pack is documentation-only. It does not invent a source scaffold. Add a versioned, root-reviewed stack pack and trusted generator before generating framework, package-manager, build-wrapper, CI, or deployment files.

## Lifecycle

Use the repository-required Python interpreter from the repository root.

### 1. Initialize

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" agent-packs\project-start\manage.py init `
  --target initiatives\my-new-project `
  --id my-new-project `
  --stack-pack generic-software-v1
```

Complete `initiatives/my-new-project/project-intent.json`. Replace every placeholder and resolve every requirement with status `unknown`.

### 2. Discovery

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" agent-packs\project-start\manage.py prepare-discovery --target initiatives\my-new-project --profile PROFILE_ID
```

Execute `.projectstart/tasks/01-discovery.task.json` through
`model-execution-harness/core/harness.py`. The bounded worker writes
`discovery.json`. If it contains conflicts or blocking questions, update the
human intent and repeat discovery. When it is clean:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" agent-packs\project-start\manage.py accept-discovery --target initiatives\my-new-project
```

### 3. Architecture

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" agent-packs\project-start\manage.py materialize-architecture --target initiatives\my-new-project --profile PROFILE_ID
```

Run the `02-architecture.task.json` packet with a scoped writer that may create only `project-design.json`. Then validate and render:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" agent-packs\project-start\manage.py render --target initiatives\my-new-project
```

The renderer refuses to overwrite existing project documents. Resolve collisions deliberately rather than using a force flag.

### 4. Fresh review and approval

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" agent-packs\project-start\manage.py materialize-review --target initiatives\my-new-project --profile PROFILE_ID
```

Run the review packet with fresh context. Record only a review bound to the current design hash and carrying `PASS` with no blocking or major findings:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" agent-packs\project-start\manage.py record-review `
  --target initiatives\my-new-project `
  --review initiatives\my-new-project\architecture-review.json

& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" agent-packs\project-start\manage.py approve --target initiatives\my-new-project
```

Approval hashes the human intent, discovery, typed design, review, rendered documents, catalog, and selected stack pack. Changing any bound artifact makes the approval stale.

## Adding a stack pack

Add `stack-packs/<id>.json` with:

- Exact component versions.
- Approved dependency families.
- Prohibited patterns and obsolete APIs.
- Required individual artifacts.
- One trusted generator ID and mode.
- One root-owned verification profile.

Validate new catalogs, intents, and packs against the schemas in `templates/`. Runtime validation remains dependency-free and adds cross-field checks that JSON Schema alone cannot express.

Do not place executable argv, secrets, credentials, or downloaded template content in a model-authored design. Generator IDs must be implemented and allowlisted by trusted controller code before use.

## Model settings

Recommended starting envelope for Medium 3.5-class models:

- Custom structured output matching the phase schema.
- High reasoning effort for architecture, normal for discovery and review.
- Curated packets below roughly 50,000 characters when possible.
- Low randomness.
- No chat transcript or broad repository dump.
- Read-only architecture tools; one scoped materialization step afterward.
- Fresh review context without the architect trajectory.

## Verification

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest discover -s agent-packs\project-start\tests -v
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest discover -s model-execution-harness\core\tests -v
```

The core harness compares the complete target diff with its baseline and rejects
unreported writes. Its baseline detects changes but does not contain rollback
data; use the graph runtime only when transactional restoration is required.
