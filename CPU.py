from RAM import RAM  
from regs import Regs  
from utils import (
    binary_to_decimal as binario_a_decimal,
    binary_to_decimal_signed as binario_a_decimal_con_signo,
    decimal_to_binary as decimal_a_binario,
    decimal_to_binary_signed as decimal_a_binario_con_signo
)

class CPU:

    def __init__(self): # create the constructor for the CPU class
        self.memory = RAM() # initialize the RAM class instance
        self.regs = Regs() # initialize the regs class instance

    def load_program(self, instructions):
        self.memory.reset()
        self.regs.reset()
        addr = RAM.INSTR_START
        self.memory.loading_mode = True
        for instr in instructions:
            if addr >= RAM.INSTR_END:
                raise IndexError("Program exceeds maximum instruction size")
            bin_addr = decimal_a_binario(addr, 32)
            self.memory.set(bin_addr, instr)
            addr += 4
        self.memory.loading_mode = False
        self.regs.set("PC", decimal_a_binario(RAM.INSTR_START, 32))

    def map_reg(self, idx):  # create method to map indices to register names
        reg_map = {
            0: "zero", 1: "at", 2: "v0", 3: "v1",
            4: "a0", 5: "a1", 6: "a2", 7: "a3",
            8: "t0", 9: "t1", 10: "t2", 11: "t3",
            12: "t4", 13: "t5", 14: "t6", 15: "t7",
            16: "s0", 17: "s1", 18: "s2", 19: "s3",
            20: "s4", 21: "s5", 22: "s6", 23: "s7",
            24: "t8", 25: "t9", 26: "k0", 27: "k1",
            28: "gp", 29: "sp", 30: "fp", 31: "ra",
            32: "PC",
        }
        if idx not in reg_map:
            raise IndexError(f"Invalid register index: {idx}")
        return reg_map[idx]  

    def run_instruction(self):  # create method to execute one instruction
        pc_val = self.regs.get("PC")  # get current PC value (32-bit binary string)
        pc_val_int = binario_a_decimal(pc_val)  # convert to integer
        pc_bin = pc_val  # already in binary format
        instr = self.memory.get(pc_bin)  # get instruction from memory
        opcode = instr[0:6]  # extract instruction opcode

        if opcode == "000000": # R-type instructions
            rs_bin = instr[6:11] # extract source register rs bits
            rt_bin = instr[11:16] # extract source register rt bits
            rd_bin = instr[16:21] # extract destination register rd bits
            funct  = instr[26:32] # extract function field for operation

            rs_idx = binario_a_decimal(rs_bin) # convert rs to numeric
            rt_idx = binario_a_decimal(rt_bin) # convert rt to numeric
            rd_idx = binario_a_decimal(rd_bin) # convert rd to numeric

            rs_name = self.map_reg(rs_idx) # get rs register name
            rt_name = self.map_reg(rt_idx) # get rt register name
            rd_name = self.map_reg(rd_idx) # get rd register name

            rs_val_bin = self.regs.get(rs_name) # get binary value of rs
            rt_val_bin = self.regs.get(rt_name) # get binary value of rt

            rs_val = binario_a_decimal_con_signo(rs_val_bin) # convert rs to signed value
            rt_val = binario_a_decimal_con_signo(rt_val_bin) # convert rt to signed value

            if funct == "100000": # ADD operation
                out = rs_val + rt_val # perform addition
                out_bin = decimal_a_binario_con_signo(out, 32) # convert result to binary
                self.regs.set(rd_name, out_bin) # store result in rd
            elif funct == "100010": # SUB operation
                out = rs_val - rt_val # perform subtraction
                out_bin = decimal_a_binario_con_signo(out, 32) # convert result to binary
                self.regs.set(rd_name, out_bin) # store result in rd
            elif funct == "100100": # AND operation
                out = rs_val & rt_val # perform logical AND
                out_bin = decimal_a_binario_con_signo(out, 32) # convert result to binary
                self.regs.set(rd_name, out_bin) # store result in rd
            elif funct == "100101": # OR operation
                out = rs_val | rt_val # perform logical OR
                out_bin = decimal_a_binario_con_signo(out, 32) # convert result to binary
                self.regs.set(rd_name, out_bin) # store result in rd
            elif funct == "000000": # SLL operation
                shamt = binario_a_decimal(instr[21:26])  # shift amount bits
                out = (rt_val % (1 << 32)) << shamt  # perform logical shift left
                out_bin = decimal_a_binario_con_signo(out, 32)  # convert result to binary
                self.regs.set(rd_name, out_bin)  # store result in rd
            elif funct == "000010":  # SRL operation
                shamt = binario_a_decimal(instr[21:26])  # shift amount bits
                out = (rt_val % (1 << 32)) >> shamt  # perform logical shift right
                out_bin = decimal_a_binario_con_signo(out, 32)  # convert result to binary
                self.regs.set(rd_name, out_bin)  # store result in rd
            elif funct == "101010":  # SLT operation (set on less than)
                out = 1 if rs_val < rt_val else 0
                out_bin = decimal_a_binario_con_signo(out, 32)
                self.regs.set(rd_name, out_bin)
            elif funct == "100011":  # SUBU operation (unsigned sub, no overflow)
                out = rs_val - rt_val
                out_bin = decimal_a_binario_con_signo(out, 32)
                self.regs.set(rd_name, out_bin)
            elif funct == "100111":  # NOR operation
                out = ~(rs_val | rt_val) & 0xFFFFFFFF
                out_bin = decimal_a_binario_con_signo(out, 32)
                self.regs.set(rd_name, out_bin)
            elif funct == "001100":  # SYSCALL (nop for simulator)
                pass

        elif opcode == "100011":  # LW instruction
            rs_idx = binario_a_decimal(instr[6:11])
            rt_idx = binario_a_decimal(instr[11:16])
            imm = binario_a_decimal_con_signo(instr[16:32])

            base_reg = self.regs.get(self.map_reg(rs_idx))
            base = binario_a_decimal(base_reg)
            addr = base + imm
            addr_bin = decimal_a_binario(addr, 32)

            val = self.memory.get(addr_bin)
            self.regs.set(self.map_reg(rt_idx), val)

        elif opcode == "101011":  # SW instruction
            rs_idx = binario_a_decimal(instr[6:11])
            rt_idx = binario_a_decimal(instr[11:16])
            imm = binario_a_decimal_con_signo(instr[16:32])

            base_reg = self.regs.get(self.map_reg(rs_idx))
            base = binario_a_decimal(base_reg)
            addr = base + imm
            addr_bin = decimal_a_binario(addr, 32)

            val = self.regs.get(self.map_reg(rt_idx))
            self.memory.set(addr_bin, val)

        elif opcode == "001000":  # ADDI instruction
            rs_idx = binario_a_decimal(instr[6:11]) # get source register index
            rt_idx = binario_a_decimal(instr[11:16]) # get destination register index
            imm = binario_a_decimal_con_signo(instr[16:32]) # convert immediate to signed

            rs_val = binario_a_decimal_con_signo(self.regs.get(self.map_reg(rs_idx))) # get source value
            out = rs_val + imm # perform addition with immediate
            out_bin = decimal_a_binario_con_signo(out, 32) # convert result to binary

            self.regs.set(self.map_reg(rt_idx), out_bin) # store result in register

        elif opcode == "001100":  # ANDI instruction
            rs_idx = binario_a_decimal(instr[6:11]) # get source register index
            rt_idx = binario_a_decimal(instr[11:16]) # get destination register index
            imm = binario_a_decimal(instr[16:32]) # convert immediate (unsigned)

            rs_val = binario_a_decimal_con_signo(self.regs.get(self.map_reg(rs_idx))) # get source value
            out = rs_val & imm # perform logical AND
            out_bin = decimal_a_binario_con_signo(out, 32) # convert result to binary

            self.regs.set(self.map_reg(rt_idx), out_bin) # store result in register

        elif opcode == "001101": # ORI instruction
            rs_idx = binario_a_decimal(instr[6:11]) # get source register index
            rt_idx = binario_a_decimal(instr[11:16]) # get destination register index
            imm = binario_a_decimal(instr[16:32]) # convert immediate (unsigned)

            rs_val = binario_a_decimal_con_signo(self.regs.get(self.map_reg(rs_idx))) # get source value
            out = rs_val | imm # perform logical OR
            out_bin = decimal_a_binario_con_signo(out, 32) # convert result to binary

            self.regs.set(self.map_reg(rt_idx), out_bin) # store result in register

        elif opcode == "000100": # BEQ instruction
            rs_idx = binario_a_decimal(instr[6:11]) # get rs register index
            rt_idx = binario_a_decimal(instr[11:16]) # get rt register index
            imm = binario_a_decimal_con_signo(instr[16:32]) # convert offset

            rs_val = binario_a_decimal_con_signo(self.regs.get(self.map_reg(rs_idx))) # get rs value
            rt_val = binario_a_decimal_con_signo(self.regs.get(self.map_reg(rt_idx))) # get rt value

            if rs_val == rt_val:  # compare register values
                new_pc = pc_val_int + 4 + (imm << 2)  # calculate next PC
                new_pc_bin = decimal_a_binario(new_pc, 32)  # convert to binary
                self.regs.set("PC", new_pc_bin)  # update PC
                return  # exit early

        elif opcode == "000111":  # BGTZ instruction
            rs_idx = binario_a_decimal(instr[6:11])  # get rs register index
            imm = binario_a_decimal_con_signo(instr[16:32])  # convert offset

            rs_val = binario_a_decimal_con_signo(self.regs.get(self.map_reg(rs_idx)))  # get rs value

            if rs_val > 0:  # check if value is greater than zero
                new_pc = pc_val_int + 4 + (imm << 2)  # calculate next PC
                new_pc_bin = decimal_a_binario(new_pc, 32)  # convert to binary
                self.regs.set("PC", new_pc_bin)  # update PC
                return  # exit early

        elif opcode == "000101":  # BNE instruction
            rs_idx = binario_a_decimal(instr[6:11])  # get rs register index
            rt_idx = binario_a_decimal(instr[11:16])  # get rt register index
            imm = binario_a_decimal_con_signo(instr[16:32])  # convert offset

            rs_val = binario_a_decimal_con_signo(self.regs.get(self.map_reg(rs_idx)))  # get rs value
            rt_val = binario_a_decimal_con_signo(self.regs.get(self.map_reg(rt_idx)))  # get rt value

            if rs_val != rt_val:  # compare register values
                new_pc = pc_val_int + 4 + (imm << 2)  # calculate next PC
                new_pc_bin = decimal_a_binario(new_pc, 32)  # convert to binary
                self.regs.set("PC", new_pc_bin)  # update PC
                return  # exit early

        elif opcode == "000110":  # BLEZ instruction
            rs_idx = binario_a_decimal(instr[6:11])  # get rs register index
            imm = binario_a_decimal_con_signo(instr[16:32])  # convert offset

            rs_val = binario_a_decimal_con_signo(self.regs.get(self.map_reg(rs_idx)))  # get rs value

            if rs_val <= 0:  # check if value is less than or equal to zero
                new_pc = pc_val_int + 4 + (imm << 2)  # calculate next PC
                new_pc_bin = decimal_a_binario(new_pc, 32)  # convert to binary
                self.regs.set("PC", new_pc_bin)  # update PC
                return  # exit early

        self.regs.set("PC", decimal_a_binario(pc_val_int + 4, 32))  # update PC normally (+4 bytes)

    def run(self):  # create method to execute the full program
        while True:  # run until an error occurs
            try:  # try executing instructions
                self.run_instruction()  # execute one instruction
            except IndexError: # catch invalid access error
                break # stop execution if an error occurs

    def dump(self, reg_filename, mem_filename): # create method to save the state
        self.regs.dump(reg_filename) # save registers to file
        self.memory.dump_data(mem_filename) # save memory to file

