# devolo_home_network: runtime-data

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [devolo_home_network](https://www.home-assistant.io/integrations/devolo_home_network/) |
| Rule   | [runtime-data](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/runtime-data)                                                     |
| Status | **done**                                                                 |

## Overview

The `runtime-data` rule applies to this integration as it needs to manage runtime objects, specifically the API client instance (`Device`) and several data update coordinators.

The integration correctly and fully implements this rule. It follows the best practices outlined in the documentation by creating a dedicated dataclass to hold all runtime data and using a typed `ConfigEntry`.

Key evidence of compliance includes:

1.  **Typed Config Entry and Data Class:**
    In `coordinator.py`, a dataclass `DevoloHomeNetworkData` is defined to structure the runtime data. A type alias, `DevoloHomeNetworkConfigEntry`, is then created to strongly type the `ConfigEntry` with this data class.

    ```python
    # homeassistant/components/devolo_home_network/coordinator.py
    @dataclass
    class DevoloHomeNetworkData:
        """The devolo Home Network data."""

        device: Device
        coordinators: dict[str, DevoloDataUpdateCoordinator[Any]]

    type DevoloHomeNetworkConfigEntry = ConfigEntry[DevoloHomeNetworkData]
    ```

2.  **Correct Initialization in `async_setup_entry`:**
    In `__init__.py`, the `async_setup_entry` function correctly uses the typed `DevoloHomeNetworkConfigEntry` and assigns an instance of `DevoloHomeNetworkData` to `entry.runtime_data`.

    ```python
    # homeassistant/components/devolo_home_network/__init__.py
    async def async_setup_entry(
        hass: HomeAssistant, entry: DevoloHomeNetworkConfigEntry
    ) -> bool:
        """Set up devolo Home Network from a config entry."""
        # ...
        entry.runtime_data = DevoloHomeNetworkData(device=device, coordinators={})
        # ...
        entry.runtime_data.coordinators = coordinators
        # ...
    ```

3.  **Consistent Usage:**
    The typed `DevoloHomeNetworkConfigEntry` is used consistently across all files (e.g., `entity.py`, `switch.py`, `sensor.py`, `diagnostics.py`). Runtime data is always accessed via `entry.runtime_data`, ensuring type safety and code clarity.

    For example, in `entity.py`:
    ```python
    # homeassistant/components/devolo_home_network/entity.py
    class DevoloEntity(Entity):
        # ...
        def __init__(
            self,
            entry: DevoloHomeNetworkConfigEntry,
        ) -> None:
            """Initialize a devolo home network device."""
            self.device = entry.runtime_data.device
            # ...
    ```

The integration's implementation is a textbook example of how to correctly use `ConfigEntry.runtime_data`.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 19:05:27 using gemini-2.5-pro. Prompt tokens: 18658, Output tokens: 755, Total tokens: 21925._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
