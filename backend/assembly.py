from mapas_opcodes.opcodes_assembly import opcodes_assembly
from common_vars import *
import tabulate
import re




def format_code_line(code_line):
    code_line = " ".join(code_line.split())
    code_line = code_line.split()
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
    operation = operation_extractor(code_line)
    if operation == "RET" or operation == "POP":
        return 2
    else:
        return 1

def dir_register(code_data):
    data_headers = 0
    code_headers = 0
    labels = {}
    data_dir_counter = -1
    code_dir_counter = -1
    current_line = 0
    for code_line in code_data:
        code_line = code_line.strip()
        current_line +=1
        is_line_label = (bool(re.search(assembly_labels_regex, code_line)))
        is_register_label = (bool(re.search(assembly_data_variables_regex, code_line)))
        

        if not code_line:
            continue

        if (bool(re.search(assembly_data_header_regex, code_line))):
            data_headers+=1
        elif (bool(re.search(assembly_code_header_regex, code_line))):
            code_headers+=1

        elif (code_headers == 1):
            if is_line_label:
                labels[label_cleaner(code_line)] = code_dir_counter+1
            else:
                code_dir_counter += ret_pop_checker(code_line)

        elif ((data_headers == 1) and (code_headers == 0)):
            if is_register_label:
                labels[variable_name_cleaner(code_line)] = data_dir_counter+1
                data_dir_counter += 1        
    if (data_headers != 1 or code_headers != 1):
        print("ERROR: Headers invalidos")
        exit()
    
    return labels

    
def identify_procedure(code_line, code_lenguage):
    identified_procedure = None
    regex_assembly = [assembly_headers_regex, assembly_labels_regex, assembly_operations_regex]
    regex_risc5 = [assembly_headers_regex, assembly_labels_regex, assembly_operations_regex]

    if code_lenguage == "RISCV":
        regex = regex_assembly
    elif code_lenguage == "ASSEMBLY":
        regex = regex_risc5

    if (re.match(regex[0], code_line)):
        identified_procedure = "Header"
    elif re.match(regex[1], code_line):
        identified_procedure = "Label"
    elif re.match(regex[2], code_line):
        identified_procedure = "Operation"
    return identified_procedure

def operation(code_line, code_labels):
    variable_labels = []
    operation, variables = format_code_line(code_line)
    variables = variables.split(",")[:max_variables[operation]]    
    if max_variables[operation] == 0:
        #opcode = opcodes_assembly[f"{operation}"]
        #print(f"{opcode}\n")
        return operation
    mapeo_variables = []
    for variable in variables:
        if variable.isnumeric():
            mapeo_variables.append("LIT")
        elif isinstance(variable, int):
            mapeo_variables.append("LIT")
        
        elif "(" in variable:
            variable = variable.replace("(", "")
            variable = variable.replace(")", "")
            if ((variable.isnumeric()) or (variable in code_labels)):
                mapeo_variables.append("(DIR)")
            else:
                mapeo_variables.append("(B)")

        elif (variable in code_labels):
            mapeo_variables.append("DIR")

        else:
            mapeo_variables.append(variable)

    mapeo_variables = ",".join(mapeo_variables)

    #opcode = opcodes_assembly[f"{operation} {mapeo_variables}"]
    #print(f"{operation} {mapeo_variables}")
    #print(f"{opcode}\n")
    #return opcode, operation
    return f"{operation} {mapeo_variables}"



def opcode_translation(formated_operation):
    return opcodes_assembly[formated_operation]


#def create_variables(code_input):

def instruction(code_input):
    labels = dir_register(code_input)
    print(labels)

    columnas = []
    for code_line in code_input:
        if not (code_line):
            continue
        procedure = identify_procedure(code_line, "ASSEMBLY")

        if procedure == "Header":
            None


        if procedure == "Label":
            None

        if procedure == "Operation":
            formateada = operation(code_line, labels)
            opcode = opcode_translation(formateada)
            
            if ("LIT" in formateada) and (re.sub(r'\D',"", code_line)).isnumeric():
                lit = re.sub(r'\D',"", code_line)
                lit = str(bin(int(lit)))[2:]
                lit = f"{"0"*(16-len(lit))}{lit}"
            elif ("DIR" in formateada):
                operation, variables = format_code_line(code_line)
                for variable in variables:
                    if variable in labels:
                        lit = re.sub(r'\D',"", labels[variable])
                        lit = str(bin(int(lit)))[2:]
                        lit = f"{"0"*(16-len(lit))}{lit}"
            else:
                lit = "0"*16

            columnas.append([code_line.strip(), formateada, f"{lit}{opcode}"])
        #print(f"Original: {code_line}\nIdentificado: {identify_procedure(code_line, "ASSEMBLY")}\n")
    headers = ["Original", "Formateada", "Opcode"]
    print(tabulate(columnas, headers))



# TEST RISCV
#identified_procedure = re.match(regex_))
#identified_procedure = re.match(regex_))
#identified_procedure = re.match(regex_))


