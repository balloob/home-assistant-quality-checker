# playstation_network: reconfiguration-flow

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [playstation_network](https://www.home-assistant.io/integrations/playstation_network/) |
| Rule   | [reconfiguration-flow](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/reconfiguration-flow)                                                     |
| Status | **todo**                                                                 |

## Overview

The `reconfiguration-flow` rule applies to this integration because it is configured with an `npsso` token which can expire or be changed by the user. A reconfiguration flow would allow the user to proactively update this token from the Home Assistant UI without having to delete and re-add the integration.

Currently, the `playstation_network` integration does not follow this rule. The `config_flow.py` file is missing an `async_step_reconfigure` method in the `PlaystationNetworkConfigFlow` class.

While the integration does implement a re-authentication flow (`async_step_reauth` and `async_step_reauth_confirm`), this is only triggered by the system when an authentication error (e.g., `ConfigEntryAuthFailed`) is raised. The rule requires a user-initiated flow, which is enabled by implementing `async_step_reconfigure`, allowing users to open the integration's configuration and click "Reconfigure" at any time.

## Suggestions

To make the integration compliant, you should add an `async_step_reconfigure` method to the `PlaystationNetworkConfigFlow` class in `homeassistant/components/playstation_network/config_flow.py`. The logic for this new method can be largely adapted from the existing `async_step_reauth_confirm` method.

1.  **Add the `async_step_reconfigure` method:**
    This method will handle the user-initiated reconfiguration. It will show a form to input the new `npsso` token, validate it, ensure it's for the same account, and then update the configuration entry.

    ```python
    # In homeassistant/components/playstation_network/config_flow.py

    class PlaystationNetworkConfigFlow(ConfigFlow, domain=DOMAIN):
        """Handle a config flow for Playstation Network."""

        # ... (keep existing async_step_user and async_step_reauth methods)

        async def async_step_reconfigure(
            self, user_input: dict[str, Any] | None = None
        ) -> ConfigFlowResult:
            """Handle a reconfiguration flow initialized by the user."""
            entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
            assert entry

            errors: dict[str, str] = {}

            if user_input:
                try:
                    npsso = parse_npsso_token(user_input[CONF_NPSSO])
                    psn = PlaystationNetwork(self.hass, npsso)
                    user: User = await psn.get_user()
                except PSNAWPAuthenticationError:
                    errors["base"] = "invalid_auth"
                except (PSNAWPNotFoundError, PSNAWPInvalidTokenError):
                    errors["base"] = "invalid_account"
                except PSNAWPError:
                    errors["base"] = "cannot_connect"
                except Exception:
                    _LOGGER.exception("Unexpected exception")
                    errors["base"] = "unknown"
                else:
                    if user.account_id != entry.unique_id:
                        return self.async_abort(
                            reason="unique_id_mismatch",
                            description_placeholders={
                                "wrong_account": user.online_id,
                                CONF_NAME: entry.title,
                            },
                        )

                    return self.async_update_reload_and_abort(
                        entry,
                        data={**entry.data, CONF_NPSSO: npsso},
                        reason="reconfigure_successful"
                    )

            return self.async_show_form(
                step_id="reconfigure",
                data_schema=self.add_suggested_values_to_schema(
                    data_schema=STEP_USER_DATA_SCHEMA, suggested_values=entry.data
                ),
                errors=errors,
                description_placeholders={
                    "npsso_link": NPSSO_LINK,
                    "psn_link": PSN_LINK,
                },
            )

        # ... (rest of the class)
    ```

2.  **Update `strings.json`:**
    To support the new `reconfigure` step in the UI, you'll need to add translations to `homeassistant/components/playstation_network/strings.json`. You can add a new `reconfigure` object within the `config.step` section, similar to `reauth_confirm`.

    ```json
    // In homeassistant/components/playstation_network/strings.json
    {
      "config": {
        "step": {
          "user": { ... },
          "reconfigure": {
            "title": "Reconfigure {name} for PlayStation Network",
            "description": "To update your NPSSO token, log in to your [PlayStation account]({psn_link}) first. Then [click here]({npsso_link}) to retrieve the token.",
            "data": {
              "npsso": "[%key:component::playstation_network::config::step::user::data::npsso%]"
            },
            "data_description": {
              "npsso": "[%key:component::playstation_network::config::step::user::data_description::npsso%]"
            }
          },
          "reauth_confirm": { ... }
        },
        ...
      },
      ...
    }
    ```

3.  **Note on `async_update_reload_and_abort`:**
    The existing `async_step_reauth_confirm` method uses a deprecated `data_updates` parameter. The suggested code above uses the current `data` parameter. It is recommended to also update the `async_step_reauth_confirm` method to use `data` for consistency and to avoid deprecation warnings.

    **Change from:**
    ```python
    return self.async_update_reload_and_abort(
        entry,
        data_updates={CONF_NPSSO: npsso},
    )
    ```
    **Change to:**
    ```python
    return self.async_update_reload_and_abort(
        entry,
        data={**entry.data, CONF_NPSSO: npsso},
    )
    ```

---

_Created at 2025-06-25 19:08:59 using gemini-2.5-pro. Prompt tokens: 9956, Output tokens: 1530, Total tokens: 18104._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
