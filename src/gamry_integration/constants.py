import comtypes.client as client

try:
    GamryCOM = client.GetModule(r"C:\Program Files (x86)\Gamry Instruments\Framework\GamryCom.exe")
except Exception:
    GamryCOM = None
