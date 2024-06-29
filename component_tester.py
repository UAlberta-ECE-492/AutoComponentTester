from enum import Enum
       
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QStackedWidget, QLabel, QWidget, \
    QTextEdit, QCheckBox
from PyQt5.QtCore import pyqtSlot, QThread, QRunnable, QThreadPool, QMetaObject, Qt, Q_ARG
from PyQt5.QtGui import QPixmap
        
class TestOutput:
    """
    The text output of the test. 
    Call these methods as your tests run to display test status to the user.
    """
    
    def __init__(self, vbox: QVBoxLayout):
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.debug_output = QTextEdit()
        self.debug_output.setReadOnly(True)
        self.output_stack = QStackedWidget()
        self.output_stack.addWidget(self.debug_output)
        self.output_stack.addWidget(self.output)
        self.output_stack.setCurrentWidget(self.output)
        vbox.addWidget(self.output_stack)
        
    def show_debug_output(self, debug: bool):
        if debug:
            self.output_stack.setCurrentWidget(self.debug_output)
        else:
            self.output_stack.setCurrentWidget(self.output)
        
    def print(self, message: str, colour = None, debug = False):
        prefix = ""
        postfix = ""
        if colour is not None:
            prefix = f"<font color=\"{colour}\">"
            postfix = "</font>"
        styled_message = prefix + message + postfix
        
        if not debug:
            QMetaObject.invokeMethod(self.output,
                    "append", Qt.QueuedConnection, 
                    Q_ARG(str, styled_message))
        QMetaObject.invokeMethod(self.debug_output,
                "append", Qt.QueuedConnection, 
                Q_ARG(str, styled_message))
        
class SetupStep:
    """
    Override if you need more complicated setup steps
    """
    def __init__(self, message: str, picture = None, align="centre"):
        self.message = message
        self.picture = picture
        self.align = align

    def add_content(self, vbox: QVBoxLayout):
        """Override this to add custom content"""
        
        if self.picture is not None:
            p = QPixmap(self.picture)
            aspect = p.width() / p.height()
            if aspect > 1.0:
                p = p.scaledToWidth(500)
            else:
                p = p.scaledToHeight(500)
            plabel = QLabel()
            plabel.setPixmap(p)
            if self.align == "centre":
                plabel.setAlignment(Qt.AlignCenter)
            vbox.addWidget(plabel)
            
        label = QLabel(self.message)
        label.setWordWrap(True)
        if self.align == "centre":
            label.setAlignment(Qt.AlignCenter)
        label.setOpenExternalLinks(True)
        vbox.addWidget(label)    


class ComponentTester:
    """
    Base class for all components that need testing.
    To implement a new component to test, override this class,
    and add it to the list of testable components.
    """
    
    def name(self) -> str:
        pass
        
    # If the test can be safely cancelled while testing
    def cancellable(self) -> bool:
        return True

    # If the component has tests, or is only a tutorial for another device (DMM)
    def has_tests(self) -> bool:
        return True
        
    def run_tests(self, output: TestOutput):
        pass
    
    def required_setup_step(self) -> int:
        return None
    
    def setup_steps(self) -> list[SetupStep]:
        pass
    
    @pyqtSlot(int, name="run_test_landing")
    def run_test_landing(self, window: QStackedWidget):
        landing_page = QWidget()
        vbox = QVBoxLayout(landing_page)
        vbox.addWidget(QLabel(f"<b>Start {self.name()} tutorial?</b>"))
        
        buttons = QHBoxLayout(landing_page)
        back_button = QPushButton("Cancel")
        back_button.clicked.connect(lambda e: window.setCurrentIndex(0))
        buttons.addWidget(back_button)
        
        required_step = self.required_setup_step()
        
        if len(self.setup_steps()) != 0:
            setup_button = QPushButton("Start Tutorial")
            setup_button.clicked.connect(lambda e, x=self: x.run_setup_step(window, 1))
            buttons.addWidget(setup_button)

        if self.has_tests():
            test_button = QPushButton("Skip")
            if required_step is None:
                test_button.clicked.connect(lambda e: self.run_test_window(window))
            else:
                test_button.clicked.connect(lambda e: self.run_setup_step(window, required_step))
            buttons.addWidget(test_button)
        
        vbox.addLayout(buttons)
        window.setCurrentIndex(window.addWidget(landing_page))
        
    @pyqtSlot(int, name="run_setup_step")
    def run_setup_step(self, window: QStackedWidget, step_number: int):
        steps = self.setup_steps()
        step = steps[step_number-1]
        
        page = QWidget()
        vbox = QVBoxLayout(page)
        
        step.add_content(vbox)
               
        buttons = QHBoxLayout(page)
        back_message = "Cancel" if step_number == 1 else "Back"
        back_button = QPushButton(back_message)
        back_button.clicked.connect(lambda e: window.removeWidget(page))
        buttons.addWidget(back_button)
        
        if step_number == len(steps):
            if self.has_tests():
                next_button = QPushButton("Start")
                next_button.clicked.connect(lambda e: self.run_test_window(window))
            else:
                next_button = QPushButton("Finish")
                next_button.clicked.connect(lambda e: window.setCurrentIndex(0))
            buttons.addWidget(next_button)
        else:
            next_button = QPushButton("Next")
            next_button.clicked.connect(lambda e: self.run_setup_step(window, step_number+1))
            buttons.addWidget(next_button)

        vbox.addLayout(buttons)
        
        window.setCurrentIndex(window.addWidget(page))

    @pyqtSlot(int, name="run_test")
    def run_test_window(self, window: QStackedWidget):
        test_page = QWidget()
        vbox = QVBoxLayout(test_page)
        
        vbox.addWidget(QLabel(f"<b>Testing {self.name()}</b>"))
        checkbox = QCheckBox("Debug output")
        vbox.addWidget(checkbox)

        test_output = TestOutput(vbox)
        
        checkbox.stateChanged.connect(lambda x: test_output.show_debug_output(x != 0))
        
        buttons = QHBoxLayout(test_page)
        if self.cancellable():
            back_button = QPushButton("Cancel")
            back_button.clicked.connect(lambda e: window.removeWidget(test_page))
            buttons.addWidget(back_button)
        
        finish_button = QPushButton("Finish")
        finish_button.setEnabled(False)
        finish_button.clicked.connect(lambda e: window.setCurrentIndex(0))
        buttons.addWidget(finish_button)
        
        rerun_button = QPushButton("Rerun")
        rerun_button.setEnabled(False)
        rerun_button.clicked.connect(lambda e: (
            window.removeWidget(test_page),
            self.run_test_window(window)
        ))
        buttons.addWidget(rerun_button)
               
        vbox.addLayout(buttons)
        window.setCurrentIndex(window.addWidget(test_page))
        
        test_runner = TestRunner(self, test_output, [finish_button, rerun_button])
        QThreadPool.globalInstance().start(test_runner)


class TestRunner(QRunnable):
    def __init__(
        self,
        component: ComponentTester,
        test_output: TestOutput,
        buttons: list[QPushButton]
    ):
        super().__init__()
        self.component = component
        self.test_output = test_output
        self.buttons = buttons
    
    def run(self):
        self.component.run_tests(self.test_output)
        for b in self.buttons:
            QMetaObject.invokeMethod(b,
                    "setEnabled", Qt.QueuedConnection, 
                    Q_ARG(bool, True))
