from .....classes.process import AbstractGraphingProcess
from .....gamry_integration.DrewEIS import main


class EISProcess(AbstractGraphingProcess):
    def run(self):
        print("Starting")
        main()
        print("Ending")

    @staticmethod
    def directory_name():
        return "Electrochemical Impedance Spectroscopy"
