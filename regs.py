from utils import binary_to_decimal as binario_a_decimal

class Regs:

    def __init__(self):  # initialize the constructor of the Regs class
        self.registers = {
            "zero": "0"*32, "at": "0"*32,
            "v0": "0"*32, "v1": "0"*32,
            "a0": "0"*32, "a1": "0"*32, "a2": "0"*32, "a3": "0"*32,
            "t0": "0"*32, "t1": "0"*32, "t2": "0"*32, "t3": "0"*32,
            "t4": "0"*32, "t5": "0"*32, "t6": "0"*32, "t7": "0"*32,
            "s0": "0"*32, "s1": "0"*32, "s2": "0"*32, "s3": "0"*32,
            "s4": "0"*32, "s5": "0"*32, "s6": "0"*32, "s7": "0"*32,
            "t8": "0"*32, "t9": "0"*32,
            "k0": "0"*32, "k1": "0"*32,
            "gp": "0"*32, "sp": "0"*32, "fp": "0"*32, "ra": "0"*32,
            "PC": "0"*32,
        }

    def set(self, reg_idx: str, value):  # method to set the value of a register
        if reg_idx not in self.registers:  # if register does not exist, raise an error
            raise IndexError("Invalid register")
        if reg_idx == "zero":  # special case for 'zero' register
            return  # do nothing to preserve immutability of zero
        if not isinstance(value, str):  # all registers require a string
            raise ValueError("Register must be a 32-bit binary string")
        if len(value) != 32:  # check if binary string is 32 bits long
            raise ValueError("Register must be a 32-bit binary string")
        for c in value:  # verify each character in the string
            if c not in ("0", "1"):  # raise error if any character is invalid
                raise ValueError("Register must be a 32-bit binary string")
        self.registers[reg_idx] = value  # store the valid value in the register

    def get(self, reg_idx: str):  # method to get the value of a register
        if reg_idx not in self.registers:  # raise error if register does not exist
            raise IndexError("Invalid register") 
        return self.registers[reg_idx]  # return the value of the register

    def reset(self):  # method to reset all registers
        for key in self.registers:  # iterate over all register keys
            if key == "zero" or key == "at":  # skip zero and at registers
                continue
            self.registers[key] = "0"*32  # reset all others to 32 zeros
        self.registers["PC"] = "0"*32  # reset PC to 32-bit zero

    def dump(self, filename):  # method to save register state to a text file
        with open(filename, 'w') as f:  # open the file
            orden = ["PC", "zero"] + [f"t{i}" for i in range(8)] + [f"s{i}" for i in range(8)]
            for reg in orden:  # write each register in the specified order
                f.write(f"{reg} {self.registers[reg]}\n")  # write register name and value

