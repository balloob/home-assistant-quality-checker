# devolo_home_control: entity-unique-id

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [devolo_home_control](https://www.home-assistant.io/integrations/devolo_home_control/) |
| Rule   | [entity-unique-id](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-unique-id)                                                     |
| Status | **done**                                                                 |

## Overview

The `entity-unique-id` rule applies to this integration as it creates entities for various platforms (sensors, switches, lights, etc.). The integration fully complies with this rule.

A central base class, `DevoloDeviceEntity`, is defined in `homeassistant/components/devolo_home_control/entity.py`. This class is responsible for setting the unique ID for all entities that inherit from it.

In its `__init__` method, the unique ID is set using the `element_uid` provided by the underlying API library:
```python
# homeassistant/components/devolo_home_control/entity.py
class DevoloDeviceEntity(Entity):
    # ...
    def __init__(
        self, homecontrol: HomeControl, device_instance: Zwave, element_uid: str
    ) -> None:
        """Initialize a devolo device entity."""
        # ...
        self._attr_unique_id = element_uid
        # ...
```
All entity platforms within the integration (`binary_sensor`, `climate`, `cover`, `light`, `sensor`, `siren`, `switch`) create entity classes that inherit from `DevoloDeviceEntity`, ensuring that `_attr_unique_id` is always set.

The integration also correctly handles cases where a single API element might produce multiple Home Assistant entities, by further modifying the unique ID to ensure it remains unique.

**Examples of good implementation:**

1.  **`DevoloConsumptionEntity`** in `sensor.py`: Two sensor entities (`current` and `total`) are created from the same API element. To avoid a unique ID collision, the `unique_id` property is overridden to append the sensor type:
    ```python
    # homeassistant/components/devolo_home_control/sensor.py
    class DevoloConsumptionEntity(DevoloMultiLevelDeviceEntity):
        # ...
        @property
        def unique_id(self) -> str:
            # ...
            return f"{self._attr_unique_id}_{self._sensor_type}"
    ```

2.  **`DevoloRemoteControl`** in `binary_sensor.py`: For remote controls with multiple buttons, a unique ID is created for each button by appending the key index to the base `element_uid`:
    ```python
    # homeassistant/components/devolo_home_control/binary_sensor.py
    class DevoloRemoteControl(DevoloDeviceEntity, BinarySensorEntity):
        # ...
        def __init__(
            self,
            # ...
            key: int,
        ) -> None:
            # ...
            super().__init__(
                homecontrol=homecontrol,
                device_instance=device_instance,
                element_uid=f"{element_uid}_{key}",
            )
            # ...
    ```

This consistent and thoughtful approach to assigning unique IDs across all entities demonstrates full compliance with the rule.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 18:59:13 using gemini-2.5-pro-preview-06-05. Prompt tokens: 13192, Output tokens: 784, Total tokens: 16143._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
