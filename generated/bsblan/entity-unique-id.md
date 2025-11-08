# bsblan: entity-unique-id

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [bsblan](https://www.home-assistant.io/integrations/bsblan/) |
| Rule   | [entity-unique-id](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-unique-id)                                                     |
| Status | **todo**                                       |

## Overview

The `entity-unique-id` rule requires that all entities provided by an integration have a unique ID. This is crucial for Home Assistant's entity registry to track entities across restarts, allowing users to apply customizations.

The `bsblan` integration creates entities for the `climate`, `sensor`, and `water_heater` platforms. The rule is therefore applicable.

The integration correctly assigns unique IDs for its `climate` and `sensor` entities by combining the device's MAC address with an entity-specific key.

-   **Sensor (`sensor.py`):** `self._attr_unique_id = f"{data.device.MAC}-{description.key}"`
-   **Climate (`climate.py`):** `self._attr_unique_id = f"{format_mac(data.device.MAC)}-climate"`

However, the `water_heater` entity does not follow this best practice. Its unique ID is set to only the device's MAC address, which is also used as the unique ID for the config entry itself.

-   **Water Heater (`water_heater.py`):**
    ```python
    def __init__(self, data: BSBLanData) -> None:
        """Initialize BSBLAN water heater."""
        super().__init__(data.coordinator, data)
        self._attr_unique_id = format_mac(data.device.MAC)
        # ...
    ```

While this may not cause an immediate failure, it is not robust. An entity's unique ID should uniquely identify the entity, not just the device it belongs to. Using the device's MAC address alone does not distinguish this specific entity from the device or from other potential entities of the same type if the hardware were to support it. This makes the implementation non-compliant with the spirit and best practices of the rule.

## Suggestions

To ensure all entities have a robust and distinct unique ID, the `BSBLANWaterHeater` entity should be updated to follow the same pattern as the other entities in this integration.

In `homeassistant/components/bsblan/water_heater.py`, modify the `__init__` method to append a static suffix to the MAC address for the `_attr_unique_id`.

**Current Code:**
```python
# homeassistant/components/bsblan/water_heater.py
class BSBLANWaterHeater(BSBLanEntity, WaterHeaterEntity):
    # ...
    def __init__(self, data: BSBLanData) -> None:
        """Initialize BSBLAN water heater."""
        super().__init__(data.coordinator, data)
        self._attr_unique_id = format_mac(data.device.MAC)
        # ...
```

**Suggested Change:**
```python
# homeassistant/components/bsblan/water_heater.py
class BSBLANWaterHeater(BSBLanEntity, WaterHeaterEntity):
    # ...
    def __init__(self, data: BSBLanData) -> None:
        """Initialize BSBLAN water heater."""
        super().__init__(data.coordinator, data)
        # Append a suffix to make the entity unique ID distinct from the device ID.
        self._attr_unique_id = f"{format_mac(data.device.MAC)}-water_heater"
        # ...
```

This change brings the `water_heater` platform into alignment with the `climate` and `sensor` platforms, ensuring every entity has a properly formed unique ID that is distinct from the device's unique ID.

---

_Created at 2025-08-05 09:37:14 using gemini-2.5-pro. Prompt tokens: 10902, Output tokens: 890, Total tokens: 14421._

_Report based on [`ee9ff71`](https://github.com/home-assistant/core/tree/ee9ff717e0d36ca02bf52a242acd3a47359eae61)._

_AI can be wrong. Always verify the report and the code against the rule._
