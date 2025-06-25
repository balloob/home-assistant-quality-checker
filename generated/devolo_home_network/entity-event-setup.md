# devolo_home_network: entity-event-setup

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [devolo_home_network](https://www.home-assistant.io/integrations/devolo_home_network/) |
| Rule   | [entity-event-setup](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-event-setup)                                                     |
| Status | **exempt**                                       |
| Reason | The integration uses a polling architecture with `DataUpdateCoordinator` and its entities do not subscribe to external events. |

## Overview

The `entity-event-setup` rule requires that entities subscribing to external events (e.g., from a library's event emitter) must register their subscription callbacks in `async_added_to_hass` and unregister them in `async_will_remove_from_hass`.

This rule does not apply to the `devolo_home_network` integration because it is built on a polling architecture, not an event-driven one.

1.  **Polling Architecture**: The integration's `manifest.json` correctly declares its `iot_class` as `"local_polling"`.
2.  **Use of `DataUpdateCoordinator`**: The integration extensively uses `DataUpdateCoordinator` (defined in `coordinator.py`) to periodically fetch data from the devolo devices.
3.  **Entity Implementation**: All entities that receive state updates, such as `DevoloSensorEntity` (`sensor.py`), `DevoloSwitchEntity` (`switch.py`), and others, inherit from `DevoloCoordinatorEntity`. This base class handles state updates via the coordinator's polling mechanism, not through direct event subscriptions. The entities get updated when the coordinator has new data, rather than reacting to a pushed event from the underlying `devolo-plc-api` library.

Since no entities subscribe to external, push-based events to manage their state, the requirements for using `async_added_to_hass` and `async_will_remove_from_hass` for event subscription management are not applicable.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 19:03:34 using gemini-2.5-pro. Prompt tokens: 18867, Output tokens: 479, Total tokens: 20945._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
