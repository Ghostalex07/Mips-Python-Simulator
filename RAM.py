class RAM:

    INSTR_BASE = 0x00400000
    INSTR_SIZE = 0x10000
    DATA_BASE = 0x10000000
    DATA_SIZE = 0x10000

    def __init__(self):
        self.memory = {}
        self.loading_mode = False

    def set(self, addr, value):
        if len(addr) != 32 or len(value) != 32:
            raise IndexError("Address and value must be 32-bit binary strings")
        direccion = int(addr, 2)
        if direccion % 4 != 0:
            raise IndexError(f"Address 0x{direccion:08X} not 4-byte aligned")
        if not self.loading_mode:
            if not (self.INSTR_BASE <= direccion < self.INSTR_BASE + self.INSTR_SIZE or
                    self.DATA_BASE <= direccion < self.DATA_BASE + self.DATA_SIZE):
                raise IndexError(f"Address 0x{direccion:08X} outside valid segments")
        self.memory[direccion] = value

    def get(self, addr):
        if len(addr) != 32:
            raise IndexError("Address must be a 32-bit binary string")
        direccion = int(addr, 2)
        if direccion % 4 != 0:
            raise IndexError(f"Address 0x{direccion:08X} not 4-byte aligned")
        return self.memory.get(direccion, "0" * 32)

    def reset(self):
        self.memory.clear()

    def dump_data(self, filename):
        with open(filename, "w") as f:
            for addr in sorted(self.memory):
                if self.DATA_BASE <= addr < self.DATA_BASE + self.DATA_SIZE:
                    f.write(f"0x{addr:08X} {self.memory[addr]}\n")
