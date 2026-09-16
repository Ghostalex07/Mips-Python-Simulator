import sys
from CPU import CPU


def load_instructions(path):
    instructions = []
    with open(path) as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            if len(line) != 32 or any(c not in "01" for c in line):
                raise ValueError(f"Line {lineno}: not a valid 32-bit instruction: {line!r}")
            instructions.append(line)
    return instructions


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "sample_program.txt"

    cpu = CPU()
    instructions = load_instructions(filepath)
    cpu.load_program(instructions)
    cpu.run()

    cpu.dump("registers_dump.txt", "memory_dump.txt")
    print("Done. Output written to registers_dump.txt and memory_dump.txt")
