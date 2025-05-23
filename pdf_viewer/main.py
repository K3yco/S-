import sys
import fitz  # PyMuPDF
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt

class PDFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python PDF Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.pdf_label = QLabel("Open a PDF file to view its content.")
        self.pdf_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.pdf_label)

        self.open_button = QPushButton("Open PDF")
        self.open_button.clicked.connect(self.open_pdf)
        self.layout.addWidget(self.open_button)

        self.doc = None
        self.current_page = 0

    def open_pdf(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf);;All Files (*)", options=options)
        if file_name:
            try:
                self.doc = fitz.open(file_name)
                self.current_page = 0
                self.display_page()
            except Exception as e:
                self.pdf_label.setText(f"Error opening PDF: {e}")
                self.doc = None

    def display_page(self):
        if self.doc and 0 <= self.current_page < self.doc.page_count:
            page = self.doc.load_page(self.current_page)
            pix = page.get_pixmap()
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(img)
            self.pdf_label.setPixmap(pixmap)
            self.setWindowTitle(f"Python PDF Viewer - Page {self.current_page + 1}/{self.doc.page_count}")
        elif self.doc:
            self.pdf_label.setText("Invalid page number.")
        else:
            self.pdf_label.setText("No PDF loaded.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    viewer.show()
    sys.exit(app.exec_())
