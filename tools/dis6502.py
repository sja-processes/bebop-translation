#!/usr/bin/env python3
"""Minimal 6502 disassembler for the Be-Bop ROM.

usage: dis6502.py BANK CPUADDR [COUNT]
  BANK    PRG bank 0-7 (16 KB each; bank 7 is fixed at $C000)
  CPUADDR start address as seen by the CPU, e.g. C000 or 8123
  COUNT   number of instructions (default 40)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# mode: byte length and format
MODES = {
    'imp': (1, ''), 'acc': (1, 'A'), 'imm': (2, '#${:02X}'),
    'zp': (2, '${:02X}'), 'zpx': (2, '${:02X},X'), 'zpy': (2, '${:02X},Y'),
    'abs': (3, '${:04X}'), 'abx': (3, '${:04X},X'), 'aby': (3, '${:04X},Y'),
    'ind': (3, '(${:04X})'), 'izx': (2, '(${:02X},X)'), 'izy': (2, '(${:02X}),Y'),
    'rel': (2, '${:04X}'),
}

OPS = {}
def _op(names, mode, codes):
    for n, c in zip(names.split(), codes):
        OPS[c] = (n, mode)

_op('ORA AND EOR ADC STA LDA CMP SBC', 'izx', range(0x01, 0x100, 0x20))
_op('ORA AND EOR ADC STA LDA CMP SBC', 'zp',  range(0x05, 0x100, 0x20))
_op('ORA AND EOR ADC LDA CMP SBC', 'imm', [0x09, 0x29, 0x49, 0x69, 0xA9, 0xC9, 0xE9])
_op('ORA AND EOR ADC STA LDA CMP SBC', 'abs', range(0x0D, 0x100, 0x20))
_op('ORA AND EOR ADC STA LDA CMP SBC', 'izy', range(0x11, 0x100, 0x20))
_op('ORA AND EOR ADC STA LDA CMP SBC', 'zpx', range(0x15, 0x100, 0x20))
_op('ORA AND EOR ADC STA LDA CMP SBC', 'aby', range(0x19, 0x100, 0x20))
_op('ORA AND EOR ADC STA LDA CMP SBC', 'abx', range(0x1D, 0x100, 0x20))
_op('ASL ROL LSR ROR', 'zp', [0x06, 0x26, 0x46, 0x66])
_op('ASL ROL LSR ROR', 'acc', [0x0A, 0x2A, 0x4A, 0x6A])
_op('ASL ROL LSR ROR', 'abs', [0x0E, 0x2E, 0x4E, 0x6E])
_op('ASL ROL LSR ROR', 'zpx', [0x16, 0x36, 0x56, 0x76])
_op('ASL ROL LSR ROR', 'abx', [0x1E, 0x3E, 0x5E, 0x7E])
_op('STX LDX DEC INC', 'zp', [0x86, 0xA6, 0xC6, 0xE6])
_op('STX LDX DEC INC', 'abs', [0x8E, 0xAE, 0xCE, 0xEE])
_op('STX LDX', 'zpy', [0x96, 0xB6])
_op('DEC INC', 'zpx', [0xD6, 0xF6])
_op('LDX', 'aby', [0xBE])
_op('DEC INC', 'abx', [0xDE, 0xFE])
_op('LDX LDY CPY CPX', 'imm', [0xA2, 0xA0, 0xC0, 0xE0])
_op('BIT STY LDY CPY CPX', 'zp', [0x24, 0x84, 0xA4, 0xC4, 0xE4])
_op('BIT STY LDY CPY CPX', 'abs', [0x2C, 0x8C, 0xAC, 0xCC, 0xEC])
_op('STY LDY', 'zpx', [0x94, 0xB4])
_op('LDY', 'abx', [0xBC])
_op('BPL BMI BVC BVS BCC BCS BNE BEQ', 'rel', range(0x10, 0x100, 0x20))
_op('JSR', 'abs', [0x20])
_op('JMP', 'abs', [0x4C])
_op('JMP', 'ind', [0x6C])
_op('BRK PHP CLC PLP SEC RTI PHA CLI RTS PLA SEI DEY TXA TYA TXS TAY TAX '
    'CLV TSX INY DEX CLD INX NOP SED',
    'imp', [0x00, 0x08, 0x18, 0x28, 0x38, 0x40, 0x48, 0x58, 0x60, 0x68, 0x78,
            0x88, 0x8A, 0x98, 0x9A, 0xA8, 0xAA, 0xB8, 0xBA, 0xC8, 0xCA, 0xD8,
            0xE8, 0xEA, 0xF8])


def load_prg():
    romdir = os.path.join(ROOT, 'rom')
    name = next(f for f in os.listdir(romdir) if f.endswith('.nes'))
    data = open(os.path.join(romdir, name), 'rb').read()
    return data[16:16 + 8 * 0x4000]


def disasm(prg, bank, addr, count):
    base = 0xC000 if bank == 7 else 0x8000
    off = bank * 0x4000 + (addr - base)
    out = []
    for _ in range(count):
        op = prg[off]
        if op not in OPS:
            out.append('{:04X}  {:02X}        .db ${:02X}'.format(addr, op, op))
            off += 1; addr += 1
            continue
        name, mode = OPS[op]
        size, fmt = MODES[mode]
        raw = prg[off:off + size]
        if size == 2:
            val = raw[1]
            if mode == 'rel':
                val = (addr + 2 + (val - 256 if val > 127 else val)) & 0xFFFF
        elif size == 3:
            val = raw[1] | raw[2] << 8
        text = name + (' ' + fmt.format(val) if fmt else '')
        out.append('{:04X}  {:<8}  {}'.format(addr, raw.hex(' ').upper(), text))
        off += size; addr += size
    return out


if __name__ == '__main__':
    bank, addr = int(sys.argv[1]), int(sys.argv[2], 16)
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    print('\n'.join(disasm(load_prg(), bank, addr, count)))
