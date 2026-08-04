import unittest

import verify_mana_api_facade


class ManaApiFacadeVerifierTest(unittest.TestCase):
    def test_worker_and_independent_contracts(self) -> None:
        self.assertEqual(0, verify_mana_api_facade.main())


if __name__ == "__main__":
    unittest.main()
