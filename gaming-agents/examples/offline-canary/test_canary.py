from pathlib import Path
import unittest


class OfflineGameCanary(unittest.TestCase):
    def test_playable_contract_is_present_without_network_dependencies(self):
        source = Path(__file__).with_name("index.html").read_text(encoding="utf-8")
        self.assertIn('<button id="score"', source)
        self.assertIn("addEventListener('click'", source)
        self.assertIn("Score: 0", source)
        self.assertNotIn("https://", source)
        self.assertNotIn("http://", source)


if __name__ == "__main__":
    unittest.main()
