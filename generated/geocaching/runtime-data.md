# geocaching: runtime-data

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [geocaching](https://www.home-assistant.io/integrations/geocaching/) |
| Rule   | [runtime-data](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/runtime-data)                                                     |
| Status | **done**                                                                 |

## Overview

The `runtime-data` rule applies to this integration because it uses a config entry to manage its connection and data, which requires a runtime object (a `DataUpdateCoordinator`) to be shared across platforms.

The `geocaching` integration correctly follows this rule by storing its `DataUpdateCoordinator` instance in `ConfigEntry.runtime_data`.

Specifically:

1.  **Typed `ConfigEntry`**: In `coordinator.py`, a type alias is created to provide strong typing for the data stored in `runtime_data`:
    ```python
    # homeassistant/components/geocaching/coordinator.py:20
    type GeocachingConfigEntry = ConfigEntry[GeocachingDataUpdateCoordinator]
    ```

2.  **Storing Runtime Data**: In `__init__.py`, after the `GeocachingDataUpdateCoordinator` is initialized, it is stored in `entry.runtime_data`:
    ```python
    # homeassistant/components/geocaching/__init__.py:21
    entry.runtime_data = coordinator
    ```

3.  **Accessing Runtime Data**: The sensor platform's `async_setup_entry` function correctly retrieves the coordinator from `entry.runtime_data`, benefiting from the type hints established in the previous steps.
    ```python
    # homeassistant/components/geocaching/sensor.py:73-77
    async def async_setup_entry(
        hass: HomeAssistant,
        entry: GeocachingConfigEntry,
        async_add_entities: AddConfigEntryEntitiesCallback,
    ) -> None:
        """Set up a Geocaching sensor entry."""
        coordinator = entry.runtime_data
        # ...
    ```

This implementation adheres perfectly to the best practices outlined in the rule, ensuring data is stored consistently and type-safely.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 18:49:49 using gemini-2.5-pro-preview-06-05. Prompt tokens: 5738, Output tokens: 518, Total tokens: 8026._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
