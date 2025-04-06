from ..base.process import BaseProcess
from . import encoding as DATA


class TestProcess(BaseProcess):
    def run(self):
        print("Test process running!")
        print(f"Average cries: {self.data[DATA.AVERAGE_CRIES]}")
        print(f"Cry count: {self.data[DATA.CRY_COUNT]}")
        print("Test process eneded.")
