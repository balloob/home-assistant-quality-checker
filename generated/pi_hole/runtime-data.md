# pi_hole: runtime-data

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [pi_hole](https://www.home-assistant.io/integrations/pi_hole/) |
| Rule   | [runtime-data](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/runtime-data)                                                     |
| Status | **done**                                                                 |
| Reason |                                                                          |

## Overview

The `runtime-data` rule mandates the use of `ConfigEntry.runtime_data` for storing data that is needed during the lifetime of a configuration entry but is not persisted to configuration file storage. This promotes consistency and enables typed access to this data.

This rule **applies** to the `pi_hole` integration. The integration initializes an API client (`hole.Hole`) and a `DataUpdateCoordinator` during its setup process. These are quintessential examples of runtime data that should be managed via `ConfigEntry.runtime_data`.

The `pi_hole` integration **fully follows** this rule.

1.  **Typed `ConfigEntry` and Data Structure:**
    In `homeassistant/components/pi_hole/__init__.py`, the integration defines a `dataclass` named `PiHoleData` to encapsulate its runtime objects:
    ```python
    @dataclass
    class PiHoleData:
        """Runtime data definition."""

        api: Hole
        coordinator: DataUpdateCoordinator[None]
    ```
    It then defines a typed `ConfigEntry` using this dataclass:
    ```python
    type PiHoleConfigEntry = ConfigEntry[PiHoleData]
    ```
    This approach aligns perfectly with the rule's recommendation for typed access to `runtime_data`.

2.  **Storing Runtime Data:**
    Within the `async_setup_entry` function in `homeassistant/components/pi_hole/__init__.py`, after initializing the `Hole` API client (`api`) and the `DataUpdateCoordinator` (`coordinator`), an instance of `PiHoleData` is created and assigned to `entry.runtime_data`:
    ```python
    # Snippet from homeassistant/components/pi_hole/__init__.py
    # ... api and coordinator are initialized ...

    entry.runtime_data = PiHoleData(api, coordinator)
    ```
    This is the correct method for storing runtime data as per the rule.

3.  **Accessing Runtime Data:**
    Throughout the integration, particularly in platform setup files (e.g., `sensor.py`, `switch.py`, `binary_sensor.py`, `update.py`) and other utility files like `diagnostics.py`, the `ConfigEntry` object `entry` is correctly typed as `PiHoleConfigEntry`. The runtime data is then accessed via `entry.runtime_data`:
    *   Example from `homeassistant/components/pi_hole/sensor.py`:
        ```python
        async def async_setup_entry(
            hass: HomeAssistant,
            entry: PiHoleConfigEntry, # Typed entry
            async_add_entities: AddConfigEntryEntitiesCallback,
        ) -> None:
            """Set up the Pi-hole sensor."""
            name = entry.data[CONF_NAME]
            hole_data = entry.runtime_data # Accessing runtime_data
            sensors = [
                PiHoleSensor(
                    hole_data.api, # Using data from runtime_data
                    hole_data.coordinator, # Using data from runtime_data
                    name,
                    entry.entry_id,
                    description,
                )
                for description in SENSOR_TYPES
            ]
            async_add_entities(sensors, True)
        ```
    *   Example from `homeassistant/components/pi_hole/diagnostics.py`:
        ```python
        async def async_get_config_entry_diagnostics(
            hass: HomeAssistant, entry: PiHoleConfigEntry # Typed entry
        ) -> dict[str, Any]:
            """Return diagnostics for a config entry."""
            api = entry.runtime_data.api # Accessing runtime_data
            # ...
        ```
    This consistent and typed access demonstrates adherence to the rule's intent.

The integration correctly uses `ConfigEntry.runtime_data` with appropriate typing, ensuring that runtime objects are managed in a standardized and safe manner.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-10 23:10:59. Prompt tokens: 10029, Output tokens: 997, Total tokens: 14018._

_Report based on [`ab7f6c3`](https://github.com/home-assistant/core/tree/ab7f6c35287f43fe1207b3de4581b3bfabd49399)._

_AI can be wrong. Always verify the report and the code against the rule._
