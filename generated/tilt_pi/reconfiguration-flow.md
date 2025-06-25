# tilt_pi: reconfiguration-flow

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [tilt_pi](https://www.home-assistant.io/integrations/tilt_pi/) |
| Rule   | [reconfiguration-flow](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/reconfiguration-flow)                                                     |
| Status | **todo**                                                                 |

## Overview

The `reconfiguration-flow` rule applies to this integration because it has a configuration flow (`"config_flow": true` in `manifest.json`) that requires user-provided settings—specifically, the URL of the Tilt Pi instance. This URL, which contains the host and port, might change if the user moves their Tilt Pi device to a new network address.

The integration currently does not follow this rule. The `config_flow.py` file defines a `TiltPiConfigFlow` class that only implements the `async_step_user` method for initial setup. It is missing the required `async_step_reconfigure` method.

Without a reconfiguration flow, if a user's Tilt Pi URL changes, their only option is to delete the integration from Home Assistant and re-add it with the new URL. This is a poor user experience that the reconfiguration flow is designed to prevent.

## Suggestions

To comply with the rule, you need to implement the `async_step_reconfigure` method in the `TiltPiConfigFlow` class within `homeassistant/components/tilt_pi/config_flow.py`.

This method will be triggered when a user clicks "RECONFIGURE" on the integration's card. It should present a form, pre-filled with the current URL, allow the user to enter a new one, validate it, and then update the existing configuration entry.

Here is a suggested implementation for the `async_step_reconfigure` method. It reuses the existing `_check_connection` helper for validation.

```python
# In homeassistant/components/tilt_pi/config_flow.py
# Add this method inside the TiltPiConfigFlow class

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a reconfiguration flow."""
        entry = self.config_entry
        assert entry

        errors: dict[str, str] = {}
        if user_input is not None:
            url = URL(user_input[CONF_URL])
            if (host := url.host) is None:
                errors[CONF_URL] = "invalid_host"
            else:
                # Prevent reconfiguring to a host that is already configured in another entry
                if host != entry.data.get(CONF_HOST):
                    self._async_abort_entries_match({CONF_HOST: host})

                port = url.port
                assert port
                error = await self._check_connection(host=host, port=port)
                if error:
                    errors["base"] = error
                else:
                    return self.async_update_reload_and_abort(
                        entry,
                        data={
                            CONF_HOST: host,
                            CONF_PORT: port,
                        },
                    )

        # Pre-fill the form with the current URL
        current_url = f"http://{entry.data[CONF_HOST]}:{entry.data[CONF_PORT]}"

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {vol.Required(CONF_URL, default=current_url): str}
            ),
            errors=errors,
        )
```

By adding this method, you provide a seamless way for users to update their Tilt Pi connection details, improving the integration's usability and fulfilling the requirements of the `reconfiguration-flow` rule.

---

_Created at 2025-06-25 18:56:07 using gemini-2.5-pro-preview-06-05. Prompt tokens: 4627, Output tokens: 878, Total tokens: 10201._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
