from ....classes.process import Process
from . import encoding as DATA


class TestProcess(Process):
    def run(self):
        print("Test process running!")
        print(f"Average cries: {self.data[DATA.AVERAGE_CRIES]}")
        print(f"Cry count: {self.data[DATA.CRY_COUNT]}")
        print("Test process eneded.")
