Design random campaign events for Orbital Command. Return JSON only as an array of
exactly twelve objects. Each object must be:

{"id":"unique-kebab-case","title":"short","text":"1-2 sentences","min_turn":integer 1..12,"choices":[{"label":"short action","effects":{"energy":integer -10..10,"alloys":integer -8..8,"science":integer -8..8,"credits":integer -8..8,"morale":integer -12..12}},{"label":"different action","effects":{"energy":integer -10..10,"alloys":integer -8..8,"science":integer -8..8,"credits":integer -8..8,"morale":integer -12..12}}]}

Every event needs exactly two meaningful choices with trade-offs. Mix hazards,
diplomacy, discoveries, crew stories, and opportunities. No Markdown or extra keys.
