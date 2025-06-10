# pi_hole: config-flow

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [pi_hole](https://www.home-assistant.io/integrations/pi_hole/) |
| Rule   | [config-flow](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/config-flow)                                                     |
| Status | **todo**                                                                 |
| Reason | N/A                                                                      |

## Overview

The `config-flow` rule mandates that integrations must be configurable through the Home Assistant UI using a config flow. This includes having a `config_flow.py`, setting `config_flow: true` in `manifest.json`, using `strings.json` for all UI text, validating user input, providing contextual help via `data_description` in `strings.json`, and correctly storing configuration in `ConfigEntry.data` and `ConfigEntry.options`.

The `pi_hole` integration is not exempt from this rule as per ADR-0010.

The integration partially follows the rule:
*   `manifest.json` correctly sets `"config_flow": true`.
*   A `config_flow.py` (class `PiHoleFlowHandler`) is implemented, handling user input for initial setup (`async_step_user`), API key input (`async_step_api_key`), and re-authentication (`async_step_reauth`, `async_step_reauth_confirm`).
*   It uses `vol.Schema` for input validation (e.g., `CONF_PORT` as `vol.Coerce(int)`).
*   It uses `strings.json` for UI labels and error messages (e.g., `config.step.user.data.host`, `config.error.cannot_connect`).
*   Connection attempts and error handling (e.g., `cannot_connect`, `invalid_auth`) are present in the config flow.

However, the integration does not fully comply with the rule due to the following:

1.  **Missing `data_description` in `strings.json`**:
    The rule states, "use `data_description` in the `strings.json` to give context about the input field." The `pi_hole/strings.json` file defines labels for input fields under `data` but lacks the `data_description` object for any of its config flow steps (`user`, `api_key`, `reauth_confirm`). This means users do not get detailed contextual help for each field within the UI.

    For example, in `strings.json` under `config.step.user`:
    ```json
    {
      "config": {
        "step": {
          "user": {
            "data": { // Labels exist
              "host": "[%key:common::config_flow::data::host%]",
              "port": "[%key:common::config_flow::data::port%]",
              // ...
            }
            // "data_description": { ... } is missing here
          }
        }
      }
    }
    ```

2.  **Incorrect storage of non-connection settings and lack of Options Flow**:
    The rule specifies: "The integration should store all configuration in the `ConfigEntry.data` field, while all settings that are not needed for the connection to be made should be stored in the `ConfigEntry.options` field." ADR-0010, referenced by the rule, reinforces this and implies an options flow for managing such options.
    The `CONF_NAME` parameter (the user-defined name for the Pi-hole instance in Home Assistant) is not essential for establishing a connection to the Pi-hole device. Currently, `CONF_NAME` is collected in `config_flow.py` and stored in `ConfigEntry.data`:
    ```python
    # homeassistant/components/pi_hole/config_flow.py
    # In PiHoleFlowHandler.async_step_user
    # self._config is populated with user_input, including CONF_NAME
    # ...
    # return self.async_create_entry(
    #     title=user_input[CONF_NAME], data=self._config # self._config contains CONF_NAME
    # )
    ```
    This should be stored in `ConfigEntry.options`. Consequently, an options flow handler should be implemented to allow users to modify `CONF_NAME` (and potentially other future options) after the initial setup, which is currently not possible. The `pi_hole` integration does not have an `OptionsFlowHandler` or an `async_get_options_flow` method.

Due to these omissions, the integration is marked as **"todo"**.

## Suggestions

To make the `pi_hole` integration compliant with the `config-flow` rule:

1.  **Add `data_description` to `strings.json`**:
    Provide contextual descriptions for all input fields in the config flow UI. This improves user experience by clarifying the purpose and expected format of each field.

    Update `homeassistant/components/pi_hole/strings.json` for each relevant step. Example for the `user` step:
    ```json
    {
      "config": {
        "step": {
          "user": {
            "data": {
              "host": "[%key:common::config_flow::data::host%]",
              "port": "[%key:common::config_flow::data::port%]",
              "name": "[%key:common::config_flow::data::name%]",
              "location": "[%key:common::config_flow::data::location%]",
              "ssl": "[%key:common::config_flow::data::ssl%]",
              "verify_ssl": "[%key:common::config_flow::data::verify_ssl%]"
            },
            "data_description": {
              "host": "The hostname or IP address of your Pi-hole device (e.g., 'pi.hole' or '192.168.1.10').",
              "port": "The port number on which your Pi-hole admin interface is accessible (usually 80 for HTTP or 443 for HTTPS).",
              "name": "A unique name for this Pi-hole instance in Home Assistant.",
              "location": "The location of the Pi-hole admin interface (e.g., 'admin').",
              "ssl": "Enable if your Pi-hole is served over HTTPS.",
              "verify_ssl": "Enable to verify the SSL certificate if HTTPS is used. Disable for self-signed certificates."
            }
          }
        },
        "api_key": {
          "data": {
            "api_key": "[%key:common::config_flow::data::api_key%]"
          },
          "data_description": {
            "api_key": "Your Pi-hole API key. Found in Pi-hole admin interface: Settings > API / Web interface > Show API token."
          }
        },
        "reauth_confirm": {
          "title": "Reauthenticate Pi-hole",
          "description": "Please enter a new API key for Pi-hole at {host}/{location}",
          "data": {
            "api_key": "[%key:common::config_flow::data::api_key%]"
          },
          "data_description": {
            "api_key": "Your Pi-hole API key. Found in Pi-hole admin interface: Settings > API / Web interface > Show API token."
          }
        }
        // ... other sections
      }
      // ...
    }
    ```

2.  **Manage `CONF_NAME` via `ConfigEntry.options` and implement an Options Flow**:
    This aligns with the requirement that non-connection-critical settings are stored in `options` and are user-modifiable post-setup.

    *   **Modify `config_flow.py` (`PiHoleFlowHandler`)**:
        *   Adjust `async_step_user` (and `async_step_api_key` if `CONF_NAME` is re-confirmed or relevant there) to separate connection data from options.
        *   When calling `self.async_create_entry`, pass `CONF_NAME` in the `options` dictionary.
        Example snippet for `async_step_user` when creating the entry:
        ```python
        # In PiHoleFlowHandler.async_step_user
        # ... (after user_input is validated and self._config is being prepared)

        # Separate data and options
        entry_data = {
            CONF_HOST: f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}",
            CONF_LOCATION: user_input[CONF_LOCATION],
            CONF_SSL: user_input[CONF_SSL],
            CONF_VERIFY_SSL: user_input[CONF_VERIFY_SSL],
            # CONF_API_KEY will be added to this dict if/when collected
        }
        # If API key is part of self._config already (e.g. from reauth flow context)
        # or if it's collected in a different manner before this point, ensure it's in entry_data.
        # This example assumes API key might be added later or is handled by self._config elsewhere.

        entry_options = {
            CONF_NAME: user_input[CONF_NAME],
        }

        # Update self._config to reflect this separation or manage distinct dicts
        # For instance, if self._config is used by _async_try_connect:
        # self._config_data_for_connection = entry_data.copy()
        # self._config_options = entry_options.copy()

        # When creating the entry:
        # (Assuming self._config holds all necessary data for connection check and then final data dict)
        # Let's assume errors are checked and api_key is populated into self._config as needed.
        # The key is to split self._config before calling async_create_entry.
        
        # Simplified: If self._config already contains all fields including api_key:
        final_data = self._config.copy()
        final_options = {CONF_NAME: final_data.pop(CONF_NAME)} # Move CONF_NAME to options

        return self.async_create_entry(
            title=final_options[CONF_NAME], # Title can still be based on name
            data=final_data,
            options=final_options
        )
        ```
        *Note: The current structure of `self._config` in `PiHoleFlowHandler` would need careful refactoring to cleanly separate what goes into `data` versus `options` across different steps.*

    *   **Implement an Options Flow Handler in `config_flow.py`**:
        ```python
        # homeassistant/components/pi_hole/config_flow.py
        from homeassistant.config_entries import ConfigEntry, OptionsFlow
        from homeassistant.core import callback
        # ... other imports from const like DEFAULT_NAME

        # Add this to PiHoleFlowHandler or as a top-level function if preferred by style
        @staticmethod
        @callback
        def async_get_options_flow(config_entry: ConfigEntry) -> PiHoleOptionsFlowHandler:
            """Get the options flow for this handler."""
            return PiHoleOptionsFlowHandler(config_entry)

        class PiHoleOptionsFlowHandler(OptionsFlow):
            """Handle Pi-hole options."""

            def __init__(self, config_entry: ConfigEntry) -> None:
                """Initialize options flow."""
                self.config_entry = config_entry

            async def async_step_init(
                self, user_input: dict[str, Any] | None = None
            ) -> ConfigFlowResult:
                """Manage the Pi-hole options."""
                if user_input is not None:
                    # Update the config entry with new options
                    return self.async_create_entry(title="", data=user_input)

                # Populate form with current options
                current_name = self.config_entry.options.get(
                    CONF_NAME, self.config_entry.data.get(CONF_NAME, DEFAULT_NAME)
                )

                options_schema = vol.Schema(
                    {
                        vol.Required(CONF_NAME, default=current_name): str,
                        # Add other configurable options here in the future
                    }
                )

                return self.async_show_form(
                    step_id="init",
                    data_schema=options_schema,
                    # Add strings for options flow to strings.json if needed
                    # e.g., description_placeholders or errors
                )

        # Ensure PiHoleFlowHandler includes:
        # async_get_options_flow = async_get_options_flow
        ```
        (And ensure `strings.json` has an `options.step.init.data.name` and potentially `data_description` for options flow fields.)

    *   **Update `__init__.py` (`async_setup_entry`)**:
        Read `CONF_NAME` from `entry.options`, with a fallback to `entry.data` for backward compatibility with existing entries.
        ```python
        # homeassistant/components/pi_hole/__init__.py
        # In async_setup_entry function:
        # name = entry.data[CONF_NAME] # Old
        name = entry.options.get(CONF_NAME, entry.data.get(CONF_NAME, DEFAULT_NAME)) # New
        host = entry.data[CONF_HOST] # Connection parameters remain in data
        # ...
        ```

By implementing these changes, `pi_hole` will provide a more user-friendly setup experience with better contextual information and correctly manage its configuration data and options as per Home Assistant standards.

---

_Created at 2025-06-10 23:07:57. Prompt tokens: 10363, Output tokens: 3138, Total tokens: 19977._

_Report based on [`ab7f6c3`](https://github.com/home-assistant/core/tree/ab7f6c35287f43fe1207b3de4581b3bfabd49399)._

_AI can be wrong. Always verify the report and the code against the rule._
