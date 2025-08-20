## Fabrial

Fabrial runs user-built sequences. It was originally designed to control lab instruments, but it can be extended through plugins to do much more.

## Installation

TODO: determine if we are supporting the compiled version

```
pip install fabrial
```
Then run
```
fabrial
```
in a terminal.

## Plugins

Fabrial plugins on [PyPi](https://pypi.org/) are generally prefixed with `fabrial-`. If no plugin exists for your use case, you can also [write your own](./doc/plugin_guide/plugin_guide.md)!

## Notes for Developers

- This program uses [PyInstaller](https://pyinstaller.org/en/stable/) to compile and [InstallForge](https://installforge.net/) to create an installer.
    - An awesome reference for both programs can be found [here](https://www.pythonguis.com/tutorials/packaging-pyqt6-applications-windows-pyinstaller/).

## Icons Attribution

Fabrial's [internal](/icons/internal/) icons come from the [Fugue Icon Set](https://p.yusukekamiyamane.com/) by [Yusuke Kamiyamane](https://p.yusukekamiyamane.com/about/), which is licensed under [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/).
