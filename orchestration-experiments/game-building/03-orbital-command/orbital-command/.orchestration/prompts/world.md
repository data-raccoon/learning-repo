Design the campaign frame for Orbital Command. Return JSON only with this exact shape:

{
  "station_name": "string",
  "setting": "2-3 concise sentences",
  "starting_resources": {"energy": 20, "alloys": 16, "science": 0, "credits": 12, "morale": 70},
  "crew_total": 12,
  "roles": [
    {"id": "engineering", "name": "string", "description": "string"},
    {"id": "science", "name": "string", "description": "string"},
    {"id": "operations", "name": "string", "description": "string"}
  ],
  "mission_goals": [
    {"id": "energy_goal", "label": "string", "resource": "energy", "target": 60},
    {"id": "science_goal", "label": "string", "resource": "science", "target": 45},
    {"id": "morale_goal", "label": "string", "resource": "morale", "target": 85}
  ]
}

Keep all identifiers and numeric values exactly as shown. Make the prose distinctive,
hopeful, and suitable for a compact strategy game. No Markdown or extra keys.
