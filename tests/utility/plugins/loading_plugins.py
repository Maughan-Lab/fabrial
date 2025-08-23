from pathlib import Path

from pytest import mark

from fabrial.utility import plugins

from .test_modules import bad_module, good_module

GOOD_PLUGIN_COUNT = 2
BAD_PLUGIN_COUNT = 1
BAD_PLUGIN_FAILURE_COUNT = 1

GOOD_MODULE_PLUGIN1 = "plugin1"
GOOD_MODULE_PLUGIN2 = "plugin2"

BAD_MODULE_NORMAL = "plugin1"
BAD_MODULE_ERROR = "throws_error"


def test_discover_plugins_from_module():
    """Tests `plugins.discover_plugins_from_module()`."""
    # `good_module`
    good_plugins = plugins.discover_plugins_from_module(good_module)
    assert len(good_plugins) == 2
    assert GOOD_MODULE_PLUGIN1 in good_plugins
    assert GOOD_MODULE_PLUGIN2 in good_plugins
    # loading the plugins should return the modules
    assert good_plugins[GOOD_MODULE_PLUGIN1]() == good_module.plugin1
    assert good_plugins[GOOD_MODULE_PLUGIN2]() == good_module.plugin2

    # `bad_module` (`discover_plugins_from_module()` should not load the plugins)
    bad_plugins = plugins.discover_plugins_from_module(bad_module)
    assert len(bad_plugins) == 2
    assert BAD_MODULE_NORMAL in bad_plugins
    assert BAD_MODULE_ERROR in bad_plugins


def test_load_plugin_settings():
    """Tests `plugins.load_plugin_settings()`."""
    settings_directory = Path(__file__).parent.joinpath("test_plugin_settings")

    # isn't missing entries
    assert plugins.load_plugin_settings(
        settings_directory.joinpath("complete.json"), ["one", "two", "three"]
    ) == {"one": False, "two": True, "three": False}

    # missing "three" entry ("three" should be assumed enabled)
    assert plugins.load_plugin_settings(
        settings_directory.joinpath("missing_some.json"), ["one", "two", "three"]
    ) == {"one": False, "two": True, "three": True}

    # doesn't exist (all entries should be `True`)
    assert plugins.load_plugin_settings(
        settings_directory.joinpath("nonexistent.json"), ["one", "two", "three"]
    ) == {"one": True, "two": True, "three": True}


def test_load_plugins():
    """Tests `plugins.load_plugins()`."""
    # assuming `plugins.discover_plugins_from_module()` works from earlier test

    # normal case
    assert plugins.load_plugins(
        plugins.discover_plugins_from_module(good_module),
        {GOOD_MODULE_PLUGIN1: True, GOOD_MODULE_PLUGIN2: True},
    )[0] == {GOOD_MODULE_PLUGIN1: good_module.plugin1, GOOD_MODULE_PLUGIN2: good_module.plugin2}

    # try with one of the plugins disabled
    assert plugins.load_plugins(
        plugins.discover_plugins_from_module(good_module),
        {GOOD_MODULE_PLUGIN1: True, GOOD_MODULE_PLUGIN2: False},
    )[0] == {GOOD_MODULE_PLUGIN1: good_module.plugin1}

    # try with a bad plugin
    assert plugins.load_plugins(
        plugins.discover_plugins_from_module(bad_module),
        {BAD_MODULE_NORMAL: True, BAD_MODULE_ERROR: True},
    ) == ({BAD_MODULE_NORMAL: bad_module.plugin1}, [BAD_MODULE_ERROR])


@mark.xfail(raises=KeyError)
def test_load_plugins_incomplete_settings():
    """Tests `plugins.load_plugins()` with an incomplete settings dictionary."""
    # since the plugin settings dictionary does not contain all discovered plugin names, this test
    # should fail
    plugins.load_plugins(plugins.discover_plugins_from_module(good_module), {})
