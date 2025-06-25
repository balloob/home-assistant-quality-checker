# devolo_home_control: test-before-configure

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [devolo_home_control](https://www.home-assistant.io/integrations/devolo_home_control/) |
| Rule   | [test-before-configure](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/test-before-configure)                                                     |
| Status | **done**                                                                 |

## Overview

The `test-before-configure` rule applies to this integration because it connects to the `mydevolo` cloud service to authenticate and discover gateways, which requires user-provided credentials. The integration must validate these credentials before creating the configuration entry.

The `devolo_home_control` integration correctly follows this rule. The config flow logic, found in `homeassistant/components/devolo_home_control/config_flow.py`, validates the user's credentials before finalizing the setup.

Specifically, the `async_step_user`, `async_step_zeroconf_confirm`, and `async_step_reauth_confirm` methods all call the internal `_connect_mydevolo` helper method. This method performs the validation.

```python
# homeassistant/components/devolo_home_control/config_flow.py

async def async_step_user(
    self, user_input: dict[str, Any] | None = None
) -> ConfigFlowResult:
    """Handle a flow initiated by the user."""
    if user_input is None:
        return self._show_form(step_id="user")
    try:
        return await self._connect_mydevolo(user_input)
    except CredentialsInvalid:
        return self._show_form(step_id="user", errors={"base": "invalid_auth"})

async def _connect_mydevolo(self, user_input: dict[str, Any]) -> ConfigFlowResult:
    """Connect to mydevolo."""
    mydevolo = configure_mydevolo(conf=user_input)
    credentials_valid = await self.hass.async_add_executor_job(
        mydevolo.credentials_valid
    )
    if not credentials_valid:
        raise CredentialsInvalid
    # ... on success, proceed to create the entry
    ...
    return self.async_create_entry(...)
```

As shown above:
1.  The `_connect_mydevolo` function calls `mydevolo.credentials_valid()`, which tests the connection and authentication with the cloud service.
2.  If the credentials are not valid, a `CredentialsInvalid` exception is raised.
3.  The calling step (e.g., `async_step_user`) catches this exception and re-displays the form with an `invalid_auth` error, allowing the user to correct their input.
4.  The configuration entry is only created via `self.async_create_entry` if the `mydevolo.credentials_valid()` check passes successfully.

This implementation perfectly aligns with the requirements of the `test-before-configure` rule.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 19:00:37 using gemini-2.5-pro-preview-06-05. Prompt tokens: 13499, Output tokens: 734, Total tokens: 16674._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
