# bsblan: action-setup

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [bsblan](https://www.home-assistant.io/integrations/bsblan/) |
| Rule   | [action-setup](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/action-setup)                                                     |
| Status | **exempt**                                       |
| Reason | The integration does not register any custom services. |

## Overview

The `action-setup` rule requires that custom integration services are registered in the `async_setup` function, rather than `async_setup_entry`. This ensures service calls can be validated even when the associated config entry is not loaded.

A review of the `bsblan` integration's code shows that it does not register any custom services. There are no calls to `hass.services.async_register` within the integration's files. All user-callable actions are implemented through standard platform entity methods, such as:
- `ClimateEntity.async_set_hvac_mode` in `climate.py`
- `ClimateEntity.async_set_temperature` in `climate.py`
- `WaterHeaterEntity.async_set_temperature` in `water_heater.py`
- `WaterHeaterEntity.async_set_operation_mode` in `water_heater.py`

Home Assistant Core handles the registration of these standard services (e.g., `climate.set_hvac_mode`, `water_heater.set_temperature`). Since the `bsblan` integration provides no custom services of its own, this rule does not apply.

## Suggestions

No suggestions needed.

---

_Created at 2025-08-05 09:34:58 using gemini-2.5-pro. Prompt tokens: 11117, Output tokens: 383, Total tokens: 12542._

_Report based on [`ee9ff71`](https://github.com/home-assistant/core/tree/ee9ff717e0d36ca02bf52a242acd3a47359eae61)._

_AI can be wrong. Always verify the report and the code against the rule._
