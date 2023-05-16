# StackScript
## A pseudo-esoteric programming language with a unique memory management method.
---
## Quick Finder
[Memory](#memory)\
[Registers](#registers)\
[Instruction Reference](#instruction-reference)

---

## Memory
All memory is organized in **stacks**. All arithmetic must be performed on stacks.

Think of it like stacks of crates:
```
[1]
[3] [3]
[2] [5]
-------
 1   2
```
When taking a crate off each stack, you can only take the top one off. This is the same in StackScript, where you can only interact with the value at the top (with a few exceptions).

---

## Registers
To make some operations possible, there are 4 **registers**:
- `v` - The value at the top of the last used stack.
- `s` - The size of the last used stack.
- `c` - The result of the last comparison, used by `jump`, `call`, and `ret` for conditional branching.
- `r` - A random value between 0-255, which changes every instruction.

---

## Instruction Reference
Usage: `instruction <required> [optional]`
| Instruction | Purpose | Affected Registers |
| - | - | - |
| `push <stack> [val1] [val2] ...` | Pushes one or more values to `stack`. | `s v` |
| `pop <stack> <n>` | Removes `n` items from `stack`. | `s v` |
| `clear <stack>` | Removes all items from `stack`. | `s v` |