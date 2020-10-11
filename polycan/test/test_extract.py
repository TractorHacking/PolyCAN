import unittest
from extract import *

class test_one(unittest.TestCase):

    def test1(self):
        with CanSignalExtractor() as CSE:
            CSE.add("61444")
            self.assertEqual(CSE.signals, ["61444"])
            CSE.remove("61444")
            self.assertEqual(CSE.signals, [])

    def test2(self):
        with CanSignalExtractor(["61444"]) as CSE:
            self.assertEqual(CSE.signals, ["61444"])



if __name__ == "__main__":
    unittest.main()
