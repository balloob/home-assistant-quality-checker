# devolo_home_control: entity-event-setup

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [devolo_home_control](https://www.home-assistant.io/integrations/devolo_home_control/) |
| Rule   | [entity-event-setup](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-event-setup)                                                     |
| Status | **done**                                                                 |

## Overview

The `entity-event-setup` rule applies to this integration because its entities subscribe to real-time push updates from the devolo Home Control gateway to update their state. The `iot_class` is `local_push`, which confirms this event-driven architecture.

The integration correctly follows this rule by managing event subscriptions within the appropriate entity lifecycle methods.

All entities in this integration inherit from the `DevoloDeviceEntity` base class defined in `homeassistant/components/devolo_home_control/entity.py`. This class correctly implements the subscription and unsubscription logic:

1.  **Subscription:** In `async_added_to_hass`, the entity subscribes to updates from the underlying API's publisher. This ensures the entity is fully initialized in Home Assistant before it starts receiving events.

    ```python
    # homeassistant/components/devolo_home_control/entity.py
    async def async_added_to_hass(self) -> None:
        """Call when entity is added to hass."""
        assert self.device_info
        assert self.device_info["name"]  # The name was set on entity creation
        self.subscriber = Subscriber(
            self.device_info["name"], callback=self.sync_callback
        )
        self._homecontrol.publisher.register(
            self._device_instance.uid, self.subscriber, self.sync_callback
        )
    ```

2.  **Unsubscription:** In `async_will_remove_from_hass`, the entity unsubscribes from the publisher. This is crucial for preventing memory leaks when the entity is removed from Home Assistant.

    ```python
    # homeassistant/components/devolo_home_control/entity.py
    async def async_will_remove_from_hass(self) -> None:
        """Call when entity is removed or disabled."""
        self._homecontrol.publisher.unregister(
            self._device_instance.uid, self.subscriber
        )
    ```

This implementation perfectly aligns with the pattern described in the rule documentation, ensuring robust and leak-free event handling for all entities within the `devolo_home_control` integration.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 18:58:44 using gemini-2.5-pro-preview-06-05. Prompt tokens: 13458, Output tokens: 612, Total tokens: 15910._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
