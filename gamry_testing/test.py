# NOTE: this script will only work on Windows (the comtypes module), and Gamry software must be
# installed to even access GamryCOM. Quincy cannot be fully cross-plo

import comtypes.client as client

if __name__ == "__main__":
    devices = client.CreateObject(progid="GamryCOM.GamryDeviceList")
    ex
    print(devices.EnumSections())