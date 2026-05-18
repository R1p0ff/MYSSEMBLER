from assembly import *
from tabulate import tabulate
# TEST ASSEMBLY

input_console_content = "DAT:"
test_lines = [
    # --- Casos Correctos de Headers ---
    "r 2",                    # Header de datos estándar
    "CODE:",                    # Header de código estándar
    
    "CODE:",                    # Header de código estándar
    "  DATA:",                  # Header con espacios iniciales
    
    # --- Casos Correctos de Labels ---
    "main:",                    # Label corto
    "avoid_addition:",          # Label largo con guion bajo
    "mystery:",                 # Otro label de subrutina
    
    # --- Casos Correctos de Instrucciones de 2 Operandos ---
    "MOV A,2",                  # Registro e inmediato básico
    "MOV B, (fibTwo)",          # Registro y direccionamiento indirecto/memoria
    "ADD A, B",                 # Operación pura entre dos registros
    "CMP A,0",                  # Comparación típica de registro con cero
    "MOV (c), A",               # Destino en memoria, origen en registro
    "XOR A, B",                 # Operación lógica de dos operandos
    
    # --- Casos Correctos de Instrucciones de 1 Operando ---
    "JMP loop",                 # Salto incondicional a etiqueta
    "JLE end",                  # Salto condicional
    "CALL mystery",             # Llamada a subrutina (1 operando de dirección)
    "PUSH A",                   # Push de un registro al stack
    "POP B",                    # Pop desde el stack a un registro
    
    # --- Casos Correctos de Instrucciones sin Operandos ---
    "RET",                      # Retorno de subrutina (0 operandos)
    "NOP",                      # No operación
    "  RET  ",                  # Instrucción limpia rodeada de espacios
    
    # --- Casos "Borde" o Erróneos (Para probar robustez) ---
    "MOV A, 1, 2",              # ERROR: Tres operandos (Esto es ilegal en tu código propietario)
    "loop",                     # ERROR: Parece label pero le faltan los dos puntos ":"
    ".data",                    # ERROR: Formato de RISC-V con punto (no debería calzar con DATA:)
    "123label:",                # ERROR: Label que empieza con número (invalido en sintaxis estándar)
    "ADD A , B",                # Caso especial: Espacio antes de la coma (tu regex debería ignorarlo)
    "   ",                      # Línea vacía / Solo espacios
]


test_code_pasada2 = [
    "DATA:",
    "    array_ptr 0",        # Dirección DATA: 0
    "    total 0",            # Dirección DATA: 1
    "    limite 10",          # Dirección DATA: 2
    "",
    "CODE:",
    "main:",                  # Código: 0
    "    MOV A, (array_ptr)", # Código: 0 -> Debe normalizarse a: MOV A,(DIR)
    "    MOV B, A",           # Código: 1 -> Debe normalizarse a: MOV B,A
    "    MOV A, 0",           # Código: 2 -> Debe normalizarse a: MOV A,LIT
    "    MOV (total), A",     # Código: 3 -> Debe normalizarse a: MOV (DIR),A
    "",
    "loop:",                  # Código: 4
    "    ADD A, (B)",         # Código: 4 -> Debe normalizarse a: ADD A,(B)
    "    INC B",              # Código: 5 -> Debe normalizarse a: INC B
    "    PUSH A",             # Código: 6 -> Debe normalizarse a: PUSH A
    "    MOV A, B",           # Código: 7 -> Debe normalizarse a: MOV A,B
    "    CMP A, (limite)",    # Código: 8 -> Debe normalizarse a: CMP A,(DIR)
    "    POP A",              # Código: 9 -> ¡Ojo! Ocupa 2 espacios (9 y 10). Próximo PC = 11.
    "    JNE loop",           # Código: 11 -> Debe normalizarse a: JNE DIR
    "",
    "end:",                   # Código: 12
    "    MOV (total), A",     # Código: 12 -> Debe normalizarse a: MOV (DIR),A
    "    RET",                # Código: 13 -> ¡Ojo! Ocupa 2 espacios (13 y 14)
]


labels = dir_register(test_code_pasada2)
print(labels)


columnas = []
for code_line in test_code_pasada2:
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
        columnas.append([code_line.strip(), formateada, opcode])

    #print(f"Original: {code_line}\nIdentificado: {identify_procedure(code_line, "ASSEMBLY")}\n")
headers = ["Original", "Formateada", "Opcode"]
print(tabulate(columnas, headers))


