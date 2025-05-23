import sys
import fitz  # PyMuPDF
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog, QHBoxLayout, QLineEdit
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt

# Constants
DEFAULT_ZOOM_LEVEL = 1.0
ZOOM_INCREMENT = 0.1
MIN_ZOOM_LEVEL = 0.1
MIN_ZOOM_BUTTON_ENABLE_THRESHOLD = 0.11 # To handle floating point inaccuracies for button enabling
ROTATION_ANGLE_INCREMENT = 90
PAGE_INPUT_WIDTH = 50

class PDFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python PDF Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # PDF Display Area
        self.pdf_label = QLabel("Open a PDF file to view its content.")
        self.pdf_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.pdf_label)
        
        # Initialize attributes
        self.doc = None
        self.current_page = 0
        self.zoom_level = DEFAULT_ZOOM_LEVEL
        self.rotation_angle = 0

        # Setup UI components
        self._setup_navigation_controls()
        self._setup_zoom_controls()
        self._setup_rotation_controls()
        self._setup_action_buttons()

        # Update button states
        self.update_all_button_states()

    def _setup_navigation_controls(self):
        # Navigation controls
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous Page")
        self.prev_button.clicked.connect(self.prev_page)
        nav_layout.addWidget(self.prev_button)

        self.page_input = QLineEdit()
        self.page_input.setFixedWidth(PAGE_INPUT_WIDTH)
        self.page_input.returnPressed.connect(self.go_to_page)
        nav_layout.addWidget(self.page_input)

        self.next_button = QPushButton("Next Page")
        self.next_button.clicked.connect(self.next_page)
        nav_layout.addWidget(self.next_button)
        self.layout.addLayout(nav_layout)

    def _setup_zoom_controls(self):
        # Zoom controls
        zoom_layout = QHBoxLayout()
        self.zoom_out_button = QPushButton("Zoom Out")
        self.zoom_out_button.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(self.zoom_out_button)

        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_in_button.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(self.zoom_in_button)
        self.layout.addLayout(zoom_layout)

    def _setup_rotation_controls(self):
        # Rotation controls
        rotation_layout = QHBoxLayout()
        self.rotate_ccw_button = QPushButton("Rotate CCW")
        self.rotate_ccw_button.clicked.connect(self.rotate_ccw)
        rotation_layout.addWidget(self.rotate_ccw_button)

        self.rotate_cw_button = QPushButton("Rotate CW")
        self.rotate_cw_button.clicked.connect(self.rotate_cw)
        rotation_layout.addWidget(self.rotate_cw_button)
        self.layout.addLayout(rotation_layout)

    def _setup_action_buttons(self):
        # Action buttons layout (Open PDF, Save Image)
        action_layout = QHBoxLayout()
        
        self.open_button = QPushButton("Open PDF") # Defined here now
        self.open_button.clicked.connect(self.open_pdf)
        action_layout.addWidget(self.open_button)

        self.save_image_button = QPushButton("Save View as Image")
        self.save_image_button.clicked.connect(self.save_image)
        action_layout.addWidget(self.save_image_button)
        self.layout.addLayout(action_layout)

    def update_all_button_states(self):
        """Updates the enabled state of all control buttons."""
        self.update_navigation_buttons()
        self.update_zoom_buttons()
        self.update_rotation_buttons()
        self.update_save_image_button()

    def open_pdf(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf);;All Files (*)", options=options)
        if file_name:
            try:
                self.doc = fitz.open(file_name)
                self.current_page = 0
                self.zoom_level = DEFAULT_ZOOM_LEVEL
                self.rotation_angle = 0
                self.display_page()
            except Exception as e:
                self.pdf_label.setText(f"Error opening PDF: {e}")
                self.doc = None
            finally:
                self.update_all_button_states()

    def display_page(self):
        if self.doc and 0 <= self.current_page < self.doc.page_count:
            page = self.doc.load_page(self.current_page)
            # Create transformation matrix: apply zoom first, then rotation
            zoom_matrix = fitz.Matrix(self.zoom_level, self.zoom_level)
            rotation_matrix = fitz.Matrix().preRotate(self.rotation_angle)
            combined_matrix = zoom_matrix * rotation_matrix
            pix = page.get_pixmap(matrix=combined_matrix)
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(img)
            self.pdf_label.setPixmap(pixmap)
            self.setWindowTitle(f"Python PDF Viewer - Page {self.current_page + 1}/{self.doc.page_count}")
        elif self.doc:
            self.pdf_label.setText("Invalid page number.")
            self.pdf_label.setPixmap(QPixmap()) # Clear pixmap
        else:
            self.pdf_label.setText("No PDF loaded.")
            self.pdf_label.setPixmap(QPixmap()) # Clear pixmap
        
        # Update button states after attempting to display a page
        self.update_all_button_states()


    def save_image(self):
        if self.doc is None or self.pdf_label.pixmap() is None or self.pdf_label.pixmap().isNull():
            # Optionally show a message to the user that there's nothing to save
            return

        options = QFileDialog.Options()
        file_name, selected_filter = QFileDialog.getSaveFileName(self, 
                                                            "Save Current View as Image", 
                                                            "", 
                                                            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;All Files (*)", 
                                                            options=options)
        if file_name:
            pixmap = self.pdf_label.pixmap()
            if not pixmap.save(file_name):
                # Optionally, show an error message if saving failed
                print(f"Error saving image to {file_name}")
            # else:
                # Optionally, show a success message
                # print(f"Image saved to {file_name}")

    def update_save_image_button(self):
        if self.doc is None or self.pdf_label.pixmap() is None or self.pdf_label.pixmap().isNull():
            self.save_image_button.setEnabled(False)
        else:
            self.save_image_button.setEnabled(True)

    def rotate_cw(self):
        if self.doc:
            self.rotation_angle = (self.rotation_angle + ROTATION_ANGLE_INCREMENT) % 360
            self.display_page()

    def rotate_ccw(self):
        if self.doc:
            self.rotation_angle = (self.rotation_angle - ROTATION_ANGLE_INCREMENT + 360) % 360
            self.display_page()

    def update_rotation_buttons(self):
        if self.doc is None:
            self.rotate_cw_button.setEnabled(False)
            self.rotate_ccw_button.setEnabled(False)
        else:
            self.rotate_cw_button.setEnabled(True)
            self.rotate_ccw_button.setEnabled(True)

    def zoom_in(self):
        if self.doc:
            self.zoom_level += 0.1
            self.display_page()
            # No need to call update_zoom_buttons here, display_page calls update_all_button_states

    def zoom_out(self):
        if self.doc:
            self.zoom_level = max(MIN_ZOOM_LEVEL, self.zoom_level - ZOOM_INCREMENT)
            self.display_page()
            # No need to call update_zoom_buttons here, display_page calls update_all_button_states

    def update_zoom_buttons(self):
        if self.doc is None:
            self.zoom_in_button.setEnabled(False)
            self.zoom_out_button.setEnabled(False)
        else:
            self.zoom_in_button.setEnabled(True)
            # Check against a slightly larger threshold to handle floating point inaccuracies
            self.zoom_out_button.setEnabled(self.zoom_level > MIN_ZOOM_BUTTON_ENABLE_THRESHOLD)


    def next_page(self):
        if self.doc and self.current_page < self.doc.page_count - 1:
            self.current_page += 1
            self.display_page()
            # No need to call update_navigation_buttons here, display_page calls update_all_button_states

    def prev_page(self):
        if self.doc and self.current_page > 0:
            self.current_page -= 1
            self.display_page()
            # No need to call update_navigation_buttons here, display_page calls update_all_button_states

    def go_to_page(self):
        if self.doc:
            try:
                page_num_str = self.page_input.text()
                page_num = int(page_num_str)
                if 1 <= page_num <= self.doc.page_count:
                    self.current_page = page_num - 1
                    self.display_page()
                    # No need to call update_navigation_buttons here, display_page calls update_all_button_states
                else:
                    # Reset to current page if input is invalid
                    self.page_input.setText(str(self.current_page + 1))
            except ValueError:
                # Reset to current page if input is not a number
                self.page_input.setText(str(self.current_page + 1))

    def update_navigation_buttons(self):
        if self.doc is None:
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            self.page_input.setEnabled(False)
            self.page_input.setText("")
        else:
            self.prev_button.setEnabled(self.current_page > 0)
            self.next_button.setEnabled(self.current_page < self.doc.page_count - 1)
            self.page_input.setEnabled(True)
            self.page_input.setText(str(self.current_page + 1))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    viewer.show()
    sys.exit(app.exec_())
