```markdown
# synology_dsm: reconfiguration-flow

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [reconfiguration-flow](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/reconfiguration-flow)                                                     |
| Status | **todo**                                                                 |

## Overview

The `reconfiguration-flow` rule requires integrations with configuration settings to implement a dedicated flow to allow users to update these settings without removing and re-adding the integration. This is particularly useful when device credentials, hostnames, or IP addresses change.

This rule applies to the `synology_dsm` integration because its initial configuration flow (`async_step_user` in `homeassistant/components/synology_dsm/config_flow.py`) requires essential connection parameters like host, port, username, password, SSL options, and potentially 2FA tokens. These are exactly the types of settings that might need to be updated if the NAS configuration changes or its network location changes.

However, the provided code for the `synology_dsm` integration **does not** implement the required `async_step_reconfigure` method within its `SynologyDSMFlowHandler` class in `config_flow.py`.

While the integration does have an `async_step_reauth` flow to handle authentication failures and an `OptionsFlow` for settings like snapshot quality and backup location, these serve different purposes than a general reconfiguration flow intended for the initial connection details (host, port, username, password). The absence of `async_step_reconfigure` means a user whose NAS IP changes (without immediate auth failure) or who simply wishes to update the connection parameters must remove and re-add the integration entirely.

Therefore, the integration currently does not fully comply with the `reconfiguration-flow` rule.

## Suggestions

To comply with the `reconfiguration-flow` rule, the `synology_dsm` integration needs to implement the `async_step_reconfigure` method in `homeassistant/components/synology_dsm/config_flow.py`.

1.  **Add `async_step_reconfigure`:** Define `async_step_reconfigure` within the `SynologyDSMFlowHandler` class. This method should accept optional `user_input` and return a `ConfigFlowResult`.
2.  **Define Schema:** The reconfigure flow should likely prompt for the same core connection parameters as the initial `user` step (host, port, ssl, verify_ssl, username, password). Reuse or adapt the `_ordered_shared_schema` and possibly handle OTP input similar to `async_step_2sa`.
3.  **Validate Input:** Inside `async_step_reconfigure`, if `user_input` is provided, attempt to connect to the Synology DSM using the new details, similar to the validation logic in `async_validate_input_create_entry`.
4.  **Handle Validation Errors:** If the connection fails or validation errors occur (e.g., `cannot_connect`, `invalid_auth`), return the form again using `self.async_show_form`, providing relevant error messages.
5.  **Update Config Entry:** If validation is successful, call `self.async_update_reload_and_abort` with the updated configuration data. This updates the existing config entry and triggers a reload of the integration with the new settings. The reason can be set to `"reconfigure_successful"`.
6.  **Initial Form Display:** If `user_input` is `None`, show the configuration form using `self.async_show_form(step_id="reconfigure", data_schema=...)`. Pre-fill the form with the *current* configuration data from `self.init_data` (which is available in reconfigure flows) to make editing easier for the user.

Refer to the example implementation provided in the rule documentation for guidance on the structure and logic of `async_step_reconfigure`. The validation logic from `async_validate_input_create_entry` is a good starting point for connecting and verifying the new credentials/host.

By implementing `async_step_reconfigure`, the Synology DSM integration will allow users to easily update connection settings via the Home Assistant UI without needing to delete and re-add the integration, fulfilling the rule requirement.

```python
# homeassistant/components/synology_dsm/config_flow.py

