default_code = """DATA:
    nulo 238
    i 10
CODE:
paso1:
    MOV A,0
    MOV B,1
    CMP A,B
    JEQ mal
    MOV B,1
    MOV A,0
    CMP A,B
    JEQ mal
    MOV A,1
    CMP A,B
    JEQ paso2
    JMP mal
paso2:
    JMP paso3
    CMP A,B
    JEQ mal
    JMP mal
paso3:
    MOV A,(i)
    CMP A,B
    JEQ mal
    MOV B,(1)
    CMP A,B
    JEQ paso4
    JMP mal
paso4:
    MOV A,1
    MOV B,1
    MOV B,(i)
    CMP A,B
    JEQ mal
    MOV A,(1)
    CMP A,B
    JEQ paso5
    JMP mal
paso5:
    INC (i)
    MOV A,(i)
    MOV B,11
    CMP A,B
    JEQ bien
    JMP mal
bien:
    MOV A,170
    MOV B,17
    JMP null
mal:
    MOV A,255
    MOV B,255
null:
    JMP null
    CMP A,B
    JEQ null"""


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

test_estres_assembler = [
    "DATA:",
    "    sensor_val -500",     # Dirección DATA: 0 (Usa los 16 bits completos para el signo)
    "    umbral 1200",         # Dirección DATA: 1
    "    estado_critico 0",    # Dirección DATA: 2
    "",
    "CODE:",
    "main:",                   # Código: 0
    "    MOV A, (sensor_val)", # Código: 0 -> MOV A,(DIR)  | Inyecta DATA 0
    "    CMP A, (umbral)",     # Código: 1 -> CMP A,(DIR)  | Inyecta DATA 1
    "    JGE activar_alerta",  # Código: 2 -> JGE DIR      | Inyecta la dirección de activar_alerta
    "",
    "caso_normal:",            # Código: 3
    "    MOV A, 0",            # Código: 3 -> MOV A,LIT    | Inyecta LIT 0
    "    MOV (estado_critico), A", # Código: 4 -> MOV (DIR),A | Inyecta DATA 2
    "    JMP fin",             # Código: 5 -> JMP DIR      | Inyecta la dirección de fin
    "",
    "activar_alerta:",         # Código: 6
    "    MOV A, 1",            # Código: 6 -> MOV A,LIT    | Inyecta LIT 1
    "    MOV (estado_critico), A", # Código: 7 -> MOV (DIR),A | Inyecta DATA 2
    "    POP B",               # Código: 8 -> ¡Ojo! POP ocupa 2 direcciones (8 y 9). Próximo PC = 10
    "",
    "fin:",                    # Código: 10
    "    RET",                 # Código: 10 -> ¡Ojo! RET ocupa 2 direcciones (10 y 11)
]

the_test = [
"DATA:",
"nulo 238",
"i 10",
"",
"CODE:",
"paso1:",
"MOV A,0",
"MOV B,1",
"CMP A,B",
"JEQ mal",
"MOV B,1",
"MOV A,0",
"CMP A,B",
"JEQ mal",
"MOV A,1",
"CMP A,B",
"JEQ paso2",
"JMP mal",
"paso2:",
"JMP paso3",
"CMP A,B",
"JEQ mal",
"JMP mal",
"paso3:",
"MOV A,(i)",
"CMP A,B",
"JEQ mal",
"MOV B,(1)",
"CMP A,B",
"JEQ paso4",
"JMP mal",
"paso4:",
"MOV A,1",
"MOV B,1",
"MOV B,(i)",
"CMP A,B",
"JEQ mal",
"MOV A,(1)",
"CMP A,B",
"JEQ paso5",
"JMP mal",
"paso5:",
"INC (i)",
"MOV A,(i)",
"MOV B,11",
"CMP A,B",
"JEQ bien",
"JMP mal",
"bien:",
"MOV A,170",
"MOV B,17",
"JMP null",
"mal:",
"MOV A,255",
"MOV B,255",
"null:",
"JMP null",
"CMP A,B",
"JEQ null"
]

default_code = """DATA:
    valor1 15
    valor2 8
    resultado 0

CODE:
paso1:
    ; --- Inicializamos el Registro B para direccionamiento indirecto ---
    MOV B,2            ; Apuntamos al casillero de 'resultado' (RAM 2)
    
    ; --- Operaciones aritméticas y lógicas de prueba ---
    MOV A,(valor1)     ; A = 15
    SUB A,(valor2)     ; A = 15 - 8 = 7
    MOV B,5
    CMP A,B            ; Comparamos 7 con 5
    JGT paso2          ; Como 7 > 5, saltamos a paso2
    JMP error_fatal    ; Si no salta, hay un fallo en las flags

paso2:
    ; --- Llamada a subrutina (Guarda PC en la pila) ---
    CALL mi_funcion
    
    ; --- Verificación post-retorno ---
    MOV A,(resultado)  ; Leemos el valor guardado por la subrutina
    MOV B,8
    CMP A,B            ; ¿resultado == 8?
    JEQ exito          ; Si es igual, vamos a la rutina de éxito
    JMP error_fatal

mi_funcion:
    ; --- Bloque de subrutina con direccionamiento indirecto ---
    MOV A,(valor2)     ; A = 8
    MOV B,2            ; B = 2 (Dirección de la variable 'resultado')
    MOV (B),A          ; Guardamos el 8 en la RAM 2 usando (B) indirecto
    INC (resultado)    ; resultado = 8 + 1 = 9
    DEC (2)            ; test operacion invalida
    RET                ; Retornamos (Ocupa 2 espacios en tu ret_pop_checker)

exito:
    MOV A,170          ; Fin exitoso (Hex AA)
    MOV B,170
    JMP bucle_fin

error_fatal:
    MOV A,255          ; Fin con error (Hex FF)
    MOV B,255

bucle_fin:
    JMP bucle_fin      ; Trampa de parada segura para el procesador"""