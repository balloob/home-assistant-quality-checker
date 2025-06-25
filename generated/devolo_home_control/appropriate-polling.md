# devolo_home_control: appropriate-polling

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [devolo_home_control](https://www.home-assistant.io/integrations/devolo_home_control/) |
| Rule   | [appropriate-polling](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/appropriate-polling)                                                     |
| Status | **exempt**                                       |
| Reason | The integration uses a push-based update mechanism, not polling. |

## Overview

The `appropriate-polling` rule requires that integrations which poll for data set a reasonable default polling interval. This rule does not apply to the `devolo_home_control` integration because it is a push-based integration, not a polling one.

Evidence for this can be found in several places in the codebase:

1.  **`manifest.json`**: The integration's `iot_class` is declared as `"local_push"`, which signals to Home Assistant and developers that it receives data updates from the device or service directly, rather than polling for them.
    ```json
    // homeassistant/components/devolo_home_control/manifest.json
    {
      "domain": "devolo_home_control",
      ...
      "iot_class": "local_push",
      ...
    }
    ```

2.  **Base Entity Configuration**: In `entity.py`, the base entity `DevoloDeviceEntity` explicitly disables polling for all derived entities by setting `_attr_should_poll = False`.
    ```python
    // homeassistant/components/devolo_home_control/entity.py
    class DevoloDeviceEntity(Entity):
        def __init__(...):
            ...
            self._attr_should_poll = False
            ...
    ```

3.  **Update Mechanism**: The integration implements a publisher/subscriber pattern for updates. Entities register a callback function (`self.sync_callback`) with a publisher upon being added to Home Assistant. This callback is triggered when new data arrives from the device via a websocket connection, which then updates the entity's state in Home Assistant. This is a classic push-based architecture.
    ```python
    // homeassistant/components/devolo_home_control/entity.py
    async def async_added_to_hass(self) -> None:
        """Call when entity is added to hass."""
        ...
        self.subscriber = Subscriber(
            self.device_info["name"], callback=self.sync_callback
        )
        self._homecontrol.publisher.register(
            self._device_instance.uid, self.subscriber, self.sync_callback
        )
    ...
    def _sync(self, message: tuple) -> None:
        """Update the state."""
        ...
        self.schedule_update_ha_state()
    ```

Since the integration does not poll, there is no polling interval to configure, making the `appropriate-polling` rule inapplicable.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 18:57:31 using gemini-2.5-pro-preview-06-05. Prompt tokens: 13443, Output tokens: 697, Total tokens: 16141._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
