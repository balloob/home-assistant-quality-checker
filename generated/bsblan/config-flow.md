# bsblan: config-flow

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [bsblan](https://www.home-assistant.io/integrations/bsblan/) |
| Rule   | [config-flow](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/config-flow)                                                     |
| Status | **done**                                       |

## Overview

The `config-flow` rule applies to the `bsblan` integration as it is a device integration that requires user-provided configuration (like host, port, and credentials) to connect to a device on the local network.

The integration fully complies with this rule.

1.  **Manifest Configuration**: The `manifest.json` file correctly enables the config flow by setting `"config_flow": true`.
2.  **Config Flow Implementation**: The integration includes a `config_flow.py` file with a robust `BSBLANFlowHandler` class. This class handles multiple setup scenarios:
    *   `async_step_user`: A standard flow for users to manually add the integration.
    *   `async_step_zeroconf`: A flow to handle automatic discovery of BSB-Lan devices on the network, providing a better user experience.
    *   `async_step_reauth`: A flow to handle re-authentication if credentials become invalid.
3.  **Input Validation**: The config flow validates the user's input by attempting to connect to the device in the `_validate_and_create` method. It correctly catches specific exceptions like `BSBLANAuthError` and `BSBLANError` to return user-friendly errors (`invalid_auth`, `cannot_connect`) to the UI.
4.  **User-Friendly Strings**: The `strings.json` file is well-structured and provides all necessary text for the config flow steps. Crucially, it includes a `data_description` block for the `user` step, which gives helpful context for each input field, as recommended by the rule for a better user experience.

    ```json
    // homeassistant/components/bsblan/strings.json
    "step": {
      "user": {
        "data": { ... },
        "data_description": {
          "host": "The hostname or IP address of your BSB-Lan device.",
          "port": "The port number of your BSB-Lan device.",
          "passkey": "The passkey for your BSB-Lan device.",
          "username": "The username for your BSB-Lan device.",
          "password": "The password for your BSB-Lan device."
        }
      }
    }
    ```
5.  **Configuration Storage**: Upon successful setup, the connection details are correctly stored in `ConfigEntry.data`, which is then used in `async_setup_entry` within `__init__.py` to initialize the integration.

The implementation is a great example of a complete and user-friendly config flow.

## Suggestions

No suggestions needed.

---

_Created at 2025-08-05 09:36:11 using gemini-2.5-pro. Prompt tokens: 11293, Output tokens: 681, Total tokens: 13823._

_Report based on [`ee9ff71`](https://github.com/home-assistant/core/tree/ee9ff717e0d36ca02bf52a242acd3a47359eae61)._

_AI can be wrong. Always verify the report and the code against the rule._
