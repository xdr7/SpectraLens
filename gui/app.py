"""
Application Launcher
=====================
Entry point for launching the SpectraLens GUI application.

Creator : Asmaul Asni Subegi, S.Kom
Email   : sabayonx@gmail.com
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from gui.main_window import SpectraLensGUI




def run_app():
    """Launch the SpectraLens GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("SpectraLens")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SpectraLens")

    window = SpectraLensGUI()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    run_app()
