import sys
import os
from PySide6 import QtWidgets
from PySide6.QtGui import QFontDatabase
from frontend.frontend import create_window, post_results, post_isa, post_log
from backend.opcodes_maps.opcodes import ISAs
from backend.opcodes_maps.default import default_code
from backend.assembly import instruction
from backend.programmer import programmer

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    # Route to css and font
    actual_route = os.path.dirname(os.path.abspath(__file__))
    css_route = os.path.join(actual_route, "frontend", "index.css")
    font_route = os.path.join(actual_route, "frontend", "fonts", "Ac437_PhoenixEGA_8x14.ttf")

    # Font load
    if os.path.exists(font_route):
        font_id = QFontDatabase.addApplicationFont(font_route)
        font_family = QFontDatabase.applicationFontFamilies(font_id)
    else:
        print(f"ERR: font {font_route}")
    
    # Stylesheet
    try:
        with open(css_route, "r", encoding="utf-8") as css_file:
            app.setStyleSheet(css_file.read())
    except FileNotFoundError:
        print(f"ERR: index.css | {css_route}")

    # Graphic UI Loop
    w, button_file, button_program, button_assemble, input_console, opcodes_console, log_console, isa_console, ISA_selector, PORT_selector = create_window(ISAs)

    # Extract n Repair input_console text into a list
    def process_text(text):
        input_console_lines = []
        for row in text:
            input_console_lines.append(row.strip())
        return input_console_lines

    post_results(default_code, input_console, True)
    post_isa(ISAs, isa_console, ISA_selector)
    
    
    log_interface = lambda msg, color="#ffffff": post_log(msg, log_console, color)
    
    last_assembly_hex = []
    def assembly_function():
        global last_assembly_hex
        assembly_table, last_assembly_hex = instruction(process_text(input_console.toPlainText().splitlines()), ISA_selector.currentText().strip(), log_interface)
        post_results(assembly_table, opcodes_console, delete=True)
        return last_assembly_hex
    
    
    button_assemble.clicked.connect(assembly_function)
    button_program.clicked.connect(lambda: programmer(port = f"{PORT_selector.currentText().strip()}", hex_bytes = last_assembly_hex, log_interface = log_interface))

    def update_selected_isa(selected_isa):
        new_opcodes = ISAs[selected_isa.strip()]
        opcodes = []
        for operation in new_opcodes:
            opcodes.append(operation.split(" ")[0])
        opcodes = set(opcodes)
        input_console.highlighter.update_opcodes(opcodes)
        post_isa(ISAs, isa_console, ISA_selector)    
        
    ISA_selector.currentTextChanged.connect(update_selected_isa)

    sys.exit(app.exec())