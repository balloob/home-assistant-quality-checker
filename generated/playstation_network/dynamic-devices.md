# playstation_network: dynamic-devices

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [playstation_network](https://www.home-assistant.io/integrations/playstation_network/) |
| Rule   | [dynamic-devices](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/dynamic-devices)                                                     |
| Status | **done**                                                                 |

## Overview

The `dynamic-devices` rule applies to this integration because a single PlayStation Network account can be associated with multiple consoles (PS5, PS4, etc.), which are treated as devices within Home Assistant. A user may acquire a new console after the initial setup of the integration, and it should be automatically discovered and added to Home Assistant.

The `playstation_network` integration correctly implements this dynamic device addition for its media player entities.

The implementation can be found in `homeassistant/components/playstation_network/media_player.py`. It follows the recommended pattern almost exactly:

1.  **Tracking Known Devices:** In `async_setup_entry`, a set `devices_added: set[PlatformType] = set()` is initialized to keep track of platforms for which entities have already been created.

2.  **Discovery Function:** A callback function, `add_entities`, is defined. This function is responsible for checking for new devices.

3.  **Detecting New Devices:** Inside `add_entities`, the code calculates new devices by comparing the currently active platforms from the coordinator with the set of known devices:
    ```python
    new_platforms = set(coordinator.data.active_sessions.keys()) - devices_added
    ```

4.  **Adding New Entities:** If `new_platforms` is not empty, it calls `async_add_entities` to create new `PsnMediaPlayerEntity` instances for each new platform.

5.  **Listening for Updates:** The `add_entities` function is registered as a listener to the coordinator, ensuring it runs after every data refresh:
    ```python
    remove_listener = coordinator.async_add_listener(add_entities)
    ```

This ensures that if a user signs into a new console for the first time, it will appear in the `active_sessions` data, be detected as a new device, and have a corresponding media player entity created automatically without any user intervention.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 19:07:47 using gemini-2.5-pro. Prompt tokens: 9621, Output tokens: 536, Total tokens: 12517._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
