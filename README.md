# Auto Component Tester

Automatically calibrates or tests various components.
Currently supports:
- Calibrating Analog Digital 2 and 3
- Testing Digital Multimeter
- Testing Current Source (TODO part num)

## How To Use

1. Install Python
2. Run `python -m pip install -r requirements.txt`
3. Run `python gui.py`

The GUI will guide you through the process.

## Adding Other Components

Testing and calibrating other components is simple:
1. Create a class inheriting from the `ComponentTester` class in the `components.py` file. 
Look at the `AD2Calibration` class as an example.
2. Override the `run_tests`, `name`, and `setup_steps` methods.
3. Import that class from `gui.py` and add it to the `TESTS` list.