"""Validate Glimweave data and assemble deterministic runtime-owned files."""

from __future__ import annotations

import json
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parents[1]
DATA_JSON = EXPERIMENT / "data" / "game-data.json"


def require(condition: bool, code: str) -> None:
    if not condition:
        raise SystemExit("FAILED " + code)


def main() -> None:
    data = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    require(isinstance(data, dict) and data.get("version"), "DATA_ROOT")
    require(len(data.get("phases", {})) == 4, "PHASE_COUNT")
    require(len(data.get("weftlingTypes", {})) == 5, "WEFTLING_TYPES")
    require(len(data.get("doctrines", {})) == 3, "DOCTRINES")
    require(len(data.get("globalUpgrades", {})) >= 18, "GLOBAL_UPGRADES")
    require(all(len(items) >= 4 for items in data.get("doctrineUpgrades", {}).values()), "DOCTRINE_UPGRADES")
    require(len(data.get("permanentUpgrades", {})) >= 4, "PERMANENT_UPGRADES")
    encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    wrapper = "window.GW=window.GW||{};\nwindow.GW_DATA=" + encoded + ";\nwindow.GW.DATA=window.GW_DATA;\n"
    (EXPERIMENT / "data" / "game-data.js").write_text(wrapper, encoding="utf-8")
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="theme-color" content="#101424">
  <title>Glimweave</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#uiRoot">Skip to controls</a>
  <main id="gameShell">
    <canvas id="gameCanvas" aria-label="The living Sky Loom and drifting Glim field"></canvas>
    <section id="uiRoot" tabindex="-1" aria-label="Glimweave controls and status"></section>
  </main>
  <div id="announcer" class="sr-only" aria-live="polite" aria-atomic="true"></div>
  <output id="smoke-result" hidden>PENDING</output>
  <script src="bootstrap.js"></script>
  <script src="data/game-data.js"></script>
  <script src="src/utils.js"></script>
  <script src="src/state.js"></script>
  <script src="src/simulation.js"></script>
  <script src="src/integration.js"></script>
  <script src="src/test-bridge.js"></script>
  <script src="src/render.js"></script>
  <script src="src/ui.js"></script>
  <script src="src/test-bridge.js"></script>
  <script src="src/smoke-scenarios.js"></script>
  <script src="smoke.js"></script>
  <script>window.GW.init();</script>
</body>
</html>
"""
    (EXPERIMENT / "index.html").write_text(html, encoding="utf-8")
    print("PASS phases=4 weftlings=5 doctrines=3 upgrades=" + str(len(data["globalUpgrades"])))


if __name__ == "__main__":
    main()
