# devolo_home_control: action-setup

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [devolo_home_control](https://www.home-assistant.io/integrations/devolo_home_control/) |
| Rule   | [action-setup](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/action-setup)                                                     |
| Status | **exempt**                                       |
| Reason | The integration does not register any custom services. |

## Overview

The `action-setup` rule requires that custom integration services are registered in the `async_setup` function, rather than `async_setup_entry`. This ensures that service actions are always available for validation, even if the corresponding config entry is not loaded.

A thorough review of the `devolo_home_control` integration's code shows that it does not define or register any custom services. There are no calls to `hass.services.async_register` in any of the provided Python files.

Since the integration does not offer any custom services, the rule governing where and how to register them does not apply. Therefore, the integration is considered exempt from this rule.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 18:57:05 using gemini-2.5-pro-preview-06-05. Prompt tokens: 13407, Output tokens: 283, Total tokens: 14647._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
