from CPU import CPU

def load_instructions(path):
    instrs = []
    with open(path, 'r') as f:
        for lineno, raw in enumerate(f, start=1):
            s = raw.strip()
            if not s:
                continue
            if len(s) != 32 or any(c not in "01" for c in s):
                raise ValueError(f"Line {lineno}: invalid instruction ({len(s)} bits): {s!r}")
            instrs.append(s)
    return instrs

if __name__ == "__main__":
    cpu = CPU()
    instructions = load_instructions('sample_program.txt')
    cpu.load_program(instructions)

    # Execute EXACTLY N instructions (where N = number of lines)
    for _ in range(len(instructions)):
        cpu.run_instruction()

    # Now dump to file
    cpu.dump("registers_dump.txt", "memory_dump.txt")

