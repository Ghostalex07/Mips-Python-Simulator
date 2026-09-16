from RAM import RAM
from regs import Regs
from utils import (
    decimal_to_unsigned_bin as to_bin,
    decimal_to_signed_bin as to_signed_bin,
    unsigned_bin_to_decimal as to_uint,
    signed_bin_to_decimal as to_sint,
)

REG_MAP = {
    0: "zero", 1: "at", 2: "v0", 3: "v1",
    4: "a0", 5: "a1", 6: "a2", 7: "a3",
    8: "t0", 9: "t1", 10: "t2", 11: "t3",
    12: "t4", 13: "t5", 14: "t6", 15: "t7",
    16: "s0", 17: "s1", 18: "s2", 19: "s3",
    20: "s4", 21: "s5", 22: "s6", 23: "s7",
    24: "t8", 25: "t9", 26: "k0", 27: "k1",
    28: "gp", 29: "sp", 30: "fp", 31: "ra",
}


class CPU:

    def __init__(self):
        self.memory = RAM()
        self.regs = Regs()

    def load_program(self, instructions):
        self.memory.reset()
        self.regs.reset()
        self.memory.loading_mode = True
        addr = RAM.INSTR_BASE
        for instr in instructions:
            if addr >= RAM.INSTR_BASE + RAM.INSTR_SIZE:
                raise IndexError("Program too large for instruction segment")
            self.memory.set(to_bin(addr, 32), instr)
            addr += 4
        self.memory.loading_mode = False
        self.regs.set("PC", to_bin(RAM.INSTR_BASE, 32))
        self.regs.set("sp", to_bin(RAM.DATA_BASE, 32))

    def _reg_name(self, idx):
        if idx not in REG_MAP:
            raise IndexError(f"Invalid register index: {idx}")
        return REG_MAP[idx]

    def _branch(self, pc_int, imm):
        target = (pc_int + 4 + (imm << 2)) & 0xFFFFFFFF
        self.regs.set("PC", to_bin(target, 32))

    def run_instruction(self):
        pc_int = self.regs.get_pc_int()
        instr = self.memory.get(to_bin(pc_int, 32))
        opcode = instr[0:6]

        jumped = False
        if opcode == "000000":
            self._exec_r_type(instr)
        elif opcode == "100011":
            self._exec_lw(instr)
        elif opcode == "101011":
            self._exec_sw(instr)
        elif opcode == "001000":
            self._exec_addi(instr)
        elif opcode == "001100":
            self._exec_andi(instr)
        elif opcode == "001101":
            self._exec_ori(instr)
        elif opcode == "000100":
            jumped = self._exec_beq(instr, pc_int)
        elif opcode == "000101":
            jumped = self._exec_bne(instr, pc_int)
        elif opcode == "000111":
            jumped = self._exec_bgtz(instr, pc_int)
        elif opcode == "000110":
            jumped = self._exec_blez(instr, pc_int)
        elif opcode == "000010":
            jumped = self._exec_j(instr)
        else:
            raise IndexError(f"Unknown opcode: {opcode}")

        if not jumped:
            self.regs.set("PC", to_bin(pc_int + 4, 32))

    def _exec_r_type(self, instr):
        rs_idx = to_uint(instr[6:11])
        rt_idx = to_uint(instr[11:16])
        rd_idx = to_uint(instr[16:21])
        shamt = to_uint(instr[21:26])
        funct = instr[26:32]

        rs_name = self._reg_name(rs_idx)
        rt_name = self._reg_name(rt_idx)
        rd_name = self._reg_name(rd_idx)

        rs = to_sint(self.regs.get(rs_name))
        rt = to_sint(self.regs.get(rt_name))

        if funct == "100000":  # add
            result = rs + rt
        elif funct == "100010":  # sub
            result = rs - rt
        elif funct == "100100":  # and
            result = rs & rt
        elif funct == "100101":  # or
            result = rs | rt
        elif funct == "100111":  # nor
            result = ~(rs | rt) & 0xFFFFFFFF
        elif funct == "000000":  # sll
            result = (to_uint(self.regs.get(rt_name)) << shamt) & 0xFFFFFFFF
            self.regs.set(rd_name, to_bin(result, 32))
            return
        elif funct == "000010":  # srl
            result = to_uint(self.regs.get(rt_name)) >> shamt
            self.regs.set(rd_name, to_bin(result, 32))
            return
        elif funct == "101010":  # slt
            result = 1 if rs < rt else 0
        elif funct == "100011":  # subu
            result = rs - rt
        elif funct == "001100":  # syscall (nop)
            return
        else:
            raise IndexError(f"Unknown R-type funct: {funct}")

        self.regs.set(rd_name, to_signed_bin(result, 32))

    def _exec_lw(self, instr):
        base_idx = to_uint(instr[6:11])
        rt_idx = to_uint(instr[11:16])
        imm = to_sint(instr[16:32])

        base = to_uint(self.regs.get(self._reg_name(base_idx)))
        addr = (base + imm) & 0xFFFFFFFF
        self.regs.set(self._reg_name(rt_idx), self.memory.get(to_bin(addr, 32)))

    def _exec_sw(self, instr):
        base_idx = to_uint(instr[6:11])
        rt_idx = to_uint(instr[11:16])
        imm = to_sint(instr[16:32])

        base = to_uint(self.regs.get(self._reg_name(base_idx)))
        addr = (base + imm) & 0xFFFFFFFF
        self.memory.set(to_bin(addr, 32), self.regs.get(self._reg_name(rt_idx)))

    def _exec_addi(self, instr):
        rs_idx = to_uint(instr[6:11])
        rt_idx = to_uint(instr[11:16])
        imm = to_sint(instr[16:32])
        rs = to_sint(self.regs.get(self._reg_name(rs_idx)))
        self.regs.set(self._reg_name(rt_idx), to_signed_bin(rs + imm, 32))

    def _exec_andi(self, instr):
        rs_idx = to_uint(instr[6:11])
        rt_idx = to_uint(instr[11:16])
        imm = to_uint(instr[16:32])
        rs = to_sint(self.regs.get(self._reg_name(rs_idx)))
        self.regs.set(self._reg_name(rt_idx), to_signed_bin(rs & imm, 32))

    def _exec_ori(self, instr):
        rs_idx = to_uint(instr[6:11])
        rt_idx = to_uint(instr[11:16])
        imm = to_uint(instr[16:32])
        rs = to_sint(self.regs.get(self._reg_name(rs_idx)))
        self.regs.set(self._reg_name(rt_idx), to_signed_bin(rs | imm, 32))

    def _exec_beq(self, instr, pc_int):
        rs_idx = to_uint(instr[6:11])
        rt_idx = to_uint(instr[11:16])
        imm = to_sint(instr[16:32])
        rs = to_sint(self.regs.get(self._reg_name(rs_idx)))
        rt = to_sint(self.regs.get(self._reg_name(rt_idx)))
        if rs == rt:
            self._branch(pc_int, imm)
            return True
        return False

    def _exec_bne(self, instr, pc_int):
        rs_idx = to_uint(instr[6:11])
        rt_idx = to_uint(instr[11:16])
        imm = to_sint(instr[16:32])
        rs = to_sint(self.regs.get(self._reg_name(rs_idx)))
        rt = to_sint(self.regs.get(self._reg_name(rt_idx)))
        if rs != rt:
            self._branch(pc_int, imm)
            return True
        return False

    def _exec_bgtz(self, instr, pc_int):
        rs_idx = to_uint(instr[6:11])
        imm = to_sint(instr[16:32])
        rs = to_sint(self.regs.get(self._reg_name(rs_idx)))
        if rs > 0:
            self._branch(pc_int, imm)
            return True
        return False

    def _exec_blez(self, instr, pc_int):
        rs_idx = to_uint(instr[6:11])
        imm = to_sint(instr[16:32])
        rs = to_sint(self.regs.get(self._reg_name(rs_idx)))
        if rs <= 0:
            self._branch(pc_int, imm)
            return True
        return False

    def _exec_j(self, instr):
        target = to_uint(instr[6:32]) << 2
        self.regs.set("PC", to_bin(target, 32))
        return True

    def run(self):
        while True:
            pc = self.regs.get_pc_int()
            if pc < RAM.INSTR_BASE or pc >= RAM.INSTR_BASE + RAM.INSTR_SIZE:
                return
            instr = self.memory.get(to_bin(pc, 32))
            if instr == "0" * 32:
                return
            try:
                self.run_instruction()
            except IndexError:
                return

    def dump(self, reg_filename, mem_filename):
        self.regs.dump(reg_filename)
        self.memory.dump_data(mem_filename)
