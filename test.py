
from Waveforms.WaveformsAutomator import WaveFormsAutomator
from Waveforms.CaliWizard import CaliWizard
from calibration import calibrate
import asyncio
from external import read_voltage, reset_dummy
import time
# Start app
app = WaveFormsAutomator.start_app(connectToExisting=True)
time.sleep(2)
wavAuto = WaveFormsAutomator(app)
time.sleep(2)
wavAuto.open_calibration_wizard()
wizard_window = wavAuto.get_wizard_window()
caliWizard = CaliWizard(wizard_window)
time.sleep(2)
#https://stackoverflow.com/questions/47518874/how-do-i-run-python-asyncio-code-in-a-jupyter-notebook
async def run():
    reset_dummy()
    print("Starting calibration...")
    value = await calibrate(caliWizard)
    print("Calibration done!", value)

asyncio.run(run())