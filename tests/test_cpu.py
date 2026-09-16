import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    decimal_to_unsigned_bin,
    decimal_to_signed_bin,
    unsigned_bin_to_decimal,
    signed_bin_to_decimal,
)
from RAM import RAM
from RAM import RAM


class TestBinConversions(unittest.TestCase):

    def test_unsigned_positive(self):
        self.assertEqual(decimal_to_unsigned_bin(10, 8), "00001010")

    def test_unsigned_edge(self):
        self.assertEqual(decimal_to_unsigned_bin(255, 8), "11111111")

    def test_unsigned_too_large(self):
        with self.assertRaises(ValueError):
            decimal_to_unsigned_bin(256, 8)

    def test_unsigned_negative(self):
        with self.assertRaises(ValueError):
            decimal_to_unsigned_bin(-1, 8)

    def test_signed_positive(self):
        self.assertEqual(decimal_to_signed_bin(10, 8), "00001010")

    def test_signed_negative(self):
        self.assertEqual(decimal_to_signed_bin(-1, 8), "11111111")
        self.assertEqual(decimal_to_signed_bin(-128, 8), "10000000")

    def test_signed_too_small(self):
        with self.assertRaises(ValueError):
            decimal_to_signed_bin(-129, 8)

    def test_bin_to_unsigned_decimal(self):
        self.assertEqual(unsigned_bin_to_decimal("00001010"), 10)

    def test_bin_to_signed_decimal(self):
        self.assertEqual(signed_bin_to_decimal("11111111"), -1)
        self.assertEqual(signed_bin_to_decimal("00000001"), 1)

    def test_bin_to_signed_negative_edge(self):
        self.assertEqual(signed_bin_to_decimal("1000000"), -64)

    def test_invalid_char(self):
        with self.assertRaises(ValueError):
            unsigned_bin_to_decimal("0000101a")


class TestRegisters(unittest.TestCase):

    def setUp(self):
        from regs import Regs
        self.regs = Regs()

    def test_zero_is_readonly(self):
        self.regs.set("zero", "1" * 32)
        self.assertEqual(self.regs.get("zero"), "0" * 32)

    def test_set_and_get(self):
        self.regs.set("t3", "0" * 31 + "1")
        self.assertEqual(self.regs.get("t3"), "0" * 31 + "1")

    def test_bad_length(self):
        with self.assertRaises(ValueError):
            self.regs.set("t3", "01")

    def test_invalid_name(self):
        with self.assertRaises(IndexError):
            self.regs.get("nope")

    def test_reset(self):
        self.regs.set("t3", "1" * 32)
        self.regs.set("s5", "1" * 32)
        self.regs.reset()
        self.assertEqual(self.regs.get("t3"), "0" * 32)
        self.assertEqual(self.regs.get("s5"), "0" * 32)
        self.assertEqual(self.regs.get("zero"), "0" * 32)

    def test_all_known_names_present(self):
        for name in ["zero", "at", "v0", "a0", "t8", "s7", "k1", "gp", "sp", "fp", "ra"]:
            self.assertIn(name, self.regs.regs)


class TestRAM(unittest.TestCase):

    def setUp(self):
        from RAM import RAM
        self.RAM = RAM
        self.ram = RAM()

    def test_word_store_load(self):
        addr = decimal_to_unsigned_bin(RAM.DATA_BASE, 32)
        self.ram.loading_mode = True
        self.ram.set(addr, "1" * 32)
        self.assertEqual(self.ram.get(addr), "1" * 32)

    def test_alignment_check(self):
        addr = decimal_to_unsigned_bin(RAM.DATA_BASE + 2, 32)
        with self.assertRaises(IndexError):
            self.ram.set(addr, "0" * 32)

    def test_out_of_segment(self):
        addr = decimal_to_unsigned_bin(0x123, 32)
        with self.assertRaises(IndexError):
            self.ram.set(addr, "0" * 32)


class TestCPUInstructions(unittest.TestCase):

    def setUp(self):
        from CPU import CPU
        self.cpu = CPU()

    def _run(self, *instructions):
        self.cpu.load_program(list(instructions))
        self.cpu.run()

    def _reg(self, name):
        from utils import unsigned_bin_to_decimal
        return unsigned_bin_to_decimal(self.cpu.regs.get(name))

    def test_rtype_add(self):
        # addi t1, zero, 10 ; addi t2, zero, 20 ; add t3, t1, t2
        self._run(
            "00100000000010010000000000001010",
            "00100000000010100000000000010100",
            "00000001001010100101100000100000",
        )
        self.assertEqual(self._reg("t3"), 30)

    def test_rtype_and_is_zero(self):
        # addi t1, zero, 3 ; addi t2, zero, 5 ; and t3, t1, t2
        self._run(
            "00100000000010010000000000000011",
            "00100000000010100000000000000101",
            "00000001001010100101100000100100",
        )
        self.assertEqual(self._reg("t3"), 1)

    def test_lw_sw(self):
        # addi sp, sp, 0 ; addi t1, zero, 7 ; sw t1, 0(sp); lw t2, 0(sp)
        self.cpu.load_program([
            "00100011101000000000000000000000",
            "00100000000010010000000000000111",
            "10101111101010010000000000000000",
            "10001111101010100000000000000000",
        ])
        self.cpu.run()
        self.assertEqual(self._reg("t2"), 7)

    def test_beq_taken(self):
        # addi t1, zero, 5 ; beq t1, t1, 1 ; addi t2, zero, 1
        # branch skips the addi so t2 stays 0
        self._run(
            "00100000000010010000000000000101",
            "00010001001010010000000000000001",
            "00100000000010100000000000000001",
        )
        self.assertEqual(self._reg("t2"), 0)

    def test_bne_not_taken(self):
        # addi t1, zero, 5 ; bne t1, t1, 1 ; addi t2, zero, 1
        self._run(
            "00100000000010010000000000000101",
            "00010101001010010000000000000001",
            "00100000000010100000000000000001",
        )
        self.assertEqual(self._reg("t2"), 1)

    def test_jump_skips(self):
        # j <3rd instr> ; addi t1, zero, 1 ; addi t2, zero, 2
        # field = (INSTR_BASE + 8) >> 2 ; opcode 000010
        field = decimal_to_unsigned_bin((RAM.INSTR_BASE + 8) >> 2, 26)
        self._run(
            "000010" + field,
            "00100000000010010000000000000001",
            "00100000000010100000000000000010",
        )
        self.assertEqual(self._reg("t2"), 2)


if __name__ == "__main__":
    unittest.main()
