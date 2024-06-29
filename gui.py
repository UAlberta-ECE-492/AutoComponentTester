from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QStackedWidget, QLabel, QWidget, \
    QHBoxLayout, QLineEdit

from components import DMM, AD2Calibration, AD3Calibration, CurrentSource

TESTS = [CurrentSource, DMM, AD2Calibration, AD3Calibration]

def run_gui():
    app = QApplication([])
    window = QStackedWidget()
    window.setWindowTitle("Component Tester")
    window.setMinimumSize(500, 0)
    
    main_page = QWidget()
    vbox = QVBoxLayout(main_page)
    vbox.addWidget(QLabel("<b>Select component to test</b>"))
    
    for test_type in TESTS:
        test = test_type()
        button = QPushButton(test.name())
        button.clicked.connect(lambda state, x=test: x.run_test_landing(window))
        vbox.addWidget(button)

    window.addWidget(main_page)
    window.show()
    app.exec()

if __name__ == "__main__":
    run_gui()
