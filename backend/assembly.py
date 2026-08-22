from backend.common_vars import *
from backend.opcodes_maps.opcodes import ISAs, max_variables_assembly
from tabulate import tabulate
import re


#? Remove comments from the lines, starting from the first detected semicolon.
def clean_comments_code_line(code_line):
    if ";" in code_line:
        code_line = code_line.split(";")[0]
    if "//" in code_line:
        code_line = code_line.split("//")[0]
    return code_line

#? Format the lines by removing comments and separating the operation from the arguments.
def format_code_line(code_line):
    code_line = clean_comments_code_line(code_line)
    code_line = code_line.strip().split()
    if len(code_line) != 0:
        return code_line[0], "".join(code_line[1:])

#? Cleans labels of extra characters and checks syntax rules.
def label_cleaner(label):
    label = label.replace(" ", "")

    if label.count(":") > 1:
        raise ValueError(f"Sintaxis error: Label '{label}' has to many ':'")
    
    if not label.endswith(":"):
        raise ValueError(f"Sintaxis error: Label '{label}' must end with ':'")

    label = label.replace(":", "")

    return label

#? Extract the variable names in DataSegment.
def variable_name_cleaner(variable):
    if not isinstance(variable, str):
        raise TypeError(f"Se esperaba texto, pero se recibió: {type(variable)}")
    variable = variable.split()
    if len(variable) == 0:
        raise ValueError("Error: Tried to read empty line.")
    return variable[0]

#? Checks whether the operation is RET or POP to calculate the required cycles.
def ret_pop_checker(code_line):
    operation = None
    if clean_comments_code_line(code_line):
        formated = format_code_line(code_line)
        operation = formated[0] if formated else None
    if operation == None:
        return 0
    else:
        return 1

#? Checks for variables and labels, assigning their memory directions.
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
                code_line = code_line.split(":", 1)
                label_part = code_line[0].strip() + ":" 

                if len(code_line) > 1:
                    instruction_part = code_line[1].strip()
                else:
                    instruction_part = ""

                try:
                    clean_label_name = label_cleaner(label_part)
                    labels[clean_label_name] = code_dir_counter
                except ValueError as error_msg:
                    log_interface(f"ERROR: {str(error_msg)}", color="#b70000")
                    raise ValueError(error_msg)

                if instruction_part:
                    code_dir_counter += ret_pop_checker(instruction_part)
            
            else:
                if not bool(re.search(assembly_operations_regex, code_line)):
                    log_interface(f"ERROR: Invalid line or instruction", color="#b70000")
                    raise ValueError(f"Sintaxis error: Invalid line or instruction {code_line}")
                code_dir_counter += ret_pop_checker(code_line)

        elif ((data_headers == 1) and (code_headers == 0)):
            is_register_label = (bool(re.search(assembly_data_variables_regex, code_line)))
            
            if is_register_label:
                labels[variable_name_cleaner(code_line)] = data_dir_counter
                data_dir_counter += 1

    if (data_headers != 1 or code_headers != 1):
        # (LOG)
        log_interface("WARNING: invalid headers", color = "#b70000")
        raise ValueError("Invalid headers: No data or code headers.")
    
    return labels, code_label_line

#? Identifies whether a given line is a Header, a Label, or an Operation.
def identify_procedure(code_line):
    #** This approach can detect invalid lines as operations, however,
    #** subsequent processing steps detect that the "operation" is invalid.
    identified_procedure = None
    regex_assembly = [assembly_headers_regex, assembly_labels_regex, assembly_operations_regex]

    regex = regex_assembly

    if (re.match(regex[0], code_line)):
        identified_procedure = "Header"
    elif re.match(regex[1], code_line):
        identified_procedure = "Label"
    elif re.match(regex[2], code_line):
        identified_procedure = "Operation"
    return identified_procedure

#? Identifies the opcode key of an operation.
def operation(code_line, code_labels, log_interface):
    operation, variables = format_code_line(code_line)
    try:
        variables = variables.split(",")[:max_variables_assembly[operation]]    
    except:
        log_interface(f"WARNING: invalid operation: {operation}", color = "#ff0000")
        raise ValueError(f"WARNING: invalid operation: {operation}")

    if max_variables_assembly[operation] == 0:
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
            elif variable.strip() == "B":
                variable_mapping.append("(B)")
            else:
                log_interface(f"WARNING: invalid register or label: {variable}", color = "#ff0000")
                return None

        elif (variable in code_labels):
            dir_operations = ["JEQ", "JNE", "JGT", "JGE", "JLT", "JLE", "JCR", "JMP", "CALL"]
            if operation not in dir_operations:
                variable_mapping.append("LIT")
            else:
                variable_mapping.append("DIR")

        else:
            variable_mapping.append(variable)

    variable_mapping = ",".join(variable_mapping)

    # (LOG)
    log_interface(f"Mapped operation to key {operation} {variable_mapping}", color="#2cde85")
    return f"{operation} {variable_mapping}"

