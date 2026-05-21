from backend.common_vars import *
from backend.opcodes_maps.opcodes import ISAs
from tabulate import tabulate
import re


def clean_comments_code_line(code_line):
    if ";" in code_line:
        code_line = code_line.split(";")
        code_line = code_line[0]
    return code_line

def format_code_line(code_line):
    code_line = clean_comments_code_line(code_line)
    code_line = " ".join(code_line.strip().split())
    code_line = code_line.split()
    if len(code_line) != 0:
        return code_line[0], "".join(code_line[1:])

def label_cleaner(label):
    label = label.replace(":", "")
    label = label.replace(" ", "")
    return label

def variable_name_cleaner(variable):
    variable = re.sub(' +', ' ', variable.strip())
    variable = variable.split(" ")
    return variable[0]

def operation_extractor(code_line):
    operation, variables = format_code_line(code_line)
    return operation

def ret_pop_checker(code_line):
    operation = None
    if clean_comments_code_line(code_line):
        operation = operation_extractor(code_line)
    if operation == "RET" or operation == "POP":
        return 2
    elif operation == None:
        return 0
    else:
        return 1

def dir_register(code_data, log_interface):
    data_headers = 0
    code_headers = 0
    labels = {}
    data_dir_counter = 0
    code_dir_counter = 0
    current_line = 0
    for code_line in code_data:
        if bool(re.search(assembly_code_header_regex, code_line)):
            code_label_line = current_line
        
        code_line = code_line.strip()
        current_line +=1        

        if not (code_line):
            continue

        if (bool(re.search(assembly_data_header_regex, code_line))):
            data_headers+=1
            continue
        elif (bool(re.search(assembly_code_header_regex, code_line))):
            code_headers+=1
            continue


        elif (code_headers == 1):
            is_line_label = (bool(re.search(assembly_labels_regex, code_line)))
            
            if is_line_label:
                labels[label_cleaner(code_line)] = code_dir_counter
                
                clean_label = code_line.split(":")
                if len(clean_label) > 1 and clean_label[1].strip():
                    code_dir_counter += ret_pop_checker(clean_label[1])
            
            else:
                code_dir_counter += ret_pop_checker(code_line)

        elif ((data_headers == 1) and (code_headers == 0)):
            is_register_label = (bool(re.search(assembly_data_variables_regex, code_line)))
            
            if is_register_label:
                labels[variable_name_cleaner(code_line)] = data_dir_counter
                data_dir_counter += 1

    if (data_headers != 1 or code_headers != 1):
        # (LOG)
        log_interface("WARNING: invalid headers", color = "#b70000")
        exit()
    
    return labels, code_label_line

def identify_procedure(code_line, code_language):
    identified_procedure = None
    regex_assembly = [assembly_headers_regex, assembly_labels_regex, assembly_operations_regex]
    regex_riscv = [assembly_headers_regex, assembly_labels_regex, assembly_operations_regex]

    if code_language == "RISCV":
        regex = regex_riscv
    elif code_language == "ASSEMBLY":
        regex = regex_assembly

    if (re.match(regex[0], code_line)):
        identified_procedure = "Header"
    elif re.match(regex[1], code_line):
        identified_procedure = "Label"
    elif re.match(regex[2], code_line):
        identified_procedure = "Operation"
    return identified_procedure

def operation(code_line, code_labels, log_interface):
    operation, variables = format_code_line(code_line)
    variables = variables.split(",")[:max_variables[operation]]    

    if max_variables[operation] == 0:
        return operation

    variable_mapping = []
    for variable in variables:
        if variable.isnumeric():
            variable_mapping.append("LIT")
        elif isinstance(variable, int):
            variable_mapping.append("LIT")
        
        elif "(" in variable:
            variable = variable.replace("(", "")
            variable = variable.replace(")", "")
            if ((variable.isnumeric()) or (variable in code_labels) or ("DIR" in variable)):
                variable_mapping.append("(DIR)")
            else:
                variable_mapping.append("(B)")

        elif (variable in code_labels):
            variable_mapping.append("DIR")

        else:
            variable_mapping.append(variable)

    variable_mapping = ",".join(variable_mapping)

    # (LOG)
    log_interface(f"Mapped operation to key {operation} {variable_mapping}", color="#2cde85")
    return f"{operation} {variable_mapping}"

