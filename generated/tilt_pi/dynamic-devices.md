# tilt_pi: dynamic-devices

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [tilt_pi](https://www.home-assistant.io/integrations/tilt_pi/) |
| Rule   | [dynamic-devices](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/dynamic-devices)                                                     |
| Status | **todo**                                                                 |

## Overview

The `dynamic-devices` rule applies to this integration because the Tilt Pi device can detect new Tilt Hydrometers at any time. A good user experience requires that these new hydrometers are automatically added as devices in Home Assistant without needing to reload the integration.

The `tilt_pi` integration currently does not follow this rule. In `sensor.py`, the `async_setup_entry` function is responsible for creating sensor entities.

```python
# homeassistant/components/tilt_pi/sensor.py

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: TiltPiConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Tilt Hydrometer sensors."""
    coordinator = config_entry.runtime_data

    async_add_entities(
        TiltSensor(
            coordinator,
            description,
            hydrometer,
        )
        for description in SENSOR_TYPES
        for hydrometer in coordinator.data.values()
    )
```

This function runs only once when the integration is first set up. It iterates through the hydrometers present in `coordinator.data` *at that specific moment* and creates entities for them. The integration lacks the required mechanism to detect new hydrometers that appear during subsequent data updates from the coordinator. To comply with the rule, it should register a listener with the coordinator that checks for new devices after each data fetch and adds them dynamically.

## Suggestions

To make the integration compliant, you should modify `sensor.py` to track which devices have already been set up and add a listener to the coordinator that creates entities for any new devices that appear.

Here is a suggested implementation for `sensor.async_setup_entry`:

```python
# homeassistant/components/tilt_pi/sensor.py

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: TiltPiConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Tilt Hydrometer sensors."""
    coordinator = config_entry.runtime_data
    known_macs: set[str] = set()

    def _discover_new_devices() -> None:
        """Discover and add new hydrometers."""
        current_macs = set(coordinator.data)
        new_macs = current_macs - known_macs

        if not new_macs:
            return

        entities_to_add = [
            TiltSensor(
                coordinator,
                description,
                coordinator.data[mac_id],
            )
            for mac_id in new_macs
            for description in SENSOR_TYPES
        ]
        
        if entities_to_add:
            known_macs.update(new_macs)
            async_add_entities(entities_to_add)

    # Call the function to add initial devices.
    _discover_new_devices()

    # Register a listener to add new devices that appear in the future.
    config_entry.async_on_unload(
        coordinator.async_add_listener(_discover_new_devices)
    )
```

### Explanation of Changes:

1.  **`known_macs: set[str] = set()`**: This set will store the MAC addresses of hydrometers for which entities have already been created, preventing duplicates.
2.  **`_discover_new_devices()` function**: This new function contains the logic to find and add new devices.
    *   It compares the set of MACs currently in `coordinator.data` with the `known_macs`.
    *   `new_macs = current_macs - known_macs` isolates any hydrometers that have appeared since the last check.
    *   If `new_macs` is not empty, it creates the necessary sensor entities for each new hydrometer.
    *   It then calls `async_add_entities` to add them to Home Assistant and updates the `known_macs` set.
3.  **Initial Call**: The `_discover_new_devices()` function is called once immediately to set up the entities for hydrometers found during the initial refresh.
4.  **Coordinator Listener**: `coordinator.async_add_listener(_discover_new_devices)` registers the function to be called after every successful data update by the coordinator. This ensures that if a new Tilt hydrometer starts broadcasting and is picked up by the Tilt Pi, it will be automatically added to Home Assistant on the next update cycle.

---

_Created at 2025-06-25 18:54:50 using gemini-2.5-pro-preview-06-05. Prompt tokens: 4292, Output tokens: 1119, Total tokens: 7443._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
