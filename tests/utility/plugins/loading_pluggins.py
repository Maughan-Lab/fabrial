from fabrial.utility import plugins

from .test_modules import bad_module, good_module

GOOD_PLUGIN_COUNT = 2
BAD_PLUGIN_COUNT = 1
BAD_PLUGIN_FAILURE_COUNT = 1


def test_load_plugins_from_module():
    """Tests `plugins.load_plugins_from_module()`."""
    # good module, we should see all modules loaded and no errors
    plugin_modules, failure_plugins = plugins.load_plugins_from_module(good_module)
    assert len(plugin_modules) == GOOD_PLUGIN_COUNT
    assert len(failure_plugins) == 0  # we should have no failures
    assert plugin_modules["normal1"] == good_module.normal1
    assert plugin_modules["normal2"] == good_module.normal2

    # bad module, we should see a failure
    plugin_modules, failure_plugins = plugins.load_plugins_from_module(bad_module)
    assert len(plugin_modules) == BAD_PLUGIN_COUNT
    assert len(failure_plugins) == BAD_PLUGIN_FAILURE_COUNT
    assert plugin_modules["normal"] == bad_module.normal
