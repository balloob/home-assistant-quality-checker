# devolo_home_control: config-flow

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [devolo_home_control](https://www.home-assistant.io/integrations/devolo_home_control/) |
| Rule   | [config-flow](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/config-flow)                                                     |
| Status | **done**                                                                 |

## Overview

The `config-flow` rule applies to the `devolo_home_control` integration, as it is a standard hub-based integration that is not exempt under ADR-0010.

The integration fully complies with this rule. It has a complete and robust implementation of the configuration flow, allowing users to set it up entirely through the Home Assistant UI.

The compliance is demonstrated by the following:

1.  **Manifest Declaration**: The `manifest.json` file correctly declares support for the configuration flow by setting `"config_flow": true`.

2.  **Config Flow Implementation**: The integration includes a `config_flow.py` file with a `DevoloHomeControlFlowHandler` class that handles multiple setup scenarios:
    *   **User-initiated setup (`async_step_user`)**: A standard flow is provided for users to manually add the integration, prompting for a username and password.
    *   **Zeroconf discovery (`async_step_zeroconf`)**: The integration can be discovered on the network, simplifying the setup process for the user.
    *   **Reauthentication (`async_step_reauth`)**: A reauth flow is implemented to handle cases where credentials become invalid, guiding the user to update them without removing the integration.

3.  **User-Friendly Text and Descriptions**: The `strings.json` file is well-structured and provides clear, user-friendly text for the configuration flow. Crucially, it uses the `data_description` key to give context to the required `username` and `password` fields, as recommended by the rule for a better user experience.
    ```json
    "data_description": {
      "username": "Email address you used to register the central unit at mydevolo.",
      "password": "Password of your mydevolo account."
    }
    ```

4.  **Correct Setup from Config Entry**: The `__init__.py` file correctly implements `async_setup_entry`, which uses the data stored in the `ConfigEntry` by the config flow to initialize the connection to the devolo Home Control hub.

The implementation is a textbook example of following the config flow pattern, covering setup, discovery, and reauthentication, while providing clear instructions to the user.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 18:58:19 using gemini-2.5-pro-preview-06-05. Prompt tokens: 13583, Output tokens: 611, Total tokens: 15680._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
