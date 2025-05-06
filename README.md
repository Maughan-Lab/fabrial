# Quincy-New
A full rewrite of Quincy using PyQt6.

Quincy is an application for controlling lab instruments. Currently, it supports ovens capable of communicating using modbus protocols and [Gamry](https://www.gamry.com/) potentiostats.

# Installation
I'm really bad at GitHub, so currently the solution is to clone/download the repository, then run the [installer](/packaging/Quincy%20Installer.exe).

# Notes for Developers
- This program uses PyInstaller to compile and InstallForge to create an installer.
    * An awesome reference for both programs can be found [here](https://www.pythonguis.com/tutorials/packaging-pyqt6-applications-windows-pyinstaller/).
- You can add additional sequence builder items by following the instructions [here](/docs/Adding%20New%20Sequence%20Items.md).

# Icons Attribution
Quincy's [internal](/icons/internal/) icons come from the [Fugue Icon Set](https://p.yusukekamiyamane.com/) by [Yusuke Kamiyamane](https://p.yusukekamiyamane.com/about/), which is licensed under [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/).
