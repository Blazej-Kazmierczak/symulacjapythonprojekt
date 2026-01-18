import sys
from PyQt5.QtWidgets import QApplication
from ui.scada_app import SCADAWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = SCADAWindow()
    w.show()
    sys.exit(app.exec_())
