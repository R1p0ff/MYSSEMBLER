default_code = """DATA:
    res 0    ; Resultado MCD
    temp 0   ; Variable auxiliar para swap
    a 105
    b 30
CODE:
start:
    MOV A,(a)
    MOV B,(b)
loop:
    CMP A,B
    JLT swap
    SUB A,B
    ; Verificamos si A es 0 (usando comparacion contra literal 0)
    MOV B,0 
    CMP A,B
    JEQ done
    MOV B,(b) ; Recargamos B original tras la comprobacion
    JMP loop
swap:
    MOV (temp),A
    MOV A,(b)
    MOV B,(temp)
    JMP loop
done:
    MOV A, B
    MOV (res), A
halt:
    JMP halt"""