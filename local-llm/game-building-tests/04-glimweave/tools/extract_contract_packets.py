"""Extract module-specific packets from the cloud-authored architecture contract."""

from __future__ import annotations

import re
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parents[1]
SOURCE = EXPERIMENT / "docs" / "ARCHITECTURE.md"
OUTPUT = EXPERIMENT / "docs" / "contracts"

PACKETS = {
    "utils": ["3. Global Namespace", "4.2 Validation", "6.5 `GW.Utils`", "7. Ownership", "11. Formatting", "13. Error", "15. Performance", "18. Implementation"],
    "state": ["3. Global Namespace", "4.2 Validation", "5. Serializable", "6.1 `GW.State`", "7. Ownership", "10. Persistence", "13. Error"],
    "simulation": ["3. Global Namespace", "4. Data Contract", "5. Serializable", "6.2 `GW.Simulation`", "7. Ownership", "8. Simulation", "9. Event", "12. Test API", "13. Error", "16. Automated", "19. Appendix"],
    "renderer": ["2.2 HTML", "3. Global Namespace", "5.1 Runtime", "6.3 `GW.Renderer`", "7. Ownership", "8.2 Glim", "11. Formatting", "12. Test API", "14. Accessibility", "15. Performance", "16. Automated"],
    "ui": ["2.2 HTML", "3. Global Namespace", "5. Serializable", "6.4 `GW.UI`", "7. Ownership", "9. Event", "10. Persistence", "11. Formatting", "12. Test API", "13. Error", "14. Accessibility", "16. Automated"],
}


def sections(lines: list[str]) -> list[tuple[str, int, int]]:
    headings: list[tuple[int, str, int]] = []
    for index, line in enumerate(lines):
        match = re.match(r"^(#{2,4})\s+(.+)$", line)
        if match:
            headings.append((len(match.group(1)), match.group(2), index))
    result: list[tuple[str, int, int]] = []
    for position, (level, title, start) in enumerate(headings):
        end = len(lines)
        for next_level, _, next_start in headings[position + 1:]:
            if next_level <= level:
                end = next_start
                break
        result.append((title, start, end))
    return result


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    indexed = sections(lines)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, selectors in PACKETS.items():
        chosen: list[str] = []
        seen: set[tuple[int, int]] = set()
        for selector in selectors:
            match = next(((title, start, end) for title, start, end in indexed if selector.lower() in title.lower()), None)
            if not match:
                raise SystemExit(f"Missing section for {name}: {selector}")
            _, start, end = match
            if (start, end) not in seen:
                chosen.extend(lines[start:end]); chosen.append(""); seen.add((start, end))
        header = f"# Glimweave — {name.title()} Implementation Contract\n\nExtracted verbatim by heading from `docs/ARCHITECTURE.md`.\n\n"
        (OUTPUT / f"{name}.md").write_text(header + "\n".join(chosen).rstrip() + "\n", encoding="utf-8")
    print("PASS packets=" + ",".join(PACKETS))


if __name__ == "__main__":
    main()
