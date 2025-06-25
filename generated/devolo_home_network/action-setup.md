# devolo_home_network: action-setup

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [devolo_home_network](https://www.home-assistant.io/integrations/devolo_home_network/) |
| Rule   | [action-setup](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/action-setup)                                                     |
| Status | **exempt**                                       |
| Reason | The integration does not register any custom services. |

## Overview

The `action-setup` rule requires that custom integration services are registered in the `async_setup` function, not within `async_setup_entry`. This ensures that services are always known to Home Assistant, even if the configuration entry for the device is not currently loaded, which improves automation validation and user feedback.

This rule is not applicable to the `devolo_home_network` integration. A review of the integration's code shows that it does not define or register any custom services using `hass.services.async_register`.

The integration provides entities such as buttons, switches, and update entities. These entities expose standard Home Assistant services (e.g., `button.press`, `switch.turn_on`, `update.install`) which are handled by their respective base integrations (`button`, `switch`, `update`). The logic for these actions is correctly implemented within the entity methods like `async_press` in `button.py` and `async_turn_on`/`async_turn_off` in `switch.py`.

Since no custom services are being registered, the requirements of the `action-setup` rule do not apply.

---

_Created at 2025-06-25 19:01:55 using gemini-2.5-pro. Prompt tokens: 18816, Output tokens: 375, Total tokens: 20637._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
