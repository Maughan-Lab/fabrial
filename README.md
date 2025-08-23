## Fabrial

Fabrial runs user-built sequences. It was originally designed to control lab instruments, but it can be extended through plugins to do much more.

## Installation

> The easiest way to install and manage Python executables is with [`uv tool`](https://docs.astral.sh/uv/guides/tools/). See [`uv`](https://docs.astral.sh/uv/)'s documentation for using this command. Otherwise, I highly recommend using a [virtual environment](https://docs.python.org/3/library/venv.html).

Install fabrial with
```
pip install fabrial
```
and run it with
```
fabrial
```

### Application Shortcut

If you'd like Fabrial to have an application shortcut (i.e. the Start Menu on Windows or a `.desktop` file on Linux), run

```
pip install fabrial[shortcut]
```

instead. Then, inside virtual environment Fabrial is installed in, enter the Python shell and run

```
>>> import fabrial
>>> fabrial.create_application_shortcut()
```

## Usage

Drag and drop sequence actions from the left into the sequence builder on the right. Then, select a directory to record data it, press the start button, and voilà! You've got a running sequence. Each action has its own parameters you can customize from the sequence builder, as well as a description of what the action does.

## Plugins

Fabrial does very little on its own, but it can be extended through plugins that add new sequence actions.

Fabrial plugins on [PyPi](https://pypi.org/) are generally prefixed with `fabrial-`. If you install a local plugin with `pip`, Fabrial will recognize it automatically. Global plugins can be installed through the settings menu. Note that if a plugin is installed in both the current environment and in the **`plugins`** folder, the latter plugin is ignored.

If no plugin exists for your use case, you can also [write your own](./doc/plugin_guide/plugin_guide.md)!

## Error Log
Fabrial logs any errors it encounters in **`HOME/.fabrial/lastrun.log`**. This error log is wiped at startup, so if Fabrial encounters an error, please consider reporting before starting restarting the application!

## Icons Attribution

Fabrial's [internal](./fabrial/assets/icons/internal/) icons come from the [Fugue Icon Set](https://p.yusukekamiyamane.com/) by [Yusuke Kamiyamane](https://p.yusukekamiyamane.com/about/), which is licensed under [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/).
