# devolo_home_control: runtime-data

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [devolo_home_control](https://www.home-assistant.io/integrations/devolo_home_control/) |
| Rule   | [runtime-data](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/runtime-data)                                                     |
| Status | **done**                                                                 |

## Overview
The `runtime-data` rule applies to this integration as it establishes and manages connections to devolo Home Control gateways during the Home Assistant runtime. These connection objects (`HomeControl` instances) are considered runtime data.

The `devolo_home_control` integration correctly follows this rule by utilizing the `ConfigEntry.runtime_data` attribute to store and access its runtime objects.

This is implemented perfectly throughout the integration:

1.  **Typed Config Entry:** A custom type alias is defined in `homeassistant/components/devolo_home_control/__init__.py`, which strongly types the `runtime_data` attribute.
    ```python
    # homeassistant/components/devolo_home_control/__init__.py
    type DevoloHomeControlConfigEntry = ConfigEntry[list[HomeControl]]
    ```

2.  **Storing Runtime Data:** In `async_setup_entry`, the integration creates one or more `HomeControl` instances and stores them in `entry.runtime_data`, matching the type hint.
    ```python
    # homeassistant/components/devolo_home_control/__init__.py
    async def async_setup_entry(
        hass: HomeAssistant, entry: DevoloHomeControlConfigEntry
    ) -> bool:
        """Set up the devolo account from a config entry."""
        # ...
        try:
            # ...
            entry.runtime_data = []
            for gateway_id in gateway_ids:
                entry.runtime_data.append(
                    await hass.async_add_executor_job(
                        partial(
                            HomeControl,
                            # ...
                        )
                    )
                )
        # ...
    ```

3.  **Accessing Runtime Data:** All other parts of the integration, such as platform setup files (`sensor.py`, `light.py`, etc.) and the `diagnostics.py` file, consistently use the typed `DevoloHomeControlConfigEntry` and access the gateway objects from `entry.runtime_data`.

    Example from `homeassistant/components/devolo_home_control/sensor.py`:
    ```python
    async def async_setup_entry(
        hass: HomeAssistant,
        entry: DevoloHomeControlConfigEntry,
        async_add_entities: AddConfigEntryEntitiesCallback,
    ) -> None:
        """Get all sensor devices and setup them via config entry."""
        entities: list[SensorEntity] = []

        for gateway in entry.runtime_data:
            # ... entities are created using the 'gateway' object
    ```

This implementation adheres to all requirements of the `runtime-data` rule, promoting consistency and type safety.

## Suggestions
No suggestions needed.

---

_Created at 2025-06-25 19:00:06 using gemini-2.5-pro-preview-06-05. Prompt tokens: 13249, Output tokens: 722, Total tokens: 16118._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
