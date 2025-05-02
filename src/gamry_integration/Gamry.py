import types

import comtypes.client as client  # type: ignore


class GamryInterface:
    """Convenience class for interacting with Gamry hardware."""

    def __init__(self) -> None:
        # TODO: make the location of GamryCOM customizable
        self.GamryCOM = client.GetModule(
            r"C:\Program Files (x86)\Gamry Instruments\Framework\GamryCom.exe"
        )
        self.device_list = client.CreateObject(self.GamryCOM.GamryDeviceList)
        self.pstats: list[Potentiostat] = []

    def module(self) -> types.ModuleType:
        """Get the underlying Module object used to interface with Gamry."""
        return self.GamryCOM

    def get_pstat_list(self) -> list[str]:
        """Get a list of Gamry potentiostat identifiers."""
        return self.device_list.EnumSections()

    def create_pstat(self, identifier: str):
        """Create a **Potentiostat** from the provided **identifier**."""
        pstat = Potentiostat(self.module(), identifier)
        self.pstats.append(pstat)
        return pstat

    def cleanup(self):
        """Clean up the interface (call this before the application terminates)."""
        self.device_list.Release()  # closes GamryCOM.exe
        for pstat in self.pstats:  # TODO: see if this is necessary or even works
            pstat.cleanup()


class Potentiostat:
    def __init__(self, COM_interface: types.ModuleType, identifer: str):
        """
        :param COM_interface: The Module object used interface with Gamry.
        :param identifier: An identifier for the physical potentiostat.
        """
        self.GamryCOM = COM_interface
        self.device = client.CreateObject(self.GamryCOM.GamryPstat)
        self.device.Init(identifer)

    def cleanup(self):
        """
        Clean up the potentiostat resources. If the potentiostat was created through a
        **GamryInterface**, this function is called automatically when the interface's `cleanup()`
        method runs.
        """
        self.device.Release()

    # TODO: add more methods to the pstat


GAMRY: GamryInterface = GamryInterface()
