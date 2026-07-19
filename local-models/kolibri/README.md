# Kolibri

Reserved local-model family. Kolibri is inventory-only until its artifact, license, runtime, endpoint contract, hardware limits, and evaluated capabilities are known.

## Admission checklist

1. Select the exact model artifact and record its upstream source, license, format, quantization, and immutable checksum.
2. Keep weights and credentials outside the repository; document only their expected external locations.
3. Choose and verify the runtime, loopback endpoint contract, health check, context limit, and GPU-slot policy.
4. Replace the `unselected` registry values with observed facts and move provider, harness, and profile from `deferred` to `candidate`.
5. Add deterministic inference and file-only canaries with independent verifiers.
6. Promote a profile to `eligible` only after retained evaluation evidence passes.

No runtime, model weight, secret, log, or PID file belongs in this directory.
