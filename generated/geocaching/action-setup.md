# geocaching: action-setup

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [geocaching](https://www.home-assistant.io/integrations/geocaching/) |
| Rule   | [action-setup](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/action-setup)                                                     |
| Status | **exempt**                                       |
| Reason | The integration does not register any custom services. |

## Overview

The `action-setup` rule requires that any custom services provided by an integration are registered within the `async_setup` function, rather than `async_setup_entry`. This ensures that the services are always available for validation, even if the configuration entry is not loaded.

A review of the `geocaching` integration's code shows that it does not define or register any custom services. The primary functionality is to provide `sensor` entities through a `DataUpdateCoordinator`. There are no calls to `hass.services.async_register` in any of the provided Python files (`__init__.py`, `coordinator.py`, `sensor.py`, etc.).

Since the integration does not offer any custom services, the rule about where to register them does not apply. Therefore, the integration is considered exempt from this rule.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 18:47:04 using gemini-2.5-pro-preview-06-05. Prompt tokens: 5896, Output tokens: 302, Total tokens: 7234._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
