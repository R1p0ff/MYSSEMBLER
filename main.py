import sys
import os
from PySide6 import QtWidgets
from PySide6.QtGui import QFontDatabase
from frontend.frontend import create_window, post_results
#from backend.assembly import opcode_translation
from backend.mapas_opcodes.opcodes_assembly import ISAs
from backend.assembly import instruction
from backend.test_assembly import the_test

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    # Rutas
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_css = os.path.join(carpeta_actual, "frontend", "index.css")
    ruta_fuente = os.path.join(carpeta_actual, "frontend", "fonts", "Ac437_PhoenixEGA_8x14.ttf")

    # Fuente
    if os.path.exists(ruta_fuente):
        id_fuente = QFontDatabase.addApplicationFont(ruta_fuente)
        familias = QFontDatabase.applicationFontFamilies(id_fuente)
    else:
        print(f"Advertencia: No se encontró el archivo de fuente en: {ruta_fuente}")
    
    # Stylesheet
    try:
        with open(ruta_css, "r", encoding="utf-8") as archivo_css:
            app.setStyleSheet(archivo_css.read())
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el archivo index.css en {ruta_css}")
    
    # Loop
    w, button_file, button_assemble, input_console, opcodes_console, log_console = create_window(ISAs)
    # Para iterar o revisar línea por línea de forma independiente
    def process_text():
        lineas = input_console.toPlainText().splitlines()
        input_console_lines = []
        for linea in lineas:
            input_console_lines.append(linea)
        return input_console_lines
    #button_assemble.clicked.connect(lambda: post_results(instruction(process_text()), opcodes_console))
    
    button_assemble.clicked.connect(lambda: post_results(instruction(the_test), opcodes_console))

    #button_assemble.clicked.connect(lambda: instruction(input_console.toPlainText()))

    sys.exit(app.exec())