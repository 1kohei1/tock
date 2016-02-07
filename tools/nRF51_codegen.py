#!/usr/bin/env python
# Generate chip specific code from CMSIS SVD definitions.
# To install the cmsis-svd dependency:
#   pip install -U cmsis-svd
from __future__ import print_function
from cmsis_svd.parser import SVDParser

def dump_json(parser):
    """Dump the SVD model as JSON."""
    import json
    svd_dict = parser.get_device().to_dict()
    print(json.dumps(svd_dict, sort_keys=True, indent=4,
        separators=(',', ': ')))

def get_peripheral_interrupts():
    # Cortex M0 supports up to 32 external interrupts
    # Source: See ARMv6-M Architecture Reference Manual,
    # Table C-2 "Programmers' model feature comparison"
    interrupts = [""] * 32

    parser = SVDParser.for_packaged_svd('Nordic', 'nrf51.svd')
    for peripheral in parser.get_device().peripherals:
        for intr in peripheral.interrupts:
            if interrupts[intr.value]:
                assert interrupts[intr.value] == intr.name
            else:
                interrupts[intr.value] = intr.name

    return interrupts

def dump_as_c_macro(name, lines, outfile, indent=0):
    print("#define %s \\" % name, file=outfile)
    for (n, line) in enumerate(lines):
        line = "\t" * indent + line
        if n < len(lines) - 1:
            line += " \\"
        print(line, file=outfile)

def dump_macros(interrupts, outfile):
    print("/* Automatically generated by nRF51_codegen.py */", file=outfile)

    lines = []
    for name in interrupts:
        if name:
            lines.append("%s_Handler," % name)
        else:
            lines.append("0, /* Reserved */")
    dump_as_c_macro("PERIPHERAL_INTERRUPT_VECTORS", lines, outfile, 1)

    lines = []
    for name in interrupts:
        if not name:
            continue
        lines.append('void %s_Handler(void) __attribute__ ' % name +
            '((weak, alias("Dummy_Handler")));')
    dump_as_c_macro("PERIPHERAL_INTERRUPT_HANDLERS", lines, outfile)

def main():
    interrupts = get_peripheral_interrupts()
    dump_macros(interrupts,
            open("src/chips/nrf51822/peripheral_interrupts.h", "w"))

if __name__ == "__main__":
    main()
