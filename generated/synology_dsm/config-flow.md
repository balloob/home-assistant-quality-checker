```markdown
# synology_dsm: config-flow

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [config-flow](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/config-flow)                                                     |
| Status | **done**                                       |
| Reason |                                                                          |

## Overview

The `config-flow` rule requires integrations to be configurable via the Home Assistant user interface using a config flow. This ensures a consistent and user-friendly setup experience. The rule applies to the `synology_dsm` integration as it requires user input for connecting to a Synology NAS device.

Based on the provided code, the `synology_dsm` integration fully complies with the `config-flow` rule:

1.  **Config Flow Implementation:** The integration has a `config_flow.py` file containing the `SynologyDSMFlowHandler` class, which inherits from `ConfigFlow`, as required. This is confirmed by the presence of the file and the class definition:
    ```python
    # homeassistant/components/synology_dsm/config_flow.py
    class SynologyDSMFlowHandler(ConfigFlow, domain=DOMAIN):
        """Handle a config flow."""
        # ...
    ```
2.  **Manifest Configuration:** The `manifest.json` file correctly sets `"config_flow": true,` indicating that the integration supports UI configuration:
    ```json
    // homeassistant/components/synology_dsm/manifest.json
    {
      "domain": "synology_dsm",
      "name": "Synology DSM",
      // ...
      "config_flow": true,
      // ...
    }
    ```
3.  **Standard Steps and Error Handling:** The `config_flow.py` implements the standard `async_step_user` for manual configuration, handles input validation in `async_validate_input_create_entry`, and uses `self.async_show_form` to present forms with errors. It also includes steps for two-step authentication (`async_step_2sa`) and optional backup configuration (`async_step_backup_share`), guiding the user through the setup.
4.  **Discovery:** The integration implements `async_step_zeroconf` and `async_step_ssdp` to handle automatic discovery of Synology devices, providing a more convenient setup for users.
5.  **Reauthentication Flow:** An `async_step_reauth` and `async_step_reauth_confirm` are implemented to handle cases where authentication fails, prompting the user to re-enter credentials.
6.  **Options Flow:** The integration defines an `async_get_options_flow` method returning a `SynologyDSMOptionsFlowHandler`, which implements `async_step_init`. This allows users to configure integration-specific options via the UI after the initial setup, such as snapshot quality and backup location, as seen in `homeassistant/components/synology_dsm/config_flow.py`.
7.  **Configuration Storage:** Configuration data like host, port, username, password, SSL settings, and MAC address are stored in `ConfigEntry.data`. User-configurable options like snapshot quality, backup share, and backup path are correctly stored in `ConfigEntry.options`, as demonstrated in `async_validate_input_create_entry` and `SynologyDSMOptionsFlowHandler.async_step_init`.
8.  **Localization and Selectors:** The integration utilizes `strings.json` for user-facing text, supporting localization. It also uses selectors like `SelectSelector` in the backup configuration steps for better user experience, as seen in `config_flow.py` and `strings.json`.

All core requirements of the `config-flow` rule are met by the `synology_dsm` integration.

## Suggestions

No suggestions needed. The integration fully complies with the `config-flow` rule.
```

_Created at 2025-05-25 11:46:27. Prompt tokens: 39791, Output tokens: 906, Total tokens: 42174_
