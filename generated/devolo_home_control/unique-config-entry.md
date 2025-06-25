# devolo_home_control: unique-config-entry

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [devolo_home_control](https://www.home-assistant.io/integrations/devolo_home_control/) |
| Rule   | [unique-config-entry](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/unique-config-entry)                                                     |
| Status | **done**                                                                 |

## Overview

The `unique-config-entry` rule applies to this integration as it uses a config flow (`"config_flow": true` in `manifest.json`) for setup. The purpose of this rule is to prevent a user from accidentally setting up the same device or service multiple times.

The `devolo_home_control` integration correctly implements this rule by using a unique identifier for each configuration entry. This prevents the same mydevolo account from being added more than once.

The implementation can be found in `homeassistant/components/devolo_home_control/config_flow.py`. Inside the `_connect_mydevolo` method, the integration performs the following steps:

1.  It authenticates with the user's mydevolo credentials.
2.  It fetches a unique `uuid` for the mydevolo account:
    ```python
    # homeassistant/components/devolo_home_control/config_flow.py:126
    uuid = await self.hass.async_add_executor_job(mydevolo.uuid)
    ```
3.  For a new configuration, it sets this `uuid` as the unique ID for the config entry and then aborts if an entry with that ID already exists:
    ```python
    # homeassistant/components/devolo_home_control/config_flow.py:129-130
    await self.async_set_unique_id(uuid)
    self._abort_if_unique_id_configured()
    ```

This pattern perfectly matches the recommended implementation described in the rule documentation, ensuring that each devolo account can only be configured once in Home Assistant.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 19:01:33 using gemini-2.5-pro-preview-06-05. Prompt tokens: 13916, Output tokens: 505, Total tokens: 16011._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
