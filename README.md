<!-- # StackScript
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
| `push <stack> [val1] [val2] ...` | Pushes one or more values to `stack`. | `s` `v` |
| `pop <stack> <n>` | Removes `n` items from `stack`. | `s` `v` |
| `clear <stack>` | Removes all items from `stack`. | `s` `v` |
| `clone <stack> <n> [other]` | Clones the top item from `stack` to `other` (or itself) `n` times. | `s` `v` |
| `move <stack1> <stack2> <n>` | Moves `n` items from `stack1` to `stack2`. | `s` `v` |
| `read <stack>` | Reads the top item and size of `stack`. | `s` `v` |
| `print <stack>` | Prints the contents of `stack`, interpreted as ASCII codes, without a new line. | `s` `v` |
| `println <stack>` | Same as `print`, but creates a new line. | `s` `v` |
| `prntraw <stack>` | Prints the raw contents of `stack` and creates a new line. | `s` `v` |
| `prntnum <stack>` | Prints the top item of `stack` and does not create a new line. | `s` `v` |
| `clrscr` | Clears the output. | *None* |
| `input <stack>` | Gets user input and pushes the result to `stack`. | `s` `v` |
| `cmp <value>` | Compares the `v` register with `value`. | `c` |
| `cmpstk <stack>` | Compares the `v` register with the top item of `stack`. | `s` `c` |
| `jump [eq\|ne\|ls\|le\|gr\|ge] <line>` | Jumps to `line` (with optional conditional `c` register check). | *None* |
| `call [eq\|ne\|ls\|le\|gr\|ge] <line>` | Stores the return line and jumps to `line` (with optional conditional `c` register check). | *None* |
| `ret [eq\|ne\|ls\|le\|gr\|ge]` | Jumps to the last return line (with optional conditional `c` register check). | *None* |
| `inc <stack>` | Increments the top item of `stack`. | `s` `v` |
| `dec <stack>` | Decrements the top item of `stack`. | `s` `v` |
| `add <stack> <n>` | Adds `n` items at the top of `stack`. | `s` `v` |
| `sub <stack> <n>` | Subtracts `n` items at the top of `stack`, starting with the top item. | `s` `v` |
| `mul <stack> <n>` | Multiplies `n` items at the top of `stack`. | `s` `v` |
| `div <stack> <n>` | Divides `n` items at the top of `stack`, starting with the top item. | `s` `v` |
| `floor <stack>` | Rounds **down** the top item of `stack`. | `s` `v` |
| `ceil <stack>` | Rounds **up** the top item of `stack`. | `s` `v` |
| `inv <stack>` | Inverts the top item of `stack`. | `s` `v` |
| `pull <stack> <i>` | Pulls element `i` (bottom-up) to the top of `stack`. | `s` `v` |
| `drop <stack> <n>` | Drops the top item of `stack` down `n` spaces. | `s` `v` | -->

tag test