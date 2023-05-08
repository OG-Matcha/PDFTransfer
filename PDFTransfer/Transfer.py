import PyPDF2
import os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QIcon


def resource_path(relative_path):
    # get absolute path to resources
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class TransferToTextThread(QThread):
    # Declare a signal to emit the progress bar and warning
    progress_bar_start_signal = pyqtSignal()
    progress_bar_stop_signal = pyqtSignal()
    warning_signal = QtCore.pyqtSignal(str, str)

    def __init__(self) -> None:
        super().__init__()
        self.pdf_file = ""
        self.text_path = ""
        self.pdf_file_name = ""

    def write_to_file(self) -> None:
        extracted_text = self.extract_text_from_pdf()

        with open(f"{resource_path(self.text_path)}/{self.pdf_file_name}.txt", "w", encoding="UTF-8") as file:
            for text in extracted_text:
                file.write(f"{text}\n")

    def extract_text_from_pdf(self) -> list[str]:
        with open(resource_path(self.pdf_file), 'rb') as pdf:
            reader = PyPDF2.PdfReader(pdf, strict=False)
            pdf_text = []

            for page in reader.pages:
                content = page.extract_text()
                pdf_text.append(content)

            return pdf_text

    def run(self) -> None:
        try:
            self.progress_bar_start_signal.emit()

            # Extracted and write down the text
            self.write_to_file()

            # Emit the message
            self.warning_signal.emit(
                "Transfer finished", "The PDF have been transfered to text file"
            )
            self.progress_bar_stop_signal.emit()

        # Handle invalid prompt error
        except PyPDF2.errors.PyPdfError:
            self.warning_signal.emit(
                "Process Failed", "The file seems to be not acceptable"
            )
            self.progress_bar_stop_signal.emit()
        except UnicodeEncodeError:
            self.warning_signal.emit(
                "Process Failed", "The file may has unacceptable characters"
            )
            self.progress_bar_stop_signal.emit()


class PDFTransfer(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PDFTransfer")
        self.setMinimumSize(600, 400)

        # Create a QIcon object from the icon file
        icon_path = "assets\\Icon.ico"
        icon = QIcon(resource_path(icon_path))
        self.setWindowIcon(icon)

        # Create the central widget and layout
        self.central_widget = QtWidgets.QWidget(self)
        self.central_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        # Create the vertical layout for the file path
        self.button_layout = QtWidgets.QVBoxLayout()

        # Create the pdf file button
        self.pdf_file_button = QtWidgets.QPushButton(
            self.central_widget, text="Select PDF File", clicked=self.select_pdf_file
        )
        self.button_layout.addWidget(self.pdf_file_button)

        # Create the text file path button
        self.text_path_button = QtWidgets.QPushButton(
            self.central_widget, text="Select Text Path", clicked=self.select_text_path
        )
        self.button_layout.addWidget(self.text_path_button)

        # Create the Transfer button
        self.transfer_button = QtWidgets.QPushButton(
            self.central_widget, text="Transfer", clicked=self.transfer_text
        )
        self.button_layout.addWidget(self.transfer_button)

        # Add the vertical layout to the central layout
        self.central_layout.addLayout(self.button_layout)

        # Create the progress bar
        self.progress_bar = QtWidgets.QProgressBar(self.central_widget)
        self.progress_bar.setVisible(False)
        self.style = '''
            QProgressBar {
                border: 2px solid #000;
                border-radius: 5px;
                text-align:center;
                height: 20px;
            }
            QProgressBar::chunk {
                background: #C7F08D;
                width:1px;
            }
        '''
        self.progress_bar.setStyleSheet(self.style)
        self.central_layout.addWidget(self.progress_bar)

        # Initialize the file path
        self.pdf_file = ""
        self.text_path = ""

        # Create the thread
        self.transfer_to_text_thread = TransferToTextThread()

        # Connect the signal to a slot
        self.transfer_to_text_thread.warning_signal.connect(self.warning)
        self.transfer_to_text_thread.progress_bar_start_signal.connect(
            self.show_progress_bar)
        self.transfer_to_text_thread.progress_bar_stop_signal.connect(
            self.hide_progress_bar)

    def transfer_text(self):
        if not self.pdf_file:
            QtWidgets.QMessageBox.warning(
                self, "Missing Entry", "Please select a pdf file")
            return
        if not self.text_path:
            QtWidgets.QMessageBox.warning(
                self, "Missing Entry", "Please select a folder to create text file")
            return

        self.transfer_to_text_thread.pdf_file = self.pdf_file
        self.transfer_to_text_thread.text_path = self.text_path
        self.transfer_to_text_thread.pdf_file_name = self.pdf_file_name

        self.transfer_to_text_thread.start()

    def select_pdf_file(self):
        self.pdf_file, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select pdf file", "C:/", "PDF (*.pdf)")
        self.pdf_file_name = QUrl.fromLocalFile(self.pdf_file).fileName()

    def select_text_path(self):
        self.text_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select text path", "C:/")

    def warning(self, title, message):
        QtWidgets.QMessageBox.warning(self, title, message)

    def show_progress_bar(self):
        # Show the progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setValue(30)

    def hide_progress_bar(self):
        # Hide the progress bar
        self.progress_bar.setVisible(False)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = PDFTransfer()
    window.show()
    app.exec_()
