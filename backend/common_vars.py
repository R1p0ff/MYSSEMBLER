import re
# Assembly
assembly_headers_regex = r"^\s*(DATA|CODE|data|code):"

assembly_data_header_regex = r"^\s*(DATA|data):"
assembly_code_header_regex = r"^\s*(CODE|code):"
assembly_data_variables_regex = r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s+(-?[0-9]+)\s*$"

assembly_labels_regex = r"^\s*(?!(?:DATA|CODE|data|code):\s*$)([a-zA-Z_][a-zA-Z0-9_]*):"

assembly_operations_regex = r"^\s*([A-Z]+)(?:\s+([^,\s]+)(?:\s*,\s*([^,\s]+))?)?"


# RISC V
riscv_headers_regex =r"^\s*\.[a-zA-Z0-9_]+"

riscv_labels_regex =r"^\s*([a-zA-Z0-9_]+):"

riscv_operations_regex =r"^\s*([a-z]+)\s+([^,\s]+)(?:\s*,\s*([^,\s]+))?(?:\s*,\s*([^,\s]+))?"


max_variables = {
    "MOV"  : 2,
    "ADD"  : 2,
    "SUB"  : 2,
    "AND"  : 2,
    "OR"   : 2,
    "XOR"  : 2,
    "NOT"  : 2,
    "SHL"  : 2,
    "SHR"  : 2,
    "INC"  : 1,
    "DEC"  : 1,
    "CMP"  : 2,
    "JMP"  : 1,
    "JLT"  : 1,
    "JEQ"  : 1,
    "JNE"  : 1,
    "NOP"  : 0,
    "JGT"  : 1,
    "JGE"  : 1,
    "JLE"  : 1,
    "JCR"  : 1,
    "PUSH" : 1,
    "POP"  : 1,
    "CALL" : 1,
    "RET"  : 0    
}