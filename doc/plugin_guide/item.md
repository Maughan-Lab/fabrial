## The Item

Items with widgets use the [`WidgetDataItem`](../../fabrial/sequence_builder/data_item.py) protocol. All this means is that our item class has specific requirements from `WidgetDataItem`. Like before, we need to import `WidgetDataItem` from Fabrial plus some extras.

<sub>Filename: random_data/random_item.py</sub>
```python
import typing
from collections.abc import Iterable, Mapping
from typing import Self

from fabrial import Json, SequenceStep, WidgetDataItem

# notice that we import our widget too
from .random_widget import RandomDataWidget
```

Next, we're going to create our item class. Let's call it `RandomDataItem`. We need to implement the `WidgetDataItem` protocol, which means inheriting from `WidgetDataItem`.

<sub>Filename: random_data/random_item.py</sub>
```python
# --snip--

# this constant is used for serializing and deserializing later
DATA_INTERVAL_KEY = "data_interval"


# we inherit from `WidgetDataItem` so Fabrial can use the item
class RandomDataItem(WidgetDataItem):
    """Record random data on an interval; item."""

    pass
```

Although we are inheriting from `WidgetDataItem`, we don't actually inherit any data. `WidgetDataItem` is a [Protocol](https://typing.python.org/en/latest/spec/protocol.html), meaning it has *requirements* rather than data. `WidgetDataItem` requires the following methods:
- `serialize()` - Converts the item into a dictionary.
- `deserialize()` - Converts a dictionary into the item. This is a classmethod, so it must be decorated with `@classmethod`.
- `widget()` - Gets the widget.
- `create_sequence_step()` - Creates the step the sequence runs.

Fabrial calls these functions when using our item, so they define how our item behaves. Let's implement them!

<sub>Filename: random_data/random_item.py</sub>
```python
# --snip--

class RandomDataItem(WidgetDataItem):
    """Record random data on an interval; item."""

    def __init__(self, data_interval: float):
        # the only thing we need to do here is create the widget
        self.random_data_widget = RandomDataWidget(data_interval)

    def serialize(self) -> dict[str, Json]:
        # we store the data interval in a dictionary
        return {DATA_INTERVAL_KEY: self.random_data_widget.interval_spinbox.value()}

    @classmethod  # notice the `@classmethod` decorator. You must have this
    def deserialize(cls, serialized_obj: Mapping[str, Json]) -> Self:
        # `cls` is the class, `RandomDataItem` in this case

        # we extract the data interval from the serialized object
        # notice how we use the same dictionary key as in `serialize()`
        data_interval = serialized_obj[DATA_INTERVAL_KEY]
        # `typing.cast()` is for type checkers; it is optional if you
        # aren't type checking
        return cls(typing.cast(float, data_interval))
        # the above line is equivalent to
        # `return RandomDataItem(data_interval)`

    def widget(self) -> RandomDataWidget:
        # this is just a getter for the widget
        return self.random_data_widget

    # the `substeps` parameter is always an empty list for items that don't
    # support subitems. If the item does supports subitems, those items will be
    # converted into sequence steps and passed to this function
    def create_sequence_step(self, substeps: Iterable[SequenceStep]) -> SequenceStep:
        # we will implement this later
        raise NotImplementedError("Not ready yet!")
```

> You'll notice we didn't really implement `create_sequence_step()`. We'll come back to fix this after we've written our step class.

There are also some optional methods for further customization:
- `supports_subitems()` - Whether the item supports nested items. By default, this just returns `False`.
- `expand_event()` - Called when the item is expanded. Only relevant if your item supports subitems.
- `collapse_event()` - Called when the item is collapsed. Only relevant if your item supports subitems.

For this tutorial, our item doesn't support subitems, so we'll ignore these methods.

### Putting the Item in the Sequence Builder

Now that we have our item class, let's make it accessible to Fabrial. We'll use one of Fabrial's entry point functions for this: `categories()`. This function returns a list of [`PluginCategory`](../../fabrial/utility/sequence_builder.py)s, where each `PluginCategory` is a separate category containing items. The function definition goes in the project's **`__init__.py`** file.

<sub>Filename: random_data/\_\_init\_\_.py</sub>
```python
from fabrial import PluginCategory

# notice we import our item
from .random_item import RandomDataItem


def categories() -> list[PluginCategory]:
    # we use "Random" as the name of the category
    # when creating the `RandomDataItem`, we use 5 as the default value
    return [PluginCategory("Random", [RandomDataItem(5)])]
```

> #### Category Notes
>
> If your category's name is the same as an existing category, your items will appear alongside others in that category.
>
> If your plugin has subcategories, you can specify them in `PluginCategory()`. You can create virtually any category structure this way.

If you are [testing as you go](./plugin_guide.md#testing-as-you-go), you can run Fabrial and our category and item should appear. Drag and drop should work automatically. Try starting a sequence with the item. Oh no! It threw an error?! Don't worry, we'll fix that soon.

___

Nice! That's the item class done for now.

The complete item code is shown below.

<sub>Filename: random_data/random_item.py</sub>
```python
import typing
from collections.abc import Iterable, Mapping
from typing import Self

from fabrial import Json, SequenceStep, WidgetDataItem

from .random_widget import RandomDataWidget

DATA_INTERVAL_KEY = "data_interval"


class RandomDataItem(WidgetDataItem):
    """Record random data on an interval; item."""

    def __init__(self, data_interval: float):
        self.random_data_widget = RandomDataWidget(data_interval)

    def serialize(self) -> dict[str, Json]:
        return {DATA_INTERVAL_KEY: self.random_data_widget.interval_spinbox.value()}

    @classmethod
    def deserialize(cls, serialized_obj: Mapping[str, Json]) -> Self:
        data_interval = serialized_obj[DATA_INTERVAL_KEY]
        return cls(typing.cast(float, data_interval))

    def widget(self) -> RandomDataWidget:
        return self.random_data_widget

    def create_sequence_step(self, substeps: Iterable[SequenceStep]) -> SequenceStep:
        raise NotImplementedError("Not ready yet!")
```