def hex_converter(litopcode, log_interface):
    opcode_bytes = [litopcode[:8], litopcode[8:16],litopcode[16:24], litopcode[24:32], litopcode[32:40]]
    hex_bytes = []
    # 00 0E E0 0E 01
    for byte in opcode_bytes:
        resultado = f"{int(byte,2):02X}"
        hex_bytes.append(resultado)
    log_interface(f"Created hex ({" ".join(hex_bytes)}) for operation {litopcode}", color="#2B885A")
    return hex_bytes

def format_charge_operation(value, opcodes, selected_operation, labels, log_interface):
    formatted = operation(selected_operation, labels, log_interface)
    try:
        opcode = opcodes[formatted]
    except:
        log_interface(f"WARNING: invalid operation: {formatted}", color = "#ff0000")
        return None
    lit = str(bin(value))[2:]
    lit = f"{"0"*(16-len(lit))}{lit}"
    return opcode, lit

def addressing(i, lit, opcode, log_interface):
    binary_address = str(bin(int(i)))[2:]
    binary_address = f"{"0"*(12-len(binary_address))}{binary_address}"
    addressed_opcode = f"{binary_address}{lit}{opcode}"
    addressed_hex = hex_converter(addressed_opcode, log_interface)
    return binary_address, addressed_opcode, addressed_hex

def data_instructions(data_lines, labels, opcodes, log_interface):
    necessary_instructions = 0
    data_labels = []
    direction = 0
    i=0
    charge_opcodes = []
    charge_opcodes_hexadecimals = []
    for code_line in data_lines:
        if not clean_comments_code_line(code_line).strip():
            label, value = format_code_line(code_line)
            if not value:
                continue
        if not (bool(re.search(assembly_data_header_regex, code_line))):
            label, value = format_code_line(code_line)
            if not value.isnumeric():
                log_interface("WARNING: invalid headers", color = "#ff0000")

            value = int(value.strip())
            operations = [f"MOV A,{value}", f"MOV (DIR),A"]
            
            opcode, lit = format_charge_operation(value, opcodes, operations[0], labels, log_interface)
            if lit == None:
                break
            binary_address, addressed_opcode, addressed_hex = addressing(i, lit, opcode, log_interface)            
            formatted_operation = operation(" ".join(format_code_line(operations[0])), labels, log_interface)
            charge_opcodes.append([f"({i})", operations[0], formatted_operation, f"{binary_address}", f"{lit}", f"{opcode}", " ".join(addressed_hex)])
            i+=1
            

            opcode, lit = format_charge_operation(direction, opcodes, operations[1], labels, log_interface)
            binary_address, addressed_opcode, addressed_hex = addressing(i, lit, opcode, log_interface)            
            formatted_operation = operation(" ".join(format_code_line(operations[1])), labels, log_interface)
            charge_opcodes.append([f"({i})", operations[0], formatted_operation, f"{binary_address}", f"{lit}", f"{opcode}", " ".join(addressed_hex)])
            i+=1

            data_labels.append(label)
            necessary_instructions+=2
            direction+=1

    return charge_opcodes, charge_opcodes_hexadecimals, necessary_instructions, data_labels, i

