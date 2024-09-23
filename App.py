import re
import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QFileDialog, QMessageBox, QHBoxLayout
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        # Define formats for syntax highlighting
        self.variable_format = QTextCharFormat()
        self.variable_format.setForeground(QColor(144, 238, 144))  # Light green for variables

        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor(135, 206, 250))  # Light blue for numbers

        self.operator_format = QTextCharFormat()
        self.operator_format.setForeground(QColor(255, 99, 71))  # Tomato for operators

        self.function_format = QTextCharFormat()
        self.function_format.setForeground(QColor(255, 215, 0))  # Gold for functions

        self.highlighting_rules = [
            (r'\b[A-Za-z_][A-Za-z0-9_]*\b', self.variable_format),  # Variables
            (r'\b\d+(\.\d+)?\b', self.number_format),                # Numbers
            (r'[\+\-\*/=]', self.operator_format),                    # Operators
            (r'\b(sin|cos|tan|log|ln|exp|sqrt)\b', self.function_format)  # Functions
        ]

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            for match in re.finditer(pattern, text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)

class MathScriptEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MathScript Editor")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("icon.ico"))
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Dark mode styles
        self.setStyleSheet("""
            QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #4C4C4C;
                color: #FFFFFF;
                border: 1px solid #6C6C6C;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #6C6C6C;
            }
            QTextEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #6C6C6C;
            }
        """)

        self.editor = QTextEdit(self)
        self.editor.setFont(QFont("Arial", 14))  # Set the font size to 14
        self.layout.addWidget(self.editor)

        # Initialize the syntax highlighter
        self.highlighter = SyntaxHighlighter(self.editor.document())

        button_layout = QHBoxLayout()

        self.run_button = QPushButton("Run", self)
        self.run_button.clicked.connect(self.run_script)
        button_layout.addWidget(self.run_button)

        self.graph_button = QPushButton("Graph", self)
        self.graph_button.clicked.connect(self.plot_graph)
        button_layout.addWidget(self.graph_button)

        self.open_button = QPushButton("Open", self)
        self.open_button.clicked.connect(self.open_file)
        button_layout.addWidget(self.open_button)

        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_file)
        button_layout.addWidget(self.save_button)

        self.layout.addLayout(button_layout)

        # Store variables
        self.variables = {}

    def run_script(self):
        script_content = self.editor.toPlainText()
        try:
            self.evaluate(script_content)
            QMessageBox.information(self, "Info", "Script executed successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def evaluate(self, script):
        for line in script.splitlines():
            if '=' in line:
                var_name, expression = line.split('=')
                var_name = var_name.strip()
                expression = expression.strip()
                # Evaluate the expression and store the result
                self.variables[var_name] = eval(expression, {"__builtins__": None}, self.variables)
            else:
                raise ValueError(f"Invalid statement: {line}")

    def plot_graph(self):
        script_content = self.editor.toPlainText()
        try:
            # Extract y = ... statements
            for line in script_content.splitlines():
                if line.startswith("y ="):
                    expression = line.split('=')[1].strip()
                    self.graph_expression(expression)
                    break
            else:
                raise ValueError("No valid graphing expression found.")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def graph_expression(self, expression):
        x = np.linspace(-10, 10, 400)  # Range for x values
        try:
            # Prepare the expression for evaluation
            y = eval(expression.replace('y', 'x'), {"__builtins__": None}, self.variables)
            
            plt.plot(x, y, label=f'y = {expression}')
            plt.title("Graph of the function")
            plt.xlabel("x")
            plt.ylabel("y")
            plt.axhline(0, color='black', lw=0.5, ls='--')
            plt.axvline(0, color='black', lw=0.5, ls='--')
            plt.grid()
            plt.legend()
            plt.show()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Graphing failed: {e}")

    def open_file(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Open MathScript File", "", "MathScript Files (*.ms);;All Files (*)", options=options)
        if filename:
            with open(filename, 'r') as f:
                content = f.read()
                self.editor.setPlainText(content)

    def save_file(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Save MathScript File", "", "MathScript Files (*.ms);;All Files (*)", options=options)
        if filename:
            with open(filename, 'w') as f:
                content = self.editor.toPlainText()
                f.write(content)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = MathScriptEditor()
    editor.show()
    sys.exit(app.exec_())
