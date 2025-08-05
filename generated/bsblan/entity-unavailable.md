# bsblan: entity-unavailable

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [bsblan](https://www.home-assistant.io/integrations/bsblan/) |
| Rule   | [entity-unavailable](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-unavailable)                                                     |
| Status | **done**                                       |

## Overview

The `entity-unavailable` rule applies to the `bsblan` integration as it is a `local_polling` integration that communicates with a network device. The connection to this device can fail, and in such cases, entities should be marked as unavailable.

The integration correctly follows this rule by utilizing the `DataUpdateCoordinator` pattern.

1.  **Coordinator Implementation:**
    In `homeassistant/components/bsblan/coordinator.py`, the `BSBLanUpdateCoordinator` implements the `_async_update_data` method. This method wraps the data fetching calls in a `try...except` block. When a `BSBLANConnectionError` is caught, it correctly raises an `UpdateFailed` exception.

    ```python
    # homeassistant/components/bsblan/coordinator.py
    
    async def _async_update_data(self) -> BSBLanCoordinatorData:
        """Get state and sensor data from BSB-Lan device."""
        try:
            # ... data fetching ...
            state = await self.client.state()
            sensor = await self.client.sensor()
            dhw = await self.client.hot_water_state()
        # ...
        except BSBLANConnectionError as err:
            host = self.config_entry.data[CONF_HOST] if self.config_entry else "unknown"
            raise UpdateFailed(
                f"Error while establishing connection with BSB-Lan device at {host}"
            ) from err

        # ...
        return BSBLanCoordinatorData(state=state, sensor=sensor, dhw=dhw)
    ```
    Raising `UpdateFailed` signals to the `DataUpdateCoordinator` that the update has failed, which in turn sets its `last_update_success` property to `False`.

2.  **Entity Implementation:**
    In `homeassistant/components/bsblan/entity.py`, the base entity `BSBLanEntity` inherits from `CoordinatorEntity`. All other entities in the integration (in `climate.py`, `sensor.py`, `water_heater.py`) inherit from this base class.

    ```python
    # homeassistant/components/bsblan/entity.py
    
    class BSBLanEntity(CoordinatorEntity[BSBLanUpdateCoordinator]):
        """Defines a base BSBLan entity."""
    
        _attr_has_entity_name = True
    
        def __init__(self, coordinator: BSBLanUpdateCoordinator, data: BSBLanData) -> None:
            """Initialize BSBLan entity."""
            super().__init__(coordinator, data)
            # ...
    ```

    The `CoordinatorEntity` class provides a default `available` property that is tied to `self.coordinator.last_update_success`. As `BSBLanEntity` does not override this property, it correctly uses the default behavior. When the coordinator fails to update, `last_update_success` becomes `False`, and all entities inheriting from `BSBLanEntity` will automatically become unavailable.

This implementation perfectly matches the recommended pattern for handling entity availability with a data update coordinator.

## Suggestions

No suggestions needed.

---

_Created at 2025-08-04 08:35:05 using gemini-2.5-pro. Prompt tokens: 11522, Output tokens: 804, Total tokens: 14103._

_Report based on [`0ab5a05`](https://github.com/home-assistant/core/tree/0ab5a05a1f6e667e6da3771cfc802aa51388bbbe)._

_AI can be wrong. Always verify the report and the code against the rule._