#? Encodes a data load operation, resolves its opcode, and converts the value to a 16-bit binary literal.
def encode_load_operation(value, opcodes, selected_operation, labels, log_interface):
    formatted = operation(selected_operation, labels, log_interface)
    try:
        opcode = opcodes[formatted]
    except:
        log_interface(f"WARNING: invalid operation: {formatted}", color = "#ff0000")
        raise ValueError(f"WARNING: invalid operation: {formatted}")

    lit = bin(value)[2:].zfill(16)

    return opcode, lit

#? Processes the data segment lines, generating the load and write instructions for each variable.
def data_instructions(data_lines, labels, opcodes, log_interface):
    necessary_instructions = 0
    data_labels = []
    direction = 0
    i=0
    charge_opcodes = []
    charge_opcodes_hexadecimals = []
    for code_line in data_lines:
        #** Ignore empty lines
        cleaned = clean_comments_code_line(code_line).strip()
        if not cleaned:
            continue

        #** Ignore data header lines
        if bool(re.search(assembly_data_header_regex, code_line)):
            continue

        label, value = format_code_line(code_line)
        if not value.strip().isnumeric():
            log_interface("WARNING: invalid data value", color="#ff0000")

        try:
            value = int(value.strip())
        except ValueError:
            log_interface(f"ERROR: Invalid numeric value for variable {label}", color="#b70000")
            raise ValueError(f"Invalid data value: {value}")

        operations = [f"MOV A,{value}", f"MOV (DIR),A"]
        
        opcode, lit = encode_load_operation(value, opcodes, operations[0], labels, log_interface)
        if lit == None:
            break
        binary_address, addressed_opcode, addressed_hex = addressing(i, lit, opcode, log_interface)            
        formatted_operation = operation(" ".join(format_code_line(operations[0])), labels, log_interface)
        charge_opcodes.append([f"({i})", operations[0], formatted_operation, f"{binary_address}", f"{lit}", f"{opcode}", " ".join(addressed_hex)])
        charge_opcodes_hexadecimals.append(addressed_hex)
        i+=1
        
        opcode, lit = encode_load_operation(direction, opcodes, operations[1], labels, log_interface)
        binary_address, addressed_opcode, addressed_hex = addressing(i, lit, opcode, log_interface)            
        formatted_operation = operation(" ".join(format_code_line(operations[1])), labels, log_interface)
        charge_opcodes.append([f"({i})", "WRITING", formatted_operation, f"{binary_address}", f"{lit}", f"{opcode}", " ".join(addressed_hex)])
        charge_opcodes_hexadecimals.append(addressed_hex)
        i+=1

        data_labels.append(label)
        necessary_instructions+=2
        direction+=1

    return charge_opcodes, charge_opcodes_hexadecimals, necessary_instructions, data_labels, i

#? Processes the code segment lines, resolving operations, literals, labels, and generating the final ROM instructions.
def code_instructions(code_lines, labels, opcodes, log_interface,charge_cost = 0):
    i = 0+charge_cost
    columns = []
    code_opcodes_hexadecimals = []
    for code_line in code_lines:
        code_line = code_line.strip()
        if not format_code_line(code_line):
            continue
        procedure = identify_procedure(code_line)
        if procedure is None:
            continue

        log_interface(f"{procedure} identified in the line {code_line}")
        
        if procedure == "Operation":
            formatted = operation(code_line, labels, log_interface)
            try:
                opcode = opcodes[formatted]
            except KeyError:
                log_interface(f"WARNING: invalid operation: {formatted}", color="#b70000")
                raise ValueError(f"WARNING: invalid operation: {formatted}")

            _, variables = format_code_line(code_line)
            
            variables = variables.split(",")
            lit = "0"*16
            for variable in variables:
                if ("LIT" in formatted):
                    if variable in labels:
                        lit = int(labels[variable])
                        lit = bin(lit)[2:].zfill(16)
                        # (LOG)
                        log_interface(f"LABEL VALUE: {lit}", color="#2cde85")
                        break
                    try:
                        lit = int(variable)
                        lit = bin(lit)[2:].zfill(16)
                        # (LOG)
                        log_interface(f"LITERAL VALUE identified in the line {code_line}, value = {variable}")
                        break
                    except ValueError:
                        pass

                elif ("DIR" in formatted):
                    variable = variable.replace("(","")
                    variable = variable.replace(")","")
                    if variable in labels:
                        register = labels[variable]
                        # (LOG)
                        log_interface(f"REGISTER DIRECTION VARIABLE identified in the line {code_line}, {variable} = {register}")
                        lit = re.sub(r'\D',"", str(register))
                        lit = bin(int(lit))[2:].zfill(16)
                        log_interface(f"LITERAL: {lit}", color="#2cde85")
                        break
                    elif variable.isnumeric():
                        # (LOG)
                        log_interface(f"REGISTER DIRECTION LITERAL identified in the line {code_line}, address = {variable}")
                        lit = bin(int(variable))[2:].zfill(16)
                    # (LOG)
                        log_interface(f"LITERAL: {lit}", color="#2cde85")
                        break
                elif ("INC" in formatted) or ("DEC" in formatted):
                    # (LOG)
                    log_interface(f"INCREASE LITERAL identified in the line {code_line}, address = {variable}")
                    lit = bin(int(1))[2:].zfill(16)
                    # (LOG)
                    log_interface(f"LITERAL: {lit}", color="#2cde85")
                    break
            binary_address, addressed_opcode, addressed_hex = addressing(i, lit, opcode, log_interface)

            code_opcodes_hexadecimals.append(addressed_hex)
            columns.append([f"({i})" ," ".join(format_code_line(code_line.strip())), formatted, f"{binary_address}", f"{lit}", f"{opcode}", " ".join(addressed_hex)])
            i+=1

    return columns, code_opcodes_hexadecimals

