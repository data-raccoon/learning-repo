Design the research tree for Orbital Command. Return JSON only as an array of exactly
six objects with this shape:

{"id":"fixed-id","name":"short","description":"one sentence","cost":integer 6..24,"prerequisite":null or "earlier id","effect":{"type":"production_bonus or morale_bonus or unlock","resource":"energy/alloys/science/credits/morale or module id","amount":integer 1..5}}

Use these IDs in order: efficient-routing, fusion-grid, diplomatic-protocols, deep-scan,
quantum-computing, closed-loop-life-support. Prerequisites may only reference an earlier
ID. Required module-unlock technologies must use effect type unlock and their module ID
as resource. No Markdown or extra keys.
