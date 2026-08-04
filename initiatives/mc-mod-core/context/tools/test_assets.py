import unittest

import verify_assets


class AssetContractTest(unittest.TestCase):
    def test_asset_contract(self) -> None:
        self.assertEqual(0, verify_assets.main())


if __name__ == "__main__":
    unittest.main()
