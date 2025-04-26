# -*- mode: python ; coding: utf-8 -*-

import os
import shutil

name = "Quincy"

a = Analysis(
    ["../main.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon="../icons/oven_icon.ico",
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    contents_directory="internal",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=name,
)

# copy the dependencies into dist/Quincy
# filenames are relative to the base directory
FILES_TO_COPY = ["oven_settings.json"]
FOLDERS_TO_COPY = ["icons", "initialization", "item_descriptions"]
for file in FILES_TO_COPY:
    shutil.copyfile(os.path.join("..", file), os.path.join("dist", name, file))
for folder in FOLDERS_TO_COPY:
    shutil.copytree(os.path.join("..", folder), os.path.join("dist", name, folder))
