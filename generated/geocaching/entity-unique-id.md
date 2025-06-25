# geocaching: entity-unique-id

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [geocaching](https://www.home-assistant.io/integrations/geocaching/) |
| Rule   | [entity-unique-id](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-unique-id)                                                     |
| Status | **done**                                                                 |

## Overview

The `entity-unique-id` rule requires that all entities provided by an integration have a unique ID. This is crucial for allowing users to customize entities and for Home Assistant to track them across restarts.

This rule applies to the `geocaching` integration as it creates `sensor` entities to display user statistics.

The integration correctly follows this rule. In the `geocaching/sensor.py` file, the `GeocachingSensor` class, which represents the sensors created by the integration, sets a unique ID for each entity in its `__init__` method.

The unique ID is constructed as follows:

`geocaching/sensor.py`:
```python
class GeocachingSensor(
    CoordinatorEntity[GeocachingDataUpdateCoordinator], SensorEntity
):
    # ...
    def __init__(
        self,
        coordinator: GeocachingDataUpdateCoordinator,
        description: GeocachingSensorEntityDescription,
    ) -> None:
        """Initialize the Geocaching sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.data.user.reference_code}_{description.key}"
        )
        # ...
```

This implementation combines the user's unique `reference_code` (which is also used as the device identifier) with the `description.key` of the specific sensor (e.g., `find_count`, `hide_count`). This ensures that every entity created by the integration has a stable and unique ID, fully satisfying the rule's requirements. For example, an ID might look like `PRCABCDE_find_count`.

---

_Created at 2025-06-25 18:49:03 using gemini-2.5-pro-preview-06-05. Prompt tokens: 5681, Output tokens: 480, Total tokens: 7312._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
