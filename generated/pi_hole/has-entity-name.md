# pi_hole: has-entity-name

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [pi_hole](https://www.home-assistant.io/integrations/pi_hole/) |
| Rule   | [has-entity-name](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/has-entity-name)                                                     |
| Status | **todo**                                                                 |
| Reason | (Only include if Status is "exempt". Explain why the rule does not apply.) |

## Overview

The `has-entity-name` rule requires entities to set `_attr_has_entity_name = True` to improve naming consistency. The entity's name is then constructed as "Device Name Entity Name". If the entity represents the main feature of a device, `_attr_name` should be set to `None` (or the `name` property should return `None`), resulting in the entity being named after the device.

This rule applies to the `pi_hole` integration as it provides several entities (binary_sensor, sensor, switch, update).

The integration partially follows the rule:

*   **Sensor Entities (`sensor.py`):** The `PiHoleSensor` class correctly sets `_attr_has_entity_name = True`. It uses `SensorEntityDescription` with `translation_key` to define the entity-specific part of the name. This is compliant.
    ```python
    # homeassistant/components/pi_hole/sensor.py
    class PiHoleSensor(PiHoleEntity, SensorEntity):
        # ...
        _attr_has_entity_name = True
        # ...
    ```

*   **Binary Sensor Entities (`binary_sensor.py`):** The `PiHoleBinarySensor` class correctly sets `_attr_has_entity_name = True`. It uses `PiHoleBinarySensorEntityDescription` with `translation_key` for the entity-specific part of the name. This is compliant.
    ```python
    # homeassistant/components/pi_hole/binary_sensor.py
    class PiHoleBinarySensor(PiHoleEntity, BinarySensorEntity):
        # ...
        _attr_has_entity_name = True
        # ...
    ```

*   **Update Entities (`update.py`):** The `PiHoleUpdateEntity` class correctly sets `_attr_has_entity_name = True`. It uses `PiHoleUpdateEntityDescription` with `translation_key` for the entity-specific part of the name. This is compliant.
    ```python
    # homeassistant/components/pi_hole/update.py
    class PiHoleUpdateEntity(PiHoleEntity, UpdateEntity):
        # ...
        _attr_has_entity_name = True
        # ...
    ```

*   **Switch Entity (`switch.py`):** The `PiHoleSwitch` class does **not** set `_attr_has_entity_name = True`. Instead, it relies on the default `_attr_has_entity_name = False` and overrides the `name` property to return the device name (`self._name`).
    ```python
    # homeassistant/components/pi_hole/switch.py
    class PiHoleSwitch(PiHoleEntity, SwitchEntity):
        """Representation of a Pi-hole switch."""

        _attr_icon = "mdi:pi-hole"
        # _attr_has_entity_name is MISSING (defaults to False)

        @property
        def name(self) -> str:
            """Return the name of the switch."""
            return self._name # self._name is the device name passed to PiHoleEntity
    ```
    While this results in the switch entity being named after the device (e.g., "Pi-hole"), which is appropriate for a main feature, it does not follow the prescribed mechanism of setting `_attr_has_entity_name = True` and `_attr_name = None` (or ensuring the `name` property returns `None`). The rule is specific about using `_attr_has_entity_name = True`.

Because the `PiHoleSwitch` entity does not conform to the rule, the integration's status is "todo".

## Suggestions

To make the `pi_hole` integration fully compliant with the `has-entity-name` rule, the `PiHoleSwitch` entity in `homeassistant/components/pi_hole/switch.py` needs to be updated.

The Pi-hole switch can be considered the main feature of the Pi-hole device (enabling/disabling Pi-hole). According to the rule, for such main features, `_attr_has_entity_name` should be `True` and `_attr_name` should be `None`, so the entity is named after the device.

**Proposed changes for `homeassistant/components/pi_hole/switch.py`:**

1.  **Add `_attr_has_entity_name = True`** to the `PiHoleSwitch` class.
2.  **Add `_attr_name = None`** to the `PiHoleSwitch` class.
3.  **Remove the overridden `name` property.** The base `Entity` class logic, in conjunction with `_attr_has_entity_name = True` and `_attr_name = None`, will correctly name the entity after the device.

**Example of the modified `PiHoleSwitch` class:**

```python
# homeassistant/components/pi_hole/switch.py

# ... (imports and other code) ...

class PiHoleSwitch(PiHoleEntity, SwitchEntity):
    """Representation of a Pi-hole switch."""

    _attr_icon = "mdi:pi-hole"
    _attr_has_entity_name = True  # Added
    _attr_name = None  # Added: Indicates this entity should be named after the device

    # The following 'name' property should be removed:
    # @property
    # def name(self) -> str:
    #     """Return the name of the switch."""
    #     return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique id of the switch."""
        return f"{self._server_unique_id}/Switch"

    @property
    def is_on(self) -> bool:
        """Return if the service is on."""
        return self.api.data.get("status") == "enabled"  # type: ignore[no-any-return]

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the service."""
        try:
            await self.api.enable()
            # It's better to rely on coordinator update, but if immediate feedback is needed
            # and it doesn't happen via coordinator, self.async_write_ha_state() might be considered
            # after direct API call success. Or, preferably, trigger a coordinator refresh.
            await self.coordinator.async_request_refresh()
        except HoleError as err:
            _LOGGER.error("Unable to enable Pi-hole: %s", err)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the service."""
        await self.async_disable()

    async def async_disable(self, duration: Any = None) -> None:
        """Disable the service for a given duration."""
        duration_seconds = True  # Disable infinitely by default
        if duration is not None:
            duration_seconds = duration.total_seconds()
            _LOGGER.debug(
                "Disabling Pi-hole '%s' (%s) for %d seconds",
                self.entity_id, # Use self.entity_id or a more descriptive name if available
                self.api.host,
                duration_seconds,
            )
        try:
            await self.api.disable(duration_seconds)
            # Similar to async_turn_on, prefer coordinator refresh
            await self.coordinator.async_request_refresh()
        except HoleError as err:
            _LOGGER.error("Unable to disable Pi-hole: %s", err)

# ... (rest of the file) ...
```

**Why these changes satisfy the rule:**
*   Setting `_attr_has_entity_name = True` explicitly opts into the new naming scheme.
*   Setting `_attr_name = None` (and removing the `name` property override) signals that this entity is the main feature of the device. The Home Assistant entity system will then use the device's name as the entity's name. This aligns with the example provided in the rule for a lock entity representing the main device feature.

By implementing these changes, the `PiHoleSwitch` entity will adhere to the `has-entity-name` rule, making the entire `pi_hole` integration compliant.

---

_Created at 2025-06-10 23:10:20. Prompt tokens: 10158, Output tokens: 2015, Total tokens: 17729._

_Report based on [`ab7f6c3`](https://github.com/home-assistant/core/tree/ab7f6c35287f43fe1207b3de4581b3bfabd49399)._

_AI can be wrong. Always verify the report and the code against the rule._
