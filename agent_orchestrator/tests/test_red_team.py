import unittest

from agent_orchestrator.contracts import ContractError, Materialization
from agent_orchestrator.materialization import render_materialization
from agent_orchestrator.schema_validation import strict_json_loads


class RedTeamTests(unittest.TestCase):
    def test_duplicate_json_properties_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON property: turn"):
            strict_json_loads('{"turn": 1, "turn": 2}')

    def test_non_standard_json_numbers_are_rejected(self):
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "non-standard JSON constant"):
                strict_json_loads('{"score": ' + value + "}")

    def test_template_cannot_traverse_attributes_or_indexes(self):
        attacks = ("{text.__class__}", "{text[0]}")
        for template in attacks:
            with self.subTest(template=template), self.assertRaisesRegex(ContractError, "only direct fields"):
                render_materialization({"text": "safe"}, Materialization("out.md", "write", template))

    def test_template_cannot_embed_nested_model_output(self):
        with self.assertRaisesRegex(ContractError, "field must be scalar"):
            render_materialization(
                {"text": {"unexpected": "payload"}},
                Materialization("out.md", "write", "{text}"),
            )


if __name__ == "__main__":
    unittest.main()
