from pywinauto.application import Application, WindowSpecification
waveformsPath = "C:/Program Files (x86)/Digilent/WaveForms3/WaveForms.exe"
class WaveFormsAutomator: 
    def __init__(self, app) -> None:
        if app == None:
            raise Exception("Must run start_app first!")
        self.__app__: Application = app
        self.wizard_window: WindowSpecification = None

    @staticmethod
    def start_app(connectToExisting: bool =False):
        if not connectToExisting:
            app = Application(backend="uia").start(waveformsPath, timeout=10)
            return app
        app = Application(backend="uia").connect(path=waveformsPath, timeout=10)
        return app
    
    def getapp(self):
        return self.__app__
    
    def open_calibration_wizard(self):
        # TODO: Handle situation when Waveforms is in any other window
        # other than start
        main_window = self.__app__.WaveFormsNewWorkspace
        if not main_window.exists():
            raise Exception("Main window does not exist")
        if self.is_wizard_window_open():
            return 
        settings_menu = main_window.Settings
        settings_menu.click_input()
        main_window.DeviceManager.click_input()
        dev_manager_window = main_window.DeviceManager
        dev_manager_window.Calibrate.click_input()
        device_calibration_window = dev_manager_window.DeviceCalibration
        device_calibration_window.Wizard.click_input()
        device_calibration_window.Yes.click_input()
        device_calibration_window.DeviceCalibrationWizard
    
    def get_wizard_window(self) -> WindowSpecification:
        if not self.is_wizard_window_open():
            raise Exception("Calibration window not open")
        top_window = self.__app__.WaveFormsNewWorkspace
        self.wizard_window = top_window.DeviceCalibrationWizard
        return self.wizard_window
    
    def is_wizard_window_open(self):
        top_window = self.__app__.WaveFormsNewWorkspace
        wizard_window = top_window.DeviceCalibrationWizard
        return wizard_window.exists()


