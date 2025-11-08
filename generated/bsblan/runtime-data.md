# bsblan: runtime-data

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [bsblan](https://www.home-assistant.io/integrations/bsblan/) |
| Rule   | [runtime-data](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/runtime-data)                                                     |
| Status | **done**                                                                 |

## Overview

The `runtime-data` rule applies to this integration because it initializes several objects during setup that are required for the duration of the config entry's lifecycle. These include the API client (`BSBLAN`), the data update coordinator (`BSBLanUpdateCoordinator`), and initial device information. These objects need to be shared with the integration's platforms (climate, sensor, water_heater).

The `bsblan` integration correctly and fully follows this rule. It implements the recommended pattern for storing and accessing runtime data in a consistent and type-safe manner.

Key points of the implementation:
1.  **Typed Config Entry**: In `__init__.py`, a custom type alias is defined for the config entry, specifying the type of data that will be stored in `runtime_data`:
    ```python
    # __init__.py
    type BSBLanConfigEntry = ConfigEntry[BSBLanData]
    ```

2.  **Runtime Data Structure**: A `dataclass` named `BSBLanData` is used to neatly bundle all runtime objects (client, coordinator, device info, etc.) into a single, typed structure.
    ```python
    # __init__.py
    @dataclasses.dataclass
    class BSBLanData:
        """BSBLan data stored in the Home Assistant data object."""
        coordinator: BSBLanUpdateCoordinator
        client: BSBLAN
        device: Device
        info: Info
        static: StaticState
    ```

3.  **Storing Runtime Data**: In `async_setup_entry`, after all necessary objects are initialized, an instance of `BSBLanData` is created and assigned to `entry.runtime_data`.
    ```python
    # __init__.py
    async def async_setup_entry(hass: HomeAssistant, entry: BSBLanConfigEntry) -> bool:
        # ... client and coordinator setup ...
        entry.runtime_data = BSBLanData(
            client=bsblan,
            coordinator=coordinator,
            device=device,
            info=info,
            static=static,
        )
        # ...
        return True
    ```

4.  **Accessing Runtime Data**: All platform setup functions (e.g., `sensor.py`, `climate.py`, `water_heater.py`) and other components like `diagnostics.py` use the `BSBLanConfigEntry` type hint and access the data via `entry.runtime_data`. This ensures type safety and clarity.
    ```python
    # sensor.py
    async def async_setup_entry(
        hass: HomeAssistant,
        entry: BSBLanConfigEntry,
        async_add_entities: AddConfigEntryEntitiesCallback,
    ) -> None:
        """Set up BSB-Lan sensor based on a config entry."""
        data = entry.runtime_data
        async_add_entities(BSBLanSensor(data, description) for description in SENSOR_TYPES)
    ```

This implementation is a model example of adherence to the `runtime-data` rule.

## Suggestions
No suggestions needed.

---

_Created at 2025-08-05 09:38:04 using gemini-2.5-pro. Prompt tokens: 10959, Output tokens: 789, Total tokens: 13507._

_Report based on [`ee9ff71`](https://github.com/home-assistant/core/tree/ee9ff717e0d36ca02bf52a242acd3a47359eae61)._

_AI can be wrong. Always verify the report and the code against the rule._
