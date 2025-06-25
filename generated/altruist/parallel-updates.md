# altruist: parallel-updates
| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [altruist](https://www.home-assistant.io/integrations/altruist/) |
| Rule   | [parallel-updates](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/parallel-updates)                                                     |
| Status | **todo**                                                                 |

## Overview
The `parallel-updates` rule requires that integrations explicitly define the number of parallel updates they can handle by setting the `PARALLEL_UPDATES` constant in each entity platform file.

This rule applies to the `altruist` integration as it provides a `sensor` platform. The integration uses a `DataUpdateCoordinator` to manage data fetching centrally for all its sensor entities. According to the rule's guidelines, when a coordinator is used for read-only platforms (like `sensor`), `PARALLEL_UPDATES` should be set to `0`. This indicates that entity updates are already managed by the coordinator and do not need to be run in parallel by the entity platform.

A review of the code shows that the `homeassistant/components/altruist/sensor.py` file is missing the `PARALLEL_UPDATES` constant.

## Suggestions
To comply with the rule, you should explicitly declare the parallel update behavior in the `sensor.py` file. Since this integration uses a `DataUpdateCoordinator` for its sensor platform, the correct value is `0`.

Add the following constant to the top of `homeassistant/components/altruist/sensor.py`:

```python
# In homeassistant/components/altruist/sensor.py

"""Defines the Altruist sensor platform."""

from collections.abc import Callable
# ... (other imports)

from . import AltruistConfigEntry
from .coordinator import AltruistDataUpdateCoordinator

# Add this line
PARALLEL_UPDATES = 0

_LOGGER = logging.getLogger(__name__)

# ... (rest of the file)
```

Adding `PARALLEL_UPDATES = 0` makes it clear that the integration relies on the coordinator for updates and does not require the Home Assistant core to manage parallel updates for its sensor entities. This fulfills the requirement of the rule.

---

_Created at 2025-06-25 18:51:26 using gemini-2.5-pro-preview-06-05. Prompt tokens: 6360, Output tokens: 509, Total tokens: 8173._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
