import re
# Assembly
assembly_headers_regex = r"^\s*(DATA|CODE|data|code):"

assembly_data_header_regex = r"^\s*(DATA|data):\s*$"
assembly_code_header_regex = r"^\s*(CODE|code):\s*$"
assembly_data_variables_regex = r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s+(-?[0-9]+)\s*$"

assembly_labels_regex = r"^\s*(?!(?:DATA|CODE|data|code):\s*$)([a-zA-Z_][a-zA-Z0-9_]*):"

assembly_operations_regex = r"^\s*([A-Z]+)(?:\s+([^,\s]+)(?:\s*,\s*([^,\s]+))?)?"


# RISC V
riscv_headers_regex =r"^\s*\.[a-zA-Z0-9_]+"
riscv_labels_regex =r"^\s*([a-zA-Z0-9_]+):"
riscv_operations_regex =r"^\s*([a-z]+)\s+([^,\s]+)(?:\s*,\s*([^,\s]+))?(?:\s*,\s*([^,\s]+))?"


