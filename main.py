import sys
import os
from PySide6 import QtWidgets
from PySide6.QtGui import QFontDatabase
from frontend.frontend import create_window
#from backend.assembly import opcode_translation
from data.isa import isa_main_computer, ISAs


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
    button_assemble.clicked.connect(lambda: opcode_translation(isa_main_computer))

    sys.exit(app.exec())