## Fabrial

Fabrial runs user-built sequences. It was originally designed to control lab instruments, but it can be extended through plugins to do much more.

## Installation

```
pip install fabrial
```
Then run
```
fabrial
```
in a terminal.

### Packaged Application (Windows Only)

Fabrial is also packaged using PyInstaller. Head over to the [latest release](https://github.com/Maughan-Lab/fabrial/releases/latest), then download and run `FabrialInstaller.exe`. This installation method does not require Python.

## Usage

Drag and drop sequence actions from the left into the sequence builder on the right. Then, select a directory to record data it, press the start button, and voilà! You've got a running sequence. Each action has its own parameters you can customize from the sequence builder, as well as a description of what the action does.

## Plugins

Fabrial does very little on its own, but it can be extended through plugins that add new sequence actions.

Fabrial plugins on [PyPi](https://pypi.org/) are generally prefixed with `fabrial-`. If you install a plugin with `pip`, Fabrial will recognize it automatically. Local plugins can also be installed through the settings menu.

If no plugin exists for your use case, you can also [write your own](./doc/plugin_guide/plugin_guide.md)!

## Notes for Maintainers

This program uses [PyInstaller](https://pyinstaller.org/en/stable/) to compile and [InstallForge](https://installforge.net/) to create an installer.

>An awesome reference for both programs can be found [here](https://www.pythonguis.com/tutorials/packaging-pyqt6-applications-windows-pyinstaller/).

## Icons Attribution

Fabrial's [internal](./fabrial/assets/icons/internal/) icons come from the [Fugue Icon Set](https://p.yusukekamiyamane.com/) by [Yusuke Kamiyamane](https://p.yusukekamiyamane.com/about/), which is licensed under [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/).
