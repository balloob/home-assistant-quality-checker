# geocaching: entity-event-setup

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [geocaching](https://www.home-assistant.io/integrations/geocaching/) |
| Rule   | [entity-event-setup](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-event-setup)                                                     |
| Status | **exempt**                                       |
| Reason | The integration's entities do not subscribe to any events. |

## Overview

The `entity-event-setup` rule requires that entities subscribe to events in `async_added_to_hass` and unsubscribe in `async_will_remove_from_hass` to ensure proper lifecycle management and prevent memory leaks.

This rule does not apply to the `geocaching` integration. The integration follows the `DataUpdateCoordinator` pattern, as indicated by its `iot_class` of `cloud_polling` in `manifest.json`. The `GeocachingDataUpdateCoordinator` in `coordinator.py` is responsible for polling the Geocaching API periodically to fetch data.

The `GeocachingSensor` entities in `sensor.py` inherit from `CoordinatorEntity`. They do not subscribe to any external events themselves. Instead, they receive updates via the coordinator mechanism. The entity's state is derived directly from the coordinator's data in the `native_value` property:

`sensor.py`:
```python
class GeocachingSensor(
    CoordinatorEntity[GeocachingDataUpdateCoordinator], SensorEntity
):
    # ...
    @property
    def native_value(self) -> str | int | None:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)
```

Since the entities do not manage any event subscriptions, the requirements of this rule are not applicable.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 18:48:45 using gemini-2.5-pro-preview-06-05. Prompt tokens: 5947, Output tokens: 436, Total tokens: 7434._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
