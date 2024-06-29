from component_tester import ComponentTester, SetupStep, TestOutput
from Serial.ActBoards.Boards.ActBoard.ActBoard import ActBoard

from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QStackedWidget, QLabel, QWidget, \
    QHBoxLayout, QLineEdit
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIntValidator

from pywinauto.application import Application, WindowSpecification
from pywinauto import keyboard
from pywinauto.timings import TimeoutError
from pywinauto.findwindows import ElementNotFoundError, WindowNotFoundError
from Waveforms.CaliWizard import CaliWizard
from SerialDevs import UT61E

import os
import traceback
import asyncio
import serial
from time import sleep

class CurrentSource(ComponentTester):
    def has_tests(self):
        return False

    def name(self) -> str:
        return "LM334Z Current Source"

    def setup_steps(self) -> list[SetupStep]:
        return [
            SetupStep("Obtain the testing board.", "Images/ADSetup/step_1.jpg"),
            SetupStep("Power the testing board with a 9V DC barrel jack.", "Images/ADSetup/step_2_board.jpg"),
            SetupStep("Connect the Arduino to the computer. The LEDs will turn cyan.", "Images/CurSourceSetup/lights.jpg"),
            SetupStep("""Place the current source in the \"Cur Source\" sockets with the bump facing the inside of the board. 
- If the current source is placed backwards, the LEDs will turn blue.
- If the current source within an acceptable tolerance the status LED will turn green. 
- If the current source is outside the tolerance, then the status LED will turn red.""", "Images/CurSourceSetup/lights_good.jpg", align="left")
        ]

class DMM(ComponentTester):
    def has_tests(self):
        return False

    def name(self) -> str:
        return "Multimeter"
    
    def setup_steps(self) -> list[SetupStep]:
        return [
            SetupStep("Obtain a DMMCheck Plus testing board. Your board may look slightly different - there are multiple revisions. You can order a DMM Check Plus from <a href=\"dmmcheckplus.com\">their site</a>.", "Images/dmm_checks.png"),
            SetupStep(
"""- Turn on the DMMCheck Plus and your multimeter. There is no external power source, the DMMCheck Plus contains an internal 9V battery.
- The AC/DC switch allows you to switch between AC and DC voltage and current.

- You can now test your multimeter's calibration by checking the voltage, current, and resistances across the various pins:
    - The voltage across the 'V' pins should be 5V in DC mode, and 5V RMS in AC mode.
    - The current across the 'I' pins should be 1mA in DC mode, and 1mA RMS in AC mode.
    - In AC mode, the frequency across the voltage and current pins should be 100Hz.
    - The resistance pins are labelled with their expected resistances. These do not change with the AC/DC switch.
""", align="left"),
            SetupStep("New DMMCheck Plus revisions have more capabilities, such as pins for testing capacitance. See <a href=\"https://dmmcheckplus.com/technical-information\">here</a> for more information.", align="left"),
        ]

class ComSelectionSetup(SetupStep):
    def __init__(self, calibrator):
        self.calibrator = calibrator
    
    def add_content(self, vbox: QVBoxLayout):
        only_int = QIntValidator()
        only_int.setRange(0, 16)
        
        board_com_edit = QLineEdit(AD2Calibration.board_com_num)
        board_com_edit.setValidator(only_int)
        board_com_edit.textChanged.connect(lambda t: AD2Calibration.set_board_com_num(t))
        
        voltmeter_com_edit = QLineEdit(AD2Calibration.voltmeter_com_num)
        voltmeter_com_edit.setValidator(only_int)
        voltmeter_com_edit.textChanged.connect(lambda t: AD2Calibration.set_voltmeter_com_num(t))
        
        vbox.addWidget(QLabel("Board COM number:"))
        vbox.addWidget(board_com_edit)
        vbox.addWidget(QLabel("Multimeter COM number:"))
        vbox.addWidget(voltmeter_com_edit)

        vbox.addWidget(QLabel(
"""
To find the COM numbers:
- open Device Manager
- expand the "Ports (COM & LPT)" item
- the board name will contain "Arduino"
- the Multimeter port is usually COM1. If using a Serial-USB adapter, the COM port will be named by the adapter.
"""
        ))

def wait_for_waveforms_close(output):
    output.print("ACTION REQUIRED: WaveForms is already open. Please close all instances of WaveForms.", colour="Orange")
    output.print("Waiting for WaveForms to close...")
    while True:
        try:
            Application().connect(title_re='WaveForms.*', timeout=0.5)
        except WindowNotFoundError:
            return
        except TimeoutError:
            return
        except Exception as e:
            pass
        sleep(0.5)
        

