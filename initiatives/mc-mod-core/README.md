# MC-Mod staged workflow

Current bounded-slice status is recorded in `.mc-mod-agents/STATUS.md` and mana
world-lifecycle ownership is defined in `docs/STATE_OWNERSHIP.md`.

This directory prepares bounded proposal and implementation packets for a Fabric 26.2 mod. It deliberately does not run a worker graph. The root advances one phase at a time and uses `model-execution-harness/core/` for packing, routing, execution, acknowledgement, and release gating.

## Pinned toolchain

- Minecraft 26.2
- Fabric Loader 0.19.3
- Fabric API 0.154.2+26.2
- Fabric Loom 1.17-SNAPSHOT (`net.fabricmc.fabric-loom`)
- Gradle 9.5.1 through a checked-in wrapper
- Java 25

Changing a pin requires explicit human approval and a schema/template/test update. A generated official Fabric project should supply the Gradle wrapper, including the binary `gradle-wrapper.jar`; a model must not synthesize or download that binary.

## Lifecycle

All Python commands use the repository-required interpreter.

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" initiatives\mc-mod\manage.py init --target initiatives/my-mod --id my-mod --profile gemini-auto-free
```

1. Complete `.mc-mod-agents/intent.md`.
2. Pack and route `.mc-mod-agents/tasks/01-mod-architect.task.json` with `model-execution-harness/core/harness.py`.
3. Have the externally scoped writer acknowledge the exact packet, then record a
   packet-bound baseline outside the target before implementation:

   ```powershell
   & "$env:USERPROFILE\.venvs\all\Scripts\python.exe" model-execution-harness\core\harness.py accept packet.json ack.json --worker worker-id
   & "$env:USERPROFILE\.venvs\all\Scripts\python.exe" model-execution-harness\core\harness.py snapshot task.json packet.json ack.json baseline.json --repo .
   ```

   After implementation, require exact changed-file hashes, independent
   root-authored verifiers, and `gate --baseline`. Worker-authored tests are
   supporting evidence only.
4. Review the design and record human approval:

   ```powershell
   & "$env:USERPROFILE\.venvs\all\Scripts\python.exe" initiatives\mc-mod\manage.py approve --target initiatives/my-mod
   ```

5. Materialize and complete the Asset task:

   ```powershell
   & "$env:USERPROFILE\.venvs\all\Scripts\python.exe" initiatives\mc-mod\manage.py materialize-build --target initiatives/my-mod --profile devstral-small
   ```

6. Record the passing asset gate, then materialize and complete Engineering:

   ```powershell
   & "$env:USERPROFILE\.venvs\all\Scripts\python.exe" initiatives\mc-mod\manage.py record-asset-gate --target initiatives/my-mod --gate path\to\asset-gate-result.json
   & "$env:USERPROFILE\.venvs\all\Scripts\python.exe" initiatives\mc-mod\manage.py materialize-engineer --target initiatives/my-mod --profile devstral-small
   ```

7. Preserve the passing harness gate output before QA:

   ```powershell
   & "$env:USERPROFILE\.venvs\all\Scripts\python.exe" initiatives\mc-mod\manage.py record-build-gate --target initiatives/my-mod --gate path\to\gate-result.json
   & "$env:USERPROFILE\.venvs\all\Scripts\python.exe" initiatives\mc-mod\manage.py materialize-qa --target initiatives/my-mod --profile gemini-auto-free
   ```

QA reads the completed trusted gate evidence. It never repairs findings or claims runtime smoke coverage that was not supplied.

## Safety boundary

Tasks contain exact target-local context slices and exact-file `write_roots`.
Verifier argv is root-authored and fixed; `mod-spec.json` selects verifier IDs
only. For mutating workers, store the harness baseline outside the target and
pass it to `gate --baseline`; this detects unreported writes and deletions in
addition to validating reported hashes. Runner-enforced write roots remain
recommended as the first enforcement layer.

Gradle tests execute project code. Run them in a suitable external sandbox when worker output is not trusted.
