Design the constructible station modules for Orbital Command. Return JSON only as an
array of exactly eight objects. Every object must have:

{"id":"kebab-case","name":"short","description":"one sentence","cost":{"alloys":integer 2..12,"credits":integer 0..8},"production":{"energy":integer -3..8,"alloys":integer 0..4,"science":integer 0..5,"credits":integer 0..4,"morale":integer -4..5},"required_tech":null or "tech id"}

Use these exact IDs in this order: solar-array, refinery, research-lab, trade-dock,
habitat-ring, fusion-core, quantum-lab, observatory. The first five require null.
fusion-core requires fusion-grid; quantum-lab requires quantum-computing; observatory
requires deep-scan. Ensure early modules are affordable from 16 alloys and 12 credits.
No Markdown or extra keys.
