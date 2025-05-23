import sys
import unittest
from PyQt5.QtWidgets import QApplication
# Adjust the import path based on your project structure if pdf_viewer is a module
# For example, if tests is at the same level as pdf_viewer directory:
# from ..pdf_viewer.main import PDFViewer
# Or ensure pdf_viewer is in PYTHONPATH
# For simplicity, assuming direct execution for now or proper path setup
sys.path.append('.') # Add root to path to find pdf_viewer module
from pdf_viewer.main import PDFViewer, DEFAULT_ZOOM_LEVEL

# It's crucial to have one QApplication instance for all tests
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

class TestPDFViewer(unittest.TestCase):
    def setUp(self):
        '''Create the GUI'''
        self.viewer = PDFViewer()

    def test_app_creation(self):
        self.assertIsNotNone(self.viewer)
        self.assertEqual(self.viewer.windowTitle(), "Python PDF Viewer")

    def test_initial_state_no_pdf(self):
        self.assertIsNone(self.viewer.doc)
        self.assertEqual(self.viewer.zoom_level, DEFAULT_ZOOM_LEVEL)
        self.assertEqual(self.viewer.rotation_angle, 0)
        
        # Check button states (after ensuring update methods have been called by __init__)
        # These buttons should be disabled initially as no PDF is loaded
        self.assertFalse(self.viewer.next_button.isEnabled())
        self.assertFalse(self.viewer.prev_button.isEnabled())
        self.assertFalse(self.viewer.page_input.isEnabled())
        self.assertFalse(self.viewer.zoom_in_button.isEnabled())
        self.assertFalse(self.viewer.zoom_out_button.isEnabled())
        self.assertFalse(self.viewer.rotate_cw_button.isEnabled())
        self.assertFalse(self.viewer.rotate_ccw_button.isEnabled())
        self.assertFalse(self.viewer.save_image_button.isEnabled())

    # Add more tests if simple logical units can be tested without complex UI interaction

if __name__ == '__main__':
    unittest.main()
