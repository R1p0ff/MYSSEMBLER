from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QPlainTextEdit
from PySide6.QtGui import QFont, QKeyEvent, QTextCursor, QSyntaxHighlighter, QTextCharFormat, QColor
from PySide6.QtCore import QRegularExpression

from frontend.fonts.ascii_art import title_art2 as title_art
from tabulate import tabulate

class AutoIndentEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (16777220, 16777221):
            cursor = self.textCursor()
            line = cursor.block().text()
            
            identation = ""
            for char in line:
                if char in (' ', '\t'):
                    identation = f"{identation}{char}"
                else:
                    break
            
            super().keyPressEvent(event)
            self.insertPlainText(identation)
        else:
            super().keyPressEvent(event)

class AssemblerHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, default_opcodes = False):
        super().__init__(parent)
        self.rules = []

        self.opcodes_format = QTextCharFormat()
        self.opcodes_format.setForeground(QColor("#2cde85"))
        self.opcodes_format.setFontWeight(QFont.Bold)

        self.comments_format = QTextCharFormat()
        self.comments_format.setForeground(QColor("#26a164"))
        self.comments_format.setFontItalic(True)


        if default_opcodes:
            self.update_opcodes(default_opcodes)

    def update_opcodes(self, operations):
        self.rules = []
        for operation in operations:
            operation_regex = QRegularExpression(f"\\b{operation}\\b")
            self.rules.append((operation_regex, self.opcodes_format))
        comment_regex = QRegularExpression(";.*")
        self.rules.append((comment_regex, self.comments_format))
        self.rehighlight()
    
    def highlightBlock(self, text):
        for pattern, text_format in self.rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), text_format)


def post_results(result, text_box, delete):
    if delete:
        text_box.clear()
    
    text_box.appendPlainText(result)

    cursor = text_box.textCursor()
    cursor.movePosition(QTextCursor.Start)
    text_box.setTextCursor(cursor)

def post(data, text_box):
    text_box.clear()
    text_box.appendPlainText(data)

    cursor = text_box.textCursor()
    cursor.movePosition(QTextCursor.Start)
    text_box.setTextCursor(cursor)



def post_isa(ISA, text_box, ISA_selector):
    text_box.clear()
    actual_selected_isa = ISA_selector.currentText().strip()
    opcodes = ISA[actual_selected_isa]
    isa_rows = []
    i = 0
    for isa in opcodes:
        isa_rows.append([i, isa, opcodes[isa]])
        i+=1
    headers = ["#", "Operation", "OPCODE"]
    tabla_isa = tabulate(isa_rows, headers)
    text_box.appendPlainText(tabla_isa)
    cursor = text_box.textCursor()
    cursor.movePosition(QTextCursor.Start)
    text_box.setTextCursor(cursor)

# Colour method with html extracted FROM
# Source - https://stackoverflow.com/a/49666693
# Posted by JustWe
# Retrieved 2026-05-19, License - CC BY-SA 3.0
def post_log(msg, log_console, color ="#ffffff", _counter=[1]):
    log_row = _counter[0]

    msg = f'<span style="color: {color};">&lt;{log_row}&gt;:{msg}</span>'
    log_console.appendHtml(msg)
    _counter[0]+=1
    cursor = log_console.textCursor()
    cursor.movePosition(QTextCursor.End)
    log_console.setTextCursor(cursor)


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

    ISA_selector = QComboBox()
    fuente_selector = ISA_selector.font()
    fuente_selector.setFamily('Ac437 PhoenixEGA 8x14')
    fuente_selector.setPointSize(12)
    ISA_selector.setFont(fuente_selector)
    for isa in ISAs:
        ISA_selector.addItem(f"    {isa}")

    # Tabs
    tab_manager = QtWidgets.QTabWidget()
    tab_manager.setObjectName("Assemblers_Tabs")

    # Input Console
    default_ISA = ISAs[ISA_selector.currentText().strip()]
    default_opcodes = []
    for operation in default_ISA:
        default_opcodes.append(operation.split(" ")[0])

    input_console = AutoIndentEdit()
    main_console_font = input_console.font()
    main_console_font.setLetterSpacing(QFont.AbsoluteSpacing, 2)
    input_console.setFont(main_console_font)
    highlighter = AssemblerHighlighter(input_console.document(), default_opcodes)
    input_console.highlighter = highlighter

    # Opcodes
    opcodes_console = QtWidgets.QPlainTextEdit(readOnly=True)
    opcodes_console.setFont(main_console_font)

    # Craftssembly
    craftssembly_console = QtWidgets.QPlainTextEdit()
    craftssembly_console.setFont(main_console_font)

    # ISA
    isa_console = QtWidgets.QPlainTextEdit(readOnly=True)


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





    # Add widgets to the layout
    main_layout = QVBoxLayout(w)
    separation = (1800-1750)/2*1.25

    upper_buttons_layout = QHBoxLayout()
    upper_buttons_layout.addWidget(button_file)
    upper_buttons_layout.addWidget(button_program)
    upper_selectors_layout = QVBoxLayout()
    upper_selectors_layout.addLayout(upper_buttons_layout)
    upper_selectors_layout.addWidget(ISA_selector)
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
    
    return w, button_file, button_assemble, input_console, opcodes_console, log_console, isa_console, ISA_selector