# devolo_home_network: entity-unique-id

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [devolo_home_network](https://www.home-assistant.io/integrations/devolo_home_network/) |
| Rule   | [entity-unique-id](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-unique-id)                                                     |
| Status | **done**                                       |

## Overview

The `entity-unique-id` rule requires that all entities provided by an integration have a unique ID, which allows Home Assistant to track them across restarts and enables user customizations. This rule applies to the `devolo_home_network` integration as it creates entities across multiple platforms (binary sensor, button, device tracker, image, sensor, switch, and update).

The integration fully complies with this rule by ensuring every entity has a unique and stable ID.

A central base class, `DevoloEntity`, is used for most entities. This class sets the `_attr_unique_id` in its `__init__` method, creating a robust and consistent unique ID.

**`entity.py`:**
```python
class DevoloEntity(Entity):
    # ...
    def __init__(
        self,
        entry: DevoloHomeNetworkConfigEntry,
    ) -> None:
        # ...
        self._attr_unique_id = (
            f"{self.device.serial_number}_{self.entity_description.key}"
        )
```
This pattern, combining the device's unique serial number with the entity description key, ensures that each entity on a given device has a distinct ID.

This base class is used by entities in the following platforms, all of which correctly inherit this behavior:
*   `binary_sensor.py`
*   `button.py`
*   `image.py`
*   `switch.py`
*   `update.py`

The `sensor` platform demonstrates a particularly good implementation for entities that are dynamically created per peer device. The `DevoloPlcDataRateSensorEntity` extends the base unique ID with the peer's MAC address to guarantee uniqueness.

**`sensor.py`:**
```python
class DevoloPlcDataRateSensorEntity(
    BaseDevoloSensorEntity[LogicalNetwork, DataRate, float]
):
    # ...
    def __init__(
        # ...
    ) -> None:
        """Initialize entity."""
        super().__init__(entry, coordinator, description)
        # ...
        self._attr_unique_id = f"{self._attr_unique_id}_{peer}"
        # ...
```

The `device_tracker` platform does not use the `DevoloEntity` base class but correctly implements the `unique_id` property directly for its `DevoloScannerEntity`.

**`device_tracker.py`:**
```python
class DevoloScannerEntity(...):
    # ...
    @property
    def unique_id(self) -> str:
        """Return unique ID of the entity."""
        return f"{self._device.serial_number}_{self.mac_address}"
```
Here, the combination of the devolo device's serial number and the tracked client's MAC address provides a stable and unique identifier.

In summary, all entities created by the `devolo_home_network` integration have a properly assigned unique ID, fully satisfying the rule's requirements.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 19:04:03 using gemini-2.5-pro. Prompt tokens: 18601, Output tokens: 794, Total tokens: 21477._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
