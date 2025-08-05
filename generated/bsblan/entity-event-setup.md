# bsblan: entity-event-setup

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [bsblan](https://www.home-assistant.io/integrations/bsblan/) |
| Rule   | [entity-event-setup](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-event-setup)                                                     |
| Status | **exempt**                                       |
| Reason | The integration uses the `DataUpdateCoordinator` pattern for polling and does not use a push-based event system for entity updates. |

## Overview

This rule requires that entities subscribe to events in `async_added_to_hass` and unsubscribe in `async_will_remove_from_hass`. This is crucial for integrations that use a push-based update mechanism where the device or library emits events that entities must listen to.

The `bsblan` integration, however, is designed around a polling-based architecture. It uses the `DataUpdateCoordinator` pattern to periodically fetch data from the BSB-Lan device.

1.  **Coordinator Setup**: In `__init__.py`, a `BSBLanUpdateCoordinator` is instantiated. This coordinator is responsible for polling the device at a regular interval defined in `coordinator.py`.
    ```python
    # homeassistant/components/bsblan/__init__.py
    coordinator = BSBLanUpdateCoordinator(hass, entry, bsblan)
    await coordinator.async_config_entry_first_refresh()
    ```

2.  **Polling Mechanism**: The `BSBLanUpdateCoordinator._async_update_data` method in `coordinator.py` actively fetches the latest state from the device. It does not listen for or subscribe to any events.
    ```python
    # homeassistant/components/bsblan/coordinator.py
    async def _async_update_data(self) -> BSBLanCoordinatorData:
        """Get state and sensor data from BSB-Lan device."""
        # ...
        state = await self.client.state()
        sensor = await self.client.sensor()
        dhw = await self.client.hot_water_state()
        # ...
        return BSBLanCoordinatorData(state=state, sensor=sensor, dhw=dhw)
    ```

3.  **Entity Implementation**: All entities in the integration, such as `BSBLanSensor`, `BSBLANClimate`, and `BSBLANWaterHeater`, inherit from `BSBLanEntity`, which in turn inherits from `CoordinatorEntity`.
    ```python
    # homeassistant/components/bsblan/entity.py
    class BSBLanEntity(CoordinatorEntity[BSBLanUpdateCoordinator]):
        """Defines a base BSBLan entity."""
    ```
    The `CoordinatorEntity` base class handles the logic of receiving updates from the coordinator. The entities simply read their state from the coordinator's data (`self.coordinator.data`). They do not need to manage their own event subscriptions.

Since the integration does not use a push-based event system for entity updates, the `entity-event-setup` rule does not apply.

## Suggestions

No suggestions needed.

---

_Created at 2025-08-05 09:36:37 using gemini-2.5-pro. Prompt tokens: 11168, Output tokens: 712, Total tokens: 13589._

_Report based on [`ee9ff71`](https://github.com/home-assistant/core/tree/ee9ff717e0d36ca02bf52a242acd3a47359eae61)._

_AI can be wrong. Always verify the report and the code against the rule._
