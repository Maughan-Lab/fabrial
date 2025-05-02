from ....classes.process import AbstractForegroundProcess
from . import encoding as DATA


class TestProcess(AbstractForegroundProcess):
    def run(self):
        print("Test process running!")
        print(f"Average cries: {self.data()[DATA.AVERAGE_CRIES]}")
        print(f"Cry count: {self.data()[DATA.CRY_COUNT]}")
        print("Test process eneded.")

    @staticmethod
    def directory_name():
        return "Test"
