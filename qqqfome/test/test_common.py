import unittest

from .. import common as c


class CommonFuncTest(unittest.TestCase):
    def test_check_type_success_with_ref_is_a_value(self):
        try:
            c.check_type(1, "num", 1)
            a = 1
            c.check_type(1, "num", a)
        except ValueError:
            self.fail("check_type function raise a exception "
                      "when the check should be success.")

    def test_check_type_success_with_ref_is_a_type(self):
        try:
            c.check_type(1, "num", int)
        except ValueError:
            self.fail("check_type function raise a exception "
                      "when the check should be success.")

    def test_check_type_fail_with_ref_is_a_value(self):
        with self.assertRaises(ValueError):
            c.check_type(1, "string", "")
        with self.assertRaises(ValueError):
            string = ""
            c.check_type(1, 'string', string)

    def test_check_type_fail_with_ref_is_a_type(self):
        with self.assertRaises(ValueError):
            c.check_type(1, "string", str)
