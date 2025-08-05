# bsblan: reauthentication-flow

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [bsblan](https://www.home-assistant.io/integrations/bsblan/) |
| Rule   | [reauthentication-flow](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/reauthentication-flow)                                                     |
| Status | **done**                                                                 |

## Overview

The `reauthentication-flow` rule applies to this integration because it uses authentication (passkey, username, and password) to communicate with the BSB-Lan device. If these credentials become invalid, Home Assistant should provide a way for the user to update them without deleting and re-adding the integration.

The `bsblan` integration correctly and fully implements the reauthentication flow.

1.  **Triggering Reauthentication**: In `coordinator.py`, the `_async_update_data` method correctly handles authentication errors from the `python-bsblan` library. When a `BSBLANAuthError` is caught, it raises a `ConfigEntryAuthFailed` exception, which signals to Home Assistant that a reauthentication flow is required.

    ```python
    # homeassistant/components/bsblan/coordinator.py
    class BSBLanUpdateCoordinator(DataUpdateCoordinator[BSBLanCoordinatorData]):
        # ...
        async def _async_update_data(self) -> BSBLanCoordinatorData:
            try:
                # ...
            except BSBLANAuthError as err:
                raise ConfigEntryAuthFailed(
                    "Authentication failed for BSB-Lan device"
                ) from err
            # ...
    ```

2.  **Handling the Reauthentication Flow**: The `config_flow.py` file implements the necessary steps to handle the reauthentication request from Home Assistant.
    -   `async_step_reauth`: This method is present and correctly initiates the reauthentication process by forwarding to `async_step_reauth_confirm`.
    -   `async_step_reauth_confirm`: This method handles the user interaction.
        -   It shows a form to the user, pre-filling existing credentials (except the password, which is standard security practice).
        -   When the user submits new credentials, it combines them with the existing configuration data.
        -   It attempts to validate the new credentials by calling `_get_bsblan_info`.
        -   If validation fails due to an authentication error (`BSBLANAuthError`), it shows the form again with an `invalid_auth` error.
        -   If validation succeeds, it updates the configuration entry with the new data and reloads the integration using `self.async_update_reload_and_abort`.

    ```python
    # homeassistant/components/bsblan/config_flow.py
    class BSBLANFlowHandler(ConfigFlow, domain=DOMAIN):
        # ...
        async def async_step_reauth(
            self, entry_data: Mapping[str, Any]
        ) -> ConfigFlowResult:
            """Handle reauth flow."""
            return await self.async_step_reauth_confirm()

        async def async_step_reauth_confirm(
            self, user_input: dict[str, Any] | None = None
        ) -> ConfigFlowResult:
            # ... (shows form if user_input is None)

            # ... (combines existing and new data)
            
            try:
                await self._get_bsblan_info(raise_on_progress=False, is_reauth=True)
            except BSBLANAuthError:
                return self.async_show_form(
                    # ... shows form again with "invalid_auth" error
                )
            except BSBLANError:
                return self.async_show_form(
                    # ... shows form again with "cannot_connect" error
                )

            # Update the config entry with the new merged data
            return self.async_update_reload_and_abort(
                existing_entry, data=config_data, reason="reauth_successful"
            )
    ```

This implementation provides a seamless user experience for updating credentials and fully complies with the rule.

## Suggestions

No suggestions needed.

---

_Created at 2025-08-04 09:07:38 using gemini-2.5-pro. Prompt tokens: 11516, Output tokens: 960, Total tokens: 14313._

_Report based on [`0ab5a05`](https://github.com/home-assistant/core/tree/0ab5a05a1f6e667e6da3771cfc802aa51388bbbe)._

_AI can be wrong. Always verify the report and the code against the rule._