def code_instructions(code_lines, labels, opcodes, log_interface,charge_cost = 0):
    i = 0+charge_cost
    columns = []
    code_opcodes_hexadecimals = []
    for code_line in code_lines:
        code_line = code_line.strip()
        if not format_code_line(code_line):
            continue
        procedure = identify_procedure(code_line, "ASSEMBLY")
        if procedure is None:
            continue

        log_interface(f"{procedure} identified in the line {code_line}")
        
        if procedure == "Operation":
            formatted = operation(code_line, labels, log_interface)
            try:
                opcode = opcodes[formatted]
            except:
                log_interface(f"WARNING: invalid operation: {formatted}", color = "#b70000")
                return None

            operation_data, variables = format_code_line(code_line)
            
            variables = variables.split(",")
            lit = "0"*16
            for variable in variables:
                if ("LIT" in formatted) and (re.sub(r'\D',"", variable)).isnumeric():
                    # (LOG)
                    log_interface(f"LITERAL VALUE identified in the line {code_line}, value = {variable}")
                    lit = re.sub(r'\D',"", variable)
                    lit = str(bin(int(lit)))[2:]
                    lit = f"{"0"*(16-len(lit))}{lit}"
                    # (LOG)
                    log_interface(f"LITERAL: {lit}", color="#2cde85")
                    break
                elif ("DIR" in formatted):
                    variable = variable.replace("(","")
                    variable = variable.replace(")","")
                    if variable in labels:
                        register = labels[variable]
                        # (LOG)
                        log_interface(f"REGISTER DIRECTION VARIABLE identified in the line {code_line}, {variable} = {register}")
                        lit = re.sub(r'\D',"", str(register))
                        lit = str(bin(int(lit)))[2:]
                        lit = f"{"0"*(16-len(lit))}{lit}"
                        # (LOG)
                        log_interface(f"LITERAL: {lit}", color="#2cde85")
                        break
                    elif variable.isnumeric():
                        # (LOG)
                        log_interface(f"REGISTER DIRECTION LITERAL identified in the line {code_line}, address = {variable}")
                        lit = str(bin(int(variable)))[2:]
                        lit = f"{"0"*(16-len(lit))}{lit}"
                        # (LOG)
                        log_interface(f"LITERAL: {lit}", color="#2cde85")
                        break
            
            binary_address, addressed_opcode, addressed_hex = addressing(i, lit, opcode, log_interface)            

            code_opcodes_hexadecimals.append(addressed_hex)
            columns.append([f"({i})" ," ".join(format_code_line(code_line.strip())), formatted, f"{binary_address}", f"{lit}", f"{opcode}", " ".join(addressed_hex)])
            
            i+=1

            active_operation = operation_extractor(code_line)
            if active_operation in ["RET", "POP"]:

                filling_binary_address = str(bin(int(i)))[2:]
                filling_binary_address = f"{"0"*(12-len(filling_binary_address))}{filling_binary_address}"
                filling_lit = "0"*16
                filling_opcode = "0"*20
                addressed_filling_opcode = f"{filling_binary_address}{filling_lit}{filling_opcode}"
                filling_addressed_hex = hex_converter(addressed_filling_opcode, log_interface)

                columns.append([f"({i})" ,f"{active_operation} FILL", "FILLING", f"{filling_binary_address}", f"{filling_lit}", f"{filling_opcode}", " ".join(filling_addressed_hex)])
                
                i+=1

    return columns, code_opcodes_hexadecimals

def instruction(code_input, selected_isa, log_interface):
    opcodes = ISAs[selected_isa]
    found_labels = []
    line_counter = 0
    clean_input = []
    for line in code_input:
        if clean_comments_code_line(line):
            clean_input.append(line)
    code_input = clean_input
    labels, code_position = dir_register(code_input, log_interface)

    for label in labels:
        found_labels.append(label)
        log_interface(f"Label \"{label}\" identified, value {hex(int(labels[label]))}")
        line_counter+=1

    data_lines = code_input[:code_position]
    code_lines = code_input[code_position+1:]

    table_data, charge_opcodes_hexadecimals, necessary_instructions, data_labels, charge_cost = data_instructions(data_lines, labels, opcodes, log_interface)
    for label in labels:
        if label not in data_labels:
            labels[label]+=necessary_instructions

    table_codes, code_opcodes_hexadecimals = code_instructions(code_lines, labels, opcodes, log_interface, charge_cost)

    hexadecimals = charge_opcodes_hexadecimals + code_opcodes_hexadecimals
    headers = ["#","Original", "Formatted", "ROM Address", "LIT", "Opcode", "HEX"]
    table_rows = table_data+table_codes
    result_table = tabulate(table_rows, headers)
    print(result_table)

    return result_table, hexadecimals

# TEST RISCV
#identified_procedure = re.match(regex_))
#identified_procedure = re.match(regex_))
#identified_procedure = re.match(regex_))