class ADCalibration(ComponentTester):
    board_com_num = ''
    voltmeter_com_num = ''
    
    def __init__(self, ad_num):
        self.ad_num = ad_num
    
    @staticmethod
    def set_board_com_num(n):
        ADCalibration.board_com_num = n
        
    def set_voltmeter_com_num(n):
        ADCalibration.voltmeter_com_num = n

    def cancellable(self): 
        return False
    
    def name(self): 
        return f"Analog Digital {self.ad_num}"
    
    def required_setup_step(self) -> int:
        if AD2Calibration.board_com_num == '' or AD2Calibration.voltmeter_com_num == '':
            return len(self.setup_steps())-1
        else:
            return len(self.setup_steps())
    
    def setup_steps(self):
        if self.ad_num == 2:
            ad_img = "Images/ADSetup/step_5_ad2.jpg"
        elif self.ad_num == 3:
            ad_img = "Images/ADSetup/step_5_ad3.jpg"
        
        return [
            SetupStep("Obtain the Analog Digital testing board.", "Images/ADSetup/step_1.jpg"),
            SetupStep("Power the testing board with a 9V DC barrel jack.", "Images/ADSetup/step_2_board.jpg"),
            SetupStep("Connect the Arduino to the computer. The LEDs will turn cyan.", "Images/ADSetup/step_3_board.jpg"),
            SetupStep("Install the VCP drivers for the Arduino Uno board from <a href=\"https://ftdichip.com/wp-content/uploads/2021/08/CDM212364_Setup.zip\">this link</a>. Installation requires administrator access. Installation instructions are available <a href=\"https://ftdichip.com/document/installation-guides/\">here</a>."),
            SetupStep("Then, connect the barrel jacks between the board and the Multimeter. Finally, turn the Multimeter to the Volts measurement setting.", "Images/ADSetup/step_4.jpg"),
            SetupStep("Connect the Multimeter to a serial port on the computer.", "Images/ADSetup/step_4_cable.jpg"),
            SetupStep(f"Connect the Analog Digital {self.ad_num} to the computer and connect the ribbon cable to the pinout board.", ad_img),
            SetupStep("Finally, connect the Analog Digital pinout to the board. Turn the handle to lock the pins.", "Images/ADSetup/step_6.jpg"),
            ComSelectionSetup(self),
            SetupStep("<b>Please do not touch the mouse or the keyboard while the calibration is running.</b>")
        ]
        
    def run_tests(self, output):
        
        ### INIT WAVEFORMS CALIBRATION -----------------------------------------------------------

        waveforms_path_global = "C:/Program Files (x86)/Digilent/WaveForms3/WaveForms.exe"
        waveforms_path_local = os.getcwd()+"/Waveforms/Application/WaveForms3/WaveForms.exe"
        if os.path.exists(waveforms_path_local):
            waveforms_path = waveforms_path_local
        elif os.path.exists(waveforms_path_global):
            output.print("WARNING: using globally installed Waveforms application. Newer Waveforms versions may result in errors.", colour="Orange")
            waveforms_path = waveforms_path_global
        else:
            output.print("ERROR: could not open WaveForms. Application could not be found", colour="Red")
            return
        
        try:
            Application().connect(title_re='WaveForms.*', timeout=0.5)
            wait_for_waveforms_close(output)
        except WindowNotFoundError:
            pass
        except TimeoutError:
            pass
        except Exception:
            wait_for_waveforms_close(output)
        
        output.print("opening WaveForms application...")
        
        try:
            app = Application(backend="uia").start(waveforms_path, timeout=10)
        except Exception as e:
            output.print("ERROR: Could not open WaveForms.", colour="Red")
            output.print("Exception traceback: " + traceback.format_exc(), debug=True)
        
        output.print("starting calibration...")
        
        try:
            bm = ActBoard(f'COM{self.board_com_num}')
        except:
            output.print("ERROR: could not open connection to board. Ensure the board is set up correctly and the COM port is correct.", colour="Red")
            app.kill()
            return
            
        try:
            dmm = UT61E.UT61E(f'COM{self.voltmeter_com_num}')
        except:
            output.print("ERROR: could not open connection to multimeter. Ensure the multimeter is set up correctly and the COM port is correct.", colour="Red")
            app.kill()
            return  
            
        output.print("[Info] opening waveforms main window...", debug=True)
        main_window = app.WaveFormsNewWorkspace
        main_window.wait("visible", timeout=0.5)
        if not main_window.exists():
            output.print("ERROR: could not automatically open Waveforms main window.", colour="Red")
            app.kill()
            return
        
        output.print("opening settings...", debug=True)
        keyboard.send_keys("%s{DOWN 2}{ENTER}")
        
        output.print("[Info] opening device manager...", debug=True)
        dev_manager_window = main_window.child_window(title="Device Manager")
       
        output.print("[Info] opening calibration...", debug=True)
        dev_manager_window.Calibrate.click_input()
        
        output.print("[Info] opening wizard...")
        device_calibration_window = dev_manager_window.DeviceCalibration
        device_calibration_window.Wizard.click_input()
        keyboard.send_keys("{LEFT 1}{ENTER}")
        
        top_window = app.WaveFormsNewWorkspace
        wizard_window = top_window.DeviceCalibrationWizard
        wizard_window.wait("visible", timeout=0.05)
        if not wizard_window.exists():
            output.print("ERROR: could not wizard window", colour="Red")
            app.kill()
            return
        
        ### START WAVEFORMS CALIBRATION -----------------------------------------------------------
        
        try:
            cali_wizard = CaliWizard(wizard_window, output)
            
            if self.ad_num == 2:
                cali_wizard.calibrate(
                    bm, 
                    dmm
                )
            elif self.ad_num == 3:
                cali_wizard.calibrate(
                    bm, 
                    dmm,
                    is_ad3=True
                )
        except Exception as e:
            output.print(f"Exception raised: {e}. Please ensure that the board is set up correctly.", colour="Red")
            output.print("Exception traceback: " + traceback.format_exc(), debug=True)
            app.kill()
            return
        
        app.kill()
        output.print("SUCCESS: Analog digital successfully calibrated", colour="Green")
        
        
class AD2Calibration(ADCalibration):
    def __init__(self):
        super().__init__(2)
        
class AD3Calibration(ADCalibration):
    def __init__(self):
        super().__init__(3)