# Add this method to SynologyDSMFlowHandler class
    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of the integration."""
        errors: dict[str, str] = {}
        config_data = self.init_data # Access current config data

        if user_input:
            # Merge user input with existing data, allowing overrides
            updated_data = {**config_data, **user_input}
            host = updated_data[CONF_HOST]
            port = updated_data.get(CONF_PORT) or (DEFAULT_PORT_SSL if updated_data.get(CONF_SSL) else DEFAULT_PORT)
            username = updated_data[CONF_USERNAME]
            password = updated_data[CONF_PASSWORD]
            use_ssl = updated_data.get(CONF_SSL, DEFAULT_USE_SSL)
            verify_ssl = updated_data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL)
            otp_code = updated_data.get(CONF_OTP_CODE) # Handle OTP if required

            session = async_get_clientsession(self.hass, verify_ssl)
            api = SynologyDSM(
                session, host, port, username, password, use_ssl, timeout=DEFAULT_TIMEOUT
            )

            try:
                # Validate connection and get serial (unique ID)
                serial = await _login_and_fetch_syno_info(api, otp_code)
                # Optionally, check if the serial matches the existing unique ID
                # This prevents reconfiguring to a different NAS
                if self.context.get("unique_id") and self.context["unique_id"] != serial:
                     errors["base"] = "wrong_account" # Or similar error key
                else:
                    # Successful validation, update config entry
                    # Note: device_token might need to be handled if 2SA is used
                    updated_entry_data = {
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_SSL: use_ssl,
                        CONF_VERIFY_SSL: verify_ssl,
                        CONF_USERNAME: username,
                        CONF_PASSWORD: password,
                        CONF_MAC: api.network.macs, # Update MACs if needed
                    }
                    if otp_code:
                       updated_entry_data[CONF_DEVICE_TOKEN] = api.device_token # Update token

                    # Preserve existing options and any other config data not in the form
                    final_data = {**config_data, **updated_entry_data}
                    final_options = dict(self.options) # Options usually handled separately, but example shows merging

                    return self.async_update_reload_and_abort(
                         self.config_entry,
                         data_updates=final_data,
                         # options_updates=final_options, # Update options if needed here
                         reason="reconfigure_successful",
                    )

            except SynologyDSMLogin2SARequiredException:
                 # If reconfigure requires 2SA, maybe transition to a 2SA step
                 # Store updated_data and ask for OTP
                 self.saved_user_input = updated_data
                 return await self.async_step_2sa(updated_data, {"base": "otp_required_during_reconfig"}) # Need a new error key and handle flow transition
            except SynologyDSMLogin2SAFailedException:
                errors[CONF_OTP_CODE] = "otp_failed"
                user_input[CONF_OTP_CODE] = None # Clear OTP field
            except SynologyDSMLoginInvalidException:
                errors[CONF_USERNAME] = "invalid_auth"
            except SynologyDSMRequestException:
                errors[CONF_HOST] = "cannot_connect"
            except SynologyDSMException:
                errors["base"] = "unknown"
            except InvalidData:
                errors["base"] = "missing_data"

        # Show the form (either initially or on error)
        # Pre-fill form with current config data or failed user input
        form_data = user_input if errors else config_data

        # Define schema similar to user step but without CONF_HOST initially
        reconfigure_schema = vol.Schema({
             vol.Required(CONF_HOST, default=form_data.get(CONF_HOST)): str,
             vol.Required(CONF_USERNAME, default=form_data.get(CONF_USERNAME)): str,
             vol.Required(CONF_PASSWORD, default=form_data.get(CONF_PASSWORD)): str,
             vol.Optional(CONF_PORT, default=form_data.get(CONF_PORT)): str, # Keep optional with default
             vol.Optional(CONF_SSL, default=form_data.get(CONF_SSL, DEFAULT_USE_SSL)): bool,
             vol.Optional(CONF_VERIFY_SSL, default=form_data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL)): bool,
             # Add OTP field if needed, maybe conditionally based on API info?
             # vol.Optional(CONF_OTP_CODE): str,
        })

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=reconfigure_schema,
            errors=errors,
            # Placeholders might be useful
        )

# Need to adjust async_step_2sa or add a new step to handle 2SA specifically triggered by reconfigure
# Need to ensure async_validate_input_create_entry is not called directly by reconfigure flow


```
**Note:** The suggested code is a template. It needs careful implementation regarding error handling (especially 2FA during reconfigure), state management (`saved_user_input`), and ensuring it updates the correct parts of the config entry data while preserving others. The validation logic from `_login_and_fetch_syno_info` is a good candidate to reuse. Handling the MAC address update (`api.network.macs`) is also important if the host changes.

_Created at 2025-05-25 11:52:15. Prompt tokens: 39973, Output tokens: 2379, Total tokens: 43296_