#? Orchestrates the entire assembly process: preprocessing, symbol table generation, data/code translation, and table formatting.
def instruction(code_input, selected_isa, log_interface):
    opcodes = ISAs[selected_isa]
    clean_input = []

    #** Preprocessing
    for line in code_input:
        if clean_comments_code_line(line):
            line_operation = format_code_line(line)
            line_operation = line_operation[0] if line_operation else None

            if line_operation == "POP" or line_operation == "RET":
                clean_input.append("DEC SP")
            clean_input.append(clean_comments_code_line(line))
    code_input = clean_input

    #** First pass: Label and headers directions
    labels, code_position = dir_register(code_input, log_interface)

    for label in labels:
        log_interface(f"Label \"{label}\" identified, value {hex(int(labels[label]))}")

    #** Separating the data segment from the code segment
    data_lines = code_input[:code_position]
    code_lines = code_input[code_position+1:]

    #** Second Pass: Data segment processing
    table_data, charge_opcodes_hexadecimals, necessary_instructions, data_labels, charge_cost = data_instructions(data_lines, labels, opcodes, log_interface)
    for label in labels:
        if label not in data_labels:
            labels[label]+=necessary_instructions

    #** Data declaration instructions
    table_codes, code_opcodes_hexadecimals = code_instructions(code_lines, labels, opcodes, log_interface, charge_cost)

    #** Code segment processing
    hexadecimals = charge_opcodes_hexadecimals + code_opcodes_hexadecimals
    headers = ["#","Original", "Formatted", "ROM Address", "LIT", "Opcode", "HEX"]
    table_rows = table_data+table_codes
    result_table = tabulate(table_rows, headers)
    # print(result_table)

    log_interface(f"OK: Assembly completed successfully", color="#1bd252")

    return result_table, hexadecimals

#? Converts a binary instruction string (literal + opcode) into  a list of 5 hexadecimal bytes (40 bits total).
def hex_converter(litopcode, log_interface):
    if len(litopcode) > 40:
        litopcode = litopcode[-40:]
    elif len(litopcode) < 40:
        litopcode = litopcode.zfill(40)

    opcode_bytes = [litopcode[i:i+8] for i in range(0, 40, 8)]

    #opcode_bytes = [litopcode[:8], litopcode[8:16],litopcode[16:24], litopcode[24:32], litopcode[32:40], litopcode[40:48]]
    hex_bytes = []
    # 00 0E E0 0E 01
    for byte in opcode_bytes:
        resultado = f"{int(byte,2):02X}"
        hex_bytes.append(resultado)
    log_interface(f"Created hex ({" ".join(hex_bytes)}) for operation {litopcode}", color="#2B885A")
    return hex_bytes

#? Formats the complete instruction binary word by combining the ROM address, literal, and opcode, then converts it to hex.
def addressing(i, lit, opcode, log_interface):
    binary_address = bin(int(i))[2:].zfill(12)

    #** Testing output
    addressed_opcode = f"{lit}{opcode}"

    if len(addressed_opcode) < 40:
        addressed_opcode = addressed_opcode.zfill(40)
    elif len(addressed_opcode) > 40:
        addressed_opcode = addressed_opcode[-40:]

    addressed_hex = hex_converter(addressed_opcode, log_interface)

    #** Real output
    addressed_opcode = f"{binary_address}{lit}{opcode}"

    return binary_address, addressed_opcode, addressed_hex

















