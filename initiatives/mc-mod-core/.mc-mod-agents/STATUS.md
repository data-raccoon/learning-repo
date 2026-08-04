# Mana Core slice status

Last controller verification: 2026-08-04.

Status in this file is the source of truth for bounded pure-Java slices. A
passing current verifier proves the named slice contract; it does not claim a
Gradle/Fabric build, client smoke test, or dedicated-server smoke test.

| Slice | Current evidence | Status |
|---|---|---|
| Storage, coordinates, and ManaMath | `verify_storage_slice.py` — 91 checks | Current verifier passed; legacy v1 result archived |
| Gradient calculation | `verify_gradient_slice.py` — 17 tests and 16 contract checks | Current verifier passed; legacy v1 result archived |
| Pair and edge flow | `verify_flow_slice.py` — worker test and 15 contract checks | Current verifier passed; legacy v1 result archived |
| Spherical gathering | `verify_gather_slice.py` — worker test and 14 contract checks | Current verifier passed; legacy v1 result archived |
| API type interfaces | `verify_api_types_slice.py` — worker test and 11 contract checks | Current verifier passed; no accepted v2 execution evidence |
| API event records | `verify_api_events_slice.py` — 12 tests and 8 contract checks | Current verifier passed; no accepted v2 execution evidence |
| Mana configuration | `verify_config_slice.py` — 22 tests and 9 contract checks | Current verifier passed; no accepted v2 execution evidence |
| World-scoped ManaAPI facade | `verify_mana_api_facade.py` — 18 tests and 36 contract checks | Current controller implementation and verifier passed |

The Medium proposal in `.mc-mod-agents/plans/14-next-task.json` and the v2 run
under `.orchestration/runs/mc-mod-core-15-devstral-mana-api-clean` describe the
earlier process-global static facade. They remain historical evidence but are
superseded by `docs/STATE_OWNERSHIP.md` and the current instance-owned API.

All v1 task lifecycle files are preserved under `.mc-mod-agents/archive/v1/`.
The active `tasks/`, `packets/`, `acks/`, and `results/` directories contain no
v1 artifacts. The design contract is structurally valid, but the architecture
change intentionally invalidated the previous approval hash. A human must run
`manage.py approve` before the manager can materialize fresh downstream v2
asset and engineering tasks.

## Known integration gap

The current pure-Java API and config packages use `com.manacore.core.api` and
`com.manacore.core.config`, while the approved `mod-spec.json` artifact paths
name `com.manacore.api` and `com.manacore.config`. Reconcile that package/path
contract in an explicit v2 task before Fabric engineering materialization; the
passing slice verifiers do not resolve the approved-spec mismatch.
