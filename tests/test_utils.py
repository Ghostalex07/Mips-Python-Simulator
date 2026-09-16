import unittest

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    decimal_to_unsigned_bin,
    decimal_to_signed_bin,
    unsigned_bin_to_decimal,
    signed_bin_to_decimal,
)


class TestConversions(unittest.TestCase):

    def test_unsigned_positive(self):
        self.assertEqual(decimal_to_unsigned_bin(10, 8), "00001010")

    def test_unsigned_too_large(self):
        with self.assertRaises(ValueError):
            decimal_to_unsigned_bin(256, 8)

    def test_unsigned_negative(self):
        with self.assertRaises(ValueError):
            decimal_to_unsigned_bin(-1, 8)

    def test_signed_negative(self):
        self.assertEqual(decimal_to_signed_bin(-1, 8), "11111111")
        self.assertEqual(decimal_to_signed_bin(-128, 8), "10000000")

    def test_signed_positive(self):
        self.assertEqual(decimal_to_signed_bin(127, 8), "01111111")

    def test_signed_too_small(self):
        with self.assertRaises(ValueError):
            decimal_to_signed_bin(-129, 8)

    def test_bin_to_unsigned(self):
        self.assertEqual(unsigned_bin_to_decimal("00001010"), 10)

    def test_bin_to_signed(self):
        self.assertEqual(signed_bin_to_decimal("11111111"), -1)
        self.assertEqual(signed_bin_to_decimal("01111111"), 127)

    def test_invalid_binary(self):
        with self.assertRaises(ValueError):
            unsigned_bin_to_decimal("000010a0")


if __name__ == "__main__":
    unittest.main()
