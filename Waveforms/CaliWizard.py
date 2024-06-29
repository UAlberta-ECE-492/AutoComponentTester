# Handler for the Calibration Wizard window
from typing import List
from Serial.ActBoards.Boards.ActBoard.ActBoard import ActBoard
from Waveforms.WaveformsAutomator import WaveFormsAutomator
from pywinauto import mouse, keyboard, Desktop
from time import sleep
from constants import stages_map_ad2, stages_map_ad3
from external import switch_relays_ad2, switch_relays_ad3
from Board.BoardManager import BoardManager
from Serial.ActBoards.RelayStates import RelayStates
from Serial.ActBoards.Boards.ActBoard.config.ActCommands import ActCalStatus
from SerialDevs import UT61E

import time

class CaliWizard: 
    def __init__(self, wizard_window, output):
        self.output = output
        if wizard_window == None:
            raise Exception("Must specify the wizard window object")
        self.__wizard_window__ = wizard_window
        self.__comboBox__ = self.__wizard_window__.ComboBox
        self.__cali_stage_names__ = self.__comboBox__.texts()
        
    def click_next(self) -> None:
        # This is way faster than self.wizard_window.Next.click_input()
        """
        Clicks the Next button in the Device Calibration Wizard window
        """
        self.__click_button__("Next")

    def click_back(self) -> None:
        # This is way faster than self.wizard_window.Next.click_input()
        """
        Clicks the Back button in the Device Calibration Wizard window
        """
        self.__click_button__("Back")

    def click_cancel(self) -> None:
        # This is way faster than self.wizard_window.Next.click_input()
        """
        Clicks the Cancel button in the Device Calibration Wizard window
        """
        self.__click_button__("Cancel")

    def click_yes(self) -> None:
        # This is way faster than self.wizard_window.Next.click_input()
        """
        Clicks the Yes button in the Device Calibration Wizard window
        """
        self.__click_button__("Yes")

    def click_ok(self) -> None:
        # This is way faster than self.wizard_window.Next.click_input()
        """
        Clicks the Ok button in the Device Calibration Wizard window
        """
        self.__wizard_window__.Ok.click_input()
    def click_retry(self) -> None:
        # This is way faster than self.wizard_window.Next.click_input()
        """
        Clicks the Retry button in the Device Calibration Wizard window
        """
        self.__click_button__("Retry")

    def __click_button__(self, button_title: str) -> None:
        """
        This can click on any button with the specific title in the Device Calibration Wizard window's and sub windows.

        Returns:
            None
        """
        # This is way faster than self.wizard_window.Next.click_input()
        self.__wizard_window__.child_window(title=button_title).click_input()
    
    def write_to_input(self, text: str) -> None:
        """
        Adds a text to the Measured: input box in the Device Calibration Wizard window
        """
        self.__wizard_window__.Edit3.set_text(text)
        
    def type_to_input_and_send(self, text: str) -> None:
        """
        Adds a text to the Measured: input box in the Device Calibration Wizard window
        """
        keyboard.send_keys(text + "{ENTER}")
    
    def get_instruction_text(self) -> str:
        """
        Returns the text from the top text box with wiring instructions
        """
        return self.__wizard_window__.Edit2.texts()
        
    
    def get_text_input(self) -> str:
        """
        Returns the text from the Measured: input box in the Device Calibration Wizard window
        """
        # TODO: Add error handling
        arr = self.__wizard_window__.Edit3.texts()
        return arr[0]

    def get_current_cali_stage_idx(self) -> int:
        """
        This returns the current calibration stage index from the Device Calibration Wizard window's ComboBox;
        There are in total 10 different calibration stages, starting at 0. Start, and ending in 9. End

        Returns:
            int: The idx of the currently selected item in the comboBox representing current calibration stage.
        """
        return self.__comboBox__.selected_index()
    
    def get_current_cali_stage_name(self) -> str:
        """
        This returns the current calibration stage text from the Device Calibration Wizard window's ComboBox;

        Returns:
            str: The text of the currently selected item in the comboBox representing current calibration stage.
        """
        return self.__comboBox__.selected_text()

    def get_cali_stages(self) -> List[str]:
        """
        This returns all the calibration stages available in the Device Calibration Wizard window's ComboBox;

        Returns:
            List[str]: Array of calibration stages from the Device Calibration comboBox.
        """
        return self.__comboBox__.texts()

    def go_to_cali_stage_by_idx(self, stage_idx: int) -> List[str]:
        """
        This goes to the specified calibration stage idx in the Device Calibration Wizard.

        Returns:
            None
        """
        item_title = self.__cali_stage_names__[stage_idx]
        self.__comboBox__.select(stage_idx)
        self.__comboBox__.child_window(title=item_title, control_type="ListItem").click_input()
    
    def go_to_cali_stage_by_name(self, stage_title: int) -> List[str]:
        """
        This goes to the specified calibration stage by key in the Device Calibration Wizard.

        Returns:
            None
        """
        self.__comboBox__.select(0)
        self.__comboBox__.child_window(title=stage_title, control_type="ListItem").click_input()

    def search_window_names(self, title: str) -> bool:
        """
        This gets a list of all visible windows and checks if "title" is a substring of any

        Args:
            title (str): the string to search for 

        Returns:
            bool: true if substring was found
        """
        windows = Desktop(backend="win32").windows()
        found = False
        i = 0
        while not found and i < len(windows):
            if title in windows[i].window_text():
                found = True
            i += 1
        return found

    def is_popup_shown(self, title: str) -> bool:
        """
        This checks whether a child window has opened on top of the Device Calibration Wizard window with a specific title.

        Returns:
            bool: True if any new window has been opened and matches the title, False otherwise.
        """
        try:
            top = self.__wizard_window__.child_window(title=title, control_type="Window")
            top.wait("visible", timeout=0.05)
            return top.exists()
        except:
            return False
          
    def read_and_write_v(self, dmm, i, post_sleep=0, limit=5):
        for _ in range(i):
            if post_sleep > 0:
                sleep(post_sleep)
            sleep(0.2)
            v = str(dmm.read_v())
            self.type_to_input_and_send(v)
            
            count = 0
            while (self.search_window_names("Error")):
                keyboard.send_keys("{ENTER}")
                v = str(dmm.read_v())
                self.type_to_input_and_send(v)
                count += 1
                if count >= limit:
                    raise Exception("Calibration error")

    def calibrate(self, bm, dmm, is_ad3=False):
        
        try:
            bm.reset_relays()
            keyboard.send_keys("{ENTER}")
            
            if not is_ad3:
                # AD2 linearity
                sleep(1)
                keyboard.send_keys("{ENTER}")
            
            # "Waveform Generator 1 Low Gain"
            bm.set_relay_state(RelayStates.STATE_WG1)
            self.read_and_write_v(dmm, 5)
                
            # "Waveform Generator 1 High Gain"
            self.read_and_write_v(dmm, 5)
                
            # "Waveform Generator 2 Low Gain"
            bm.set_relay_state(RelayStates.STATE_WG2)
            self.read_and_write_v(dmm, 5)
                
            # "Waveform Generator 2 High Gain"
            self.read_and_write_v(dmm, 5)
            
            # "Oscilloscope"  part 1 -- all to ground
            bm.set_relay_state(RelayStates.STATE_SCOPE_TO_GND)
            keyboard.send_keys("{ENTER}")
            
            # check for part 2
            instruction = self.get_instruction_text()[-1]
            while instruction != 'Connect the Oscilloscope N inputs to ground.':
                sleep(0.5)
                instruction = self.get_instruction_text()[-1]
            
            # "Oscilloscope"  part 2 -- 1+ and 2+ to WG1
            bm.set_relay_state(RelayStates.STATE_SCOPE_TO_WG1)
            keyboard.send_keys("{ENTER}")
            if is_ad3:
                sleep(5)
            else:
                sleep(20)
            # keyboard.send_keys("{ENTER}")
            
            if is_ad3:
                # AD3 osc linearity
                bm.set_relay_state(RelayStates.STATE_SCOPE_TO_GND)
                keyboard.send_keys("{ENTER}")
                sleep(15)   
        
            # "7. Positive Supply"
            bm.set_relay_state(RelayStates.STATE_V_PLUS)
            self.read_and_write_v(dmm, 2, post_sleep=3)
            
            # "8. Negative Supply"
            bm.set_relay_state(RelayStates.STATE_V_MINUS)
            self.read_and_write_v(dmm, 2, post_sleep=2)
            
            # "9. End"
            self.__wizard_window__.child_window(title="Finish").click_input()
            self.__wizard_window__.child_window(title="Apply").click_input()
            self.__wizard_window__.child_window(title="Yes").click_input()
            sleep(3)
            bm.set_cal_status(ActCalStatus.cal_good)
            print("Saving calibration steps...")
        except Exception as e:
            bm.set_cal_status(ActCalStatus.error)
            dmm.close()
            bm.close()
            raise e
        dmm.close()
        bm.close()
