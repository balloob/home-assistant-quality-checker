# bsblan: action-exceptions

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [bsblan](https://www.home-assistant.io/integrations/bsblan/) |
| Rule   | [action-exceptions](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/action-exceptions)                                                     |
| Status | **done**                                                                 |

## Overview
The `action-exceptions` rule applies to this integration because it provides `climate` and `water_heater` entities, which expose user-callable services (e.g., setting temperature, changing HVAC mode).

The integration correctly follows this rule by raising appropriate exceptions when actions fail.

1.  **`ServiceValidationError` for Invalid User Input:**
    In `climate.py`, the `async_set_preset_mode` service correctly validates user input. If a user tries to set a preset mode when the HVAC mode is not 'auto', it raises a `ServiceValidationError`. This is the correct exception for handling invalid service calls.

    ```python
    # homeassistant/components/bsblan/climate.py:126-132
    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set preset mode."""
        if self.hvac_mode != HVACMode.AUTO and preset_mode != PRESET_NONE:
            raise ServiceValidationError(
                "Preset mode can only be set when HVAC mode is set to 'auto'",
                translation_domain=DOMAIN,
                translation_key="set_preset_mode_error",
                translation_placeholders={"preset_mode": preset_mode},
            )
        await self.async_set_data(preset_mode=preset_mode)
    ```

2.  **`HomeAssistantError` for Device/Communication Failures:**
    Throughout the `climate` and `water_heater` platforms, when an action fails due to a communication issue with the device (indicated by a `BSBLANError` from the underlying library), the integration correctly catches this specific error and raises a `HomeAssistantError`. This informs the user that an internal or communication error occurred. All such exceptions are properly chained (`from err`) and use translatable messages.

    Example from `water_heater.py`:
    ```python
    # homeassistant/components/bsblan/water_heater.py:101-107
    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        try:
            await self.coordinator.client.set_hot_water(nominal_setpoint=temperature)
        except BSBLANError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="set_temperature_error",
            ) from err
    ```

    Example from `climate.py`:
    ```python
    # homeassistant/components/bsblan/climate.py:149-156
    try:
        await self.coordinator.client.thermostat(**data)
    except BSBLANError as err:
        raise HomeAssistantError(
            "An error occurred while updating the BSBLAN device",
            translation_domain=DOMAIN,
            translation_key="set_data_error",
        ) from err
    ```

The integration consistently uses the correct exception types for different failure scenarios, adhering to the rule's requirements.

## Suggestions
No suggestions needed.

---

_Created at 2025-08-04 08:34:12 using gemini-2.5-pro. Prompt tokens: 11068, Output tokens: 805, Total tokens: 13949._

_Report based on [`0ab5a05`](https://github.com/home-assistant/core/tree/0ab5a05a1f6e667e6da3771cfc802aa51388bbbe)._

_AI can be wrong. Always verify the report and the code against the rule._
