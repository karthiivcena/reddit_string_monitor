import unittest
from filters import should_forward

class FilterTests(unittest.TestCase):
    def test_empty_filters_allow(self):
        self.assertTrue(should_forward({"text":"Reddit alert"}, {"filters":{}}))
    def test_include_any(self):
        c={"filters":{"include_text":["reddit","python"],"match_mode":"any"}}
        self.assertTrue(should_forward({"text":"REDDIT alert"}, c))
        self.assertFalse(should_forward({"text":"email alert"}, c))
    def test_exclude(self):
        c={"filters":{"exclude_text":["ignore"]}}
        self.assertFalse(should_forward({"text":"IGNORE this"}, c))

if __name__ == "__main__": unittest.main()
