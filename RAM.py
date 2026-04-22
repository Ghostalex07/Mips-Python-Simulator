class RAM:

    INSTR_START = 0x00400000
    INSTR_END = 0x00400000 + 0x10000
    DATA_START = 0x10000000
    DATA_END = 0x10000000 + 0x10000

    def __init__(self):
        self.memory = {}
        self.loading_mode = False

    def set(self, addr: str, value: str):
        if len(addr) != 32 or len(value) != 32:
            raise IndexError("Address or value must be 32 bits")
        direccion = int(addr, 2)
        if direccion % 4 != 0:
            raise IndexError("Address not aligned (must be multiple of 4)")
        if direccion < 0 or direccion > 0xFFFFFFFF:
            raise IndexError("Address out of range")
        if not self.loading_mode:
            in_instr_range = self.INSTR_START <= direccion < self.INSTR_END
            in_data_range = self.DATA_START <= direccion < self.DATA_END
            if not (in_instr_range or in_data_range):
                raise IndexError(f"Address 0x{direccion:08X} not in valid segment")
        self.memory[direccion] = value

    def get(self, addr: str):
        if len(addr) != 32:
            raise IndexError("Address must be 32 bits")
        direccion = int(addr, 2)
        if direccion % 4 != 0:
            raise IndexError("Address not aligned (must be multiple of 4)")
        if direccion < 0 or direccion > 0xFFFFFFFF:
            raise IndexError("Address out of range")
        return self.memory.get(direccion, "0" * 32)

    def reset(self):
        self.memory.clear()

    def dump(self, filename: str):
        with open(filename, 'w') as f:
            for addr in sorted(self.memory):
                f.write(f"0x{addr:08X} {self.memory[addr]}\n")

    def dump_instr(self, filename: str):
        with open(filename, 'w') as f:
            for addr in sorted(self.memory):
                if self.INSTR_START <= addr < self.INSTR_END:
                    f.write(f"0x{addr:08X} {self.memory[addr]}\n")

    def dump_data(self, filename: str):
        with open(filename, 'w') as f:
            for addr in sorted(self.memory):
                if self.DATA_START <= addr < self.DATA_END:
                    f.write(f"0x{addr:08X} {self.memory[addr]}\n")