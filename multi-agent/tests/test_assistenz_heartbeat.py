from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from scripts.check_assistenz_heartbeat import _format, acknowledge, check


WORK_ORDER = """---
id: TEST-WO-001
status: ready
owner: assistenz
created: 2026-07-17
review_date: 2026-07-31
---

# Work Order: Test Action

## Approval Level

`routine`
"""

RISK_REGISTER = """---
id: TEST-RISK-001
status: active
owner: legal_risk_governance
created: 2026-07-17
review_date: 2026-07-31
---

# Risk Register

| ID | Risk | Category | Likelihood | Impact | Early signal | Mitigation | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R-001 | Test risk | governance | medium | high | signal | mitigate | chief_of_staff | open |
"""


class AssistenzHeartbeatTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "company" / "work-orders").mkdir(parents=True)
        (self.root / "company" / "work-orders" / "test.md").write_text(WORK_ORDER, encoding="utf-8")
        (self.root / "company" / "risk-register.md").write_text(RISK_REGISTER, encoding="utf-8")
        self.state = self.root / ".runtime" / "assistenz-heartbeat" / "state.json"
        self.today = date(2026, 7, 17)

    def test_first_run_reports_active_work_and_open_risk(self) -> None:
        changes = check(self.root, self.state, self.today)
        self.assertEqual(len(changes["new"]), 2)
        self.assertEqual(changes["changed"], [])
        self.assertEqual(changes["resolved"], [])

    def test_unchanged_second_run_is_quiet(self) -> None:
        check(self.root, self.state, self.today)
        self.assertTrue(acknowledge(self.root))
        changes = check(self.root, self.state, self.today)
        self.assertEqual(changes, {"new": [], "changed": [], "resolved": []})

    def test_resolved_and_changed_findings_are_distinguished(self) -> None:
        check(self.root, self.state, self.today)
        acknowledge(self.root)
        work_order = self.root / "company" / "work-orders" / "test.md"
        work_order.write_text(WORK_ORDER.replace("owner: assistenz", "owner: chief_of_staff"), encoding="utf-8")
        risk_register = self.root / "company" / "risk-register.md"
        risk_register.write_text(RISK_REGISTER.replace("| open |", "| mitigated |"), encoding="utf-8")

        changes = check(self.root, self.state, self.today)

        self.assertEqual(len(changes["changed"]), 1)
        self.assertEqual(changes["changed"][0]["owner"], "chief_of_staff")
        self.assertEqual(len(changes["resolved"]), 1)
        self.assertEqual(changes["resolved"][0]["kind"], "risk")
        self.assertEqual(changes["resolved"][0]["status"], "resolved")
        self.assertIn("status=resolved", _format(changes))

    def test_state_path_outside_runtime_is_rejected(self) -> None:
        outside = self.root / "state.json"
        with self.assertRaisesRegex(ValueError, "Heartbeat state must be"):
            check(self.root, outside, self.today)

    def test_prose_founder_gate_is_detected(self) -> None:
        work_order = self.root / "company" / "work-orders" / "test.md"
        work_order.write_text(
            WORK_ORDER.replace("`routine`", "Founder approval is required before execution."),
            encoding="utf-8",
        )
        changes = check(self.root, self.state, self.today)
        work = next(item for item in changes["new"] if item["kind"] == "work_order")
        self.assertEqual(work["approval_gate"], "founder-approval-required")

    def test_corrupt_state_fails_closed(self) -> None:
        self.state.parent.mkdir(parents=True)
        self.state.write_text("not-json", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Cannot read heartbeat state"):
            check(self.root, self.state, self.today)


if __name__ == "__main__":
    unittest.main()
