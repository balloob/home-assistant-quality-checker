# devolo_home_control: common-modules

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [devolo_home_control](https://www.home-assistant.io/integrations/devolo_home_control/) |
| Rule   | [common-modules](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/common-modules)                                                     |
| Status | **done**                                                                 |

## Overview

The `common-modules` rule requires that common architectural patterns, such as base entities and data update coordinators, be placed in standardized files (`entity.py` and `coordinator.py`, respectively) to improve consistency and maintainability across integrations.

This rule applies to the `devolo_home_control` integration, and the integration correctly follows it.

1.  **Base Entity (`entity.py`):**
    The integration provides entities for multiple platforms (e.g., `switch`, `sensor`, `light`). To reduce code duplication, it correctly implements base entity classes in `homeassistant/components/devolo_home_control/entity.py`.
    -   `DevoloDeviceEntity` serves as the primary base class, handling common logic such as device info setup, availability, and subscribing to data updates via the `homecontrol.publisher`.
    -   `DevoloMultiLevelSwitchDeviceEntity` inherits from `DevoloDeviceEntity` and provides a further specialized base for entities like dimmers, covers, and thermostats.
    -   Platform-specific entities, such as `DevoloCoverDeviceEntity` in `cover.py`, properly inherit from these base classes:
        ```python
        # homeassistant/components/devolo_home_control/cover.py
        class DevoloCoverDeviceEntity(DevoloMultiLevelSwitchDeviceEntity, CoverEntity):
            """Representation of a cover device within devolo Home Control."""
        ```
    This demonstrates a correct and effective use of a common entity module.

2.  **Coordinator (`coordinator.py`):**
    The rule suggests placing a `DataUpdateCoordinator` in `coordinator.py`. This pattern is primarily for integrations that poll an API for data at regular intervals. However, the `devolo_home_control` integration is push-based, as indicated by its `iot_class` of `local_push`.

    Data updates are not polled; they are pushed from the device over a websocket and handled by a publisher/subscriber mechanism, implemented in `subscriber.py` and used within the `DevoloDeviceEntity` base class.

    ```python
    # homeassistant/components/devolo_home_control/entity.py
    async def async_added_to_hass(self) -> None:
        """Call when entity is added to hass."""
        # ...
        self._homecontrol.publisher.register(
            self._device_instance.uid, self.subscriber, self.sync_callback
        )
    ```

    Because the integration does not use the polling-based `DataUpdateCoordinator` pattern, the absence of a `coordinator.py` file is correct and appropriate for its architecture.

In summary, the integration correctly uses `entity.py` for its base entity classes and, due to its push-based nature, rightly omits the use of a `DataUpdateCoordinator`. Therefore, it fully complies with the `common-modules` rule.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 18:57:57 using gemini-2.5-pro-preview-06-05. Prompt tokens: 13204, Output tokens: 763, Total tokens: 15647._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
