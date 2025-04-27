from .....classes.process import Process
from .....gamry_integration.DrewEIS import main


class EISProcess(Process):
    def run(self):
        print("Starting")
        main()
        print("Ending")
