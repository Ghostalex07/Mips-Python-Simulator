# Mips-Simulator

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)

A small MIPS processor simulator written in Python. It reads raw 32-bit machine code, executes it, and dumps the final state of registers and memory to text files. Built as a personal project to understand how a CPU actually runs instructions.

## How it works

The simulator mimics a simplified MIPS datapath:

- **`RAM.py`** — word-addressed memory split into an instruction segment (`0x00400000`) and a data segment (`0x10000000`).
- **`regs.py`** — the 32 general-purpose registers plus `PC`, all stored as 32-bit binary strings.
- **`CPU.py`** — fetches, decodes and executes one instruction at a time: R-type, I-type and J-type formats.
- **`utils.py`** — conversions between integers and fixed-width binary strings (unsigned and two's complement).
- **`sim.py`** — entry point that loads a program file and runs it.

## Usage

```bash
python3 sim.py                        # uses sample_program.txt
python3 sim.py my_program.txt         # or pass your own file
```

The program file must contain one 32-bit instruction per line. After execution two files are produced:

- `registers_dump.txt` — final value of every register
- `memory_dump.txt` — contents of the data segment

## Sample program

The included `sample_program.txt` sums `1+1+1` in a loop and stores the result:

| Address   | Instruction            | Effect                 |
|-----------|------------------------|------------------------|
| 0x00400000| addi t1, zero, 3       | loop counter = 3       |
| 0x00400004| addi t2, zero, 1       | increment              |
| 0x00400008| add t3, t3, t2         | result += increment    |
| 0x0040000C| addi t1, t1, -1        | counter -= 1           |
| 0x00400010| bne t1, zero, -3       | loop while counter > 0 |
| 0x00400014| sw t3, 0(sp)           | store result in memory |

Expected output: `t3 = 3` and `0x10000000 = 3`.

## Supported instructions

R-type: `add`, `sub`, `and`, `or`, `nor`, `sll`, `srl`, `slt`, `subu`

I-type: `addi`, `andi`, `ori`, `lw`, `sw`, `beq`, `bne`, `bgtz`, `blez`

J-type: `j`

The `zero` register is read-only and `$sp` is initialized to the base of the data segment when a program is loaded.

## License

MIT — see [LICENSE](LICENSE).