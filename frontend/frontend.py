from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox
from PySide6.QtGui import QFont
from frontend.fonts.ascii_art import title_art2 as title_art
def create_window(ISAs):
    w = QtWidgets.QWidget()
    window_w = 1800
    window_h = 1000
    w.resize(window_w, window_h)
    w.setWindowTitle("PySide6 Application")


    # Widgets
    title = QtWidgets.QLabel(title_art, alignment=QtCore.Qt.AlignCenter)
    title.setObjectName("title")

    button_assemble = QtWidgets.QPushButton("Assemble")
    button_assemble.setObjectName("btnAssemble")

    button_program = QtWidgets.QPushButton("Program")
    button_file = QtWidgets.QPushButton("Import File")
    button_file.setObjectName("btnImportFile")

    selector_ISA = QComboBox()
    fuente_selector = selector_ISA.font()
    fuente_selector.setFamily('Ac437 PhoenixEGA 8x14')
    fuente_selector.setPointSize(12)
    selector_ISA.setFont(fuente_selector)
    for isa in ISAs:

        selector_ISA.addItem(f"    {isa}")

    # Tabs
    tab_manager = QtWidgets.QTabWidget()
    tab_manager.setObjectName("pestañas_assemblers")

    # Input Console
    input_console = QtWidgets.QPlainTextEdit()
    main_console_font = input_console.font()
    main_console_font.setLetterSpacing(QFont.AbsoluteSpacing, 2)
    input_console.setFont(main_console_font)

    # Opcodes
    opcodes_console = QtWidgets.QPlainTextEdit(readOnly=True)
    opcodes_console.setFont(main_console_font)

    # Craftssembly
    craftssembly_console = QtWidgets.QPlainTextEdit()
    craftssembly_console.setFont(main_console_font)

    # ISA
    isa_console = QtWidgets.QPlainTextEdit()
    #craftssembly_console.setFont(main_console_font)


    # LOG Console
    log_console = QtWidgets.QPlainTextEdit(readOnly=True)
    log_console.setObjectName("consolaLog")
    log_console_font = log_console.font()
    log_console_font.setLetterSpacing(QFont.AbsoluteSpacing, 2) 
    log_console.setFont(log_console_font)
    
    tab_manager.addTab(input_console, "Assembler")
    tab_manager.addTab(opcodes_console, "Opcodes")
    tab_manager.addTab(craftssembly_console, "Craftsembler")
    tab_manager.addTab(isa_console, "ISA")

    # --- ARREGLAR BOTONES DE SCROLL DE LAS PESTAÑAS ---
    botones_scroll = tab_manager.findChildren(QtWidgets.QToolButton)
    for i, boton in enumerate(botones_scroll):
        fuente_boton = boton.font()
        fuente_boton.setFamily('Ac437 PhoenixEGA 8x14')
        fuente_boton.setPointSize(12)
        boton.setFont(fuente_boton)
        if i == 0:
            boton.setText("<")
        elif i == 1:
            boton.setText(">")
        boton.setArrowType(QtCore.Qt.NoArrow)
    



    # Add widgets to the layout
    main_layout = QVBoxLayout(w)
    separation = (1800-1750)/2*1.25


    upper_buttons_layout = QHBoxLayout()
    upper_buttons_layout.addWidget(button_file)
    upper_buttons_layout.addWidget(button_program)
    upper_selectors_layout = QVBoxLayout()
    upper_selectors_layout.addLayout(upper_buttons_layout)
    upper_selectors_layout.addWidget(selector_ISA)
    upper_layout = QHBoxLayout()
    upper_layout.setContentsMargins(separation,0 , separation, 0)
    upper_layout.addWidget(title)
    upper_layout.addLayout(upper_selectors_layout)


    middle_layout = QHBoxLayout()
    middle_layout.setContentsMargins(separation, separation/2, separation, separation/2)
    middle_layout.addWidget(tab_manager, 1) 


    bottom_layout = QHBoxLayout()
    bottom_layout.setContentsMargins(separation, separation/2, separation, separation)

    log_console.setFixedWidth(1000)
    bottom_layout.addWidget(log_console)
    bottom_layout.addStretch()

    bottom_layout.addWidget(button_assemble)

    main_layout.addLayout(upper_layout)
    main_layout.addLayout(middle_layout)
    main_layout.addLayout(bottom_layout)
    
    # Show the window
    w.show()
    
    return w, button_file, button_assemble, input_console, opcodes_console, log_console