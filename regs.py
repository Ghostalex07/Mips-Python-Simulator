from utils import unsigned_bin_to_decimal


class Regs:

    ZERO32 = "0" * 32

    def __init__(self):
        self._init_regs()

    def _init_regs(self):
        names = [
            "zero", "at", "v0", "v1",
            "a0", "a1", "a2", "a3",
            "t0", "t1", "t2", "t3",
            "t4", "t5", "t6", "t7",
            "s0", "s1", "s2", "s3",
            "s4", "s5", "s6", "s7",
            "t8", "t9",
            "k0", "k1",
            "gp", "sp", "fp", "ra",
        ]
        self.regs = {name: self.ZERO32 for name in names}
        self.regs["PC"] = self.ZERO32

    def set(self, name, value):
        if name not in self.regs:
            raise IndexError(f"Invalid register: {name}")
        if name == "zero":
            return
        if not isinstance(value, str) or len(value) != 32:
            raise ValueError(f"Register {name} must be a 32-bit binary string")
        if any(c not in "01" for c in value):
            raise ValueError(f"Register {name} must contain only 0s and 1s")
        self.regs[name] = value

    def get(self, name):
        if name not in self.regs:
            raise IndexError(f"Invalid register: {name}")
        return self.regs[name]

    def get_pc_int(self):
        return unsigned_bin_to_decimal(self.regs["PC"])

    def reset(self):
        for name in self.regs:
            self.regs[name] = self.ZERO32

    def dump(self, filename):
        order = ["PC", "zero"] + [f"t{i}" for i in range(8)] + [f"s{i}" for i in range(8)]
        with open(filename, "w") as f:
            for name in order:
                f.write(f"{name} {self.regs[name]}\n")
