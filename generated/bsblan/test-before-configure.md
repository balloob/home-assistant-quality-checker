# bsblan: test-before-configure

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [bsblan](https://www.home-assistant.io/integrations/bsblan/) |
| Rule   | [test-before-configure](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/test-before-configure)                                                     |
| Status | **done**                                                                 |

## Overview

The `test-before-configure` rule applies to this integration because it connects to a network device (`iot_class: local_polling`) and requires connection details like host, port, and credentials to function. Validating these details before creating the configuration entry is crucial for a good user experience.

The `bsblan` integration fully complies with this rule. The config flow robustly tests the connection and credentials before creating the entry.

This is implemented in `config_flow.py` through a helper method, `_validate_and_create`, which is called from the `async_step_user` and `async_step_discovery_confirm` steps.

Inside `_validate_and_create`, the connection test is wrapped in a `try...except` block:

```python
# homeassistant/components/bsblan/config_flow.py L155-L188
async def _validate_and_create(
    self, user_input: dict[str, Any], is_discovery: bool = False
) -> ConfigFlowResult:
    """Validate device connection and create entry."""
    try:
        await self._get_bsblan_info()
    except BSBLANAuthError:
        if is_discovery:
            # ... shows discovery form with error
        return self._show_setup_form({"base": "invalid_auth"}, user_input)
    except BSBLANError:
        if is_discovery:
            # ... shows discovery form with error
        return self._show_setup_form({"base": "cannot_connect"})

    return self._async_create_entry()
```

The actual connection test happens within the `_get_bsblan_info` method, which instantiates the client and makes an API call:

```python
# homeassistant/components/bsblan/config_flow.py L324-L336
async def _get_bsblan_info(...) -> None:
    """Get device information from a BSBLAN device."""
    config = BSBLANConfig(
        host=self.host,
        passkey=self.passkey,
        # ...
    )
    session = async_get_clientsession(self.hass)
    bsblan = BSBLAN(config, session)
    device = await bsblan.device() # This is the test call
    # ...
```

If `bsblan.device()` raises a `BSBLANAuthError` (for bad credentials) or `BSBLANError` (for connection issues), the `except` blocks in `_validate_and_create` catch it and re-display the form with the appropriate error (`invalid_auth` or `cannot_connect`). The config entry is only created via `_async_create_entry()` upon a successful connection test.

This pattern is also correctly applied during the re-authentication flow (`async_step_reauth_confirm`), ensuring that updated credentials are also validated before being saved.

---

_Created at 2025-08-05 09:38:37 using gemini-2.5-pro. Prompt tokens: 11209, Output tokens: 773, Total tokens: 14154._

_Report based on [`ee9ff71`](https://github.com/home-assistant/core/tree/ee9ff717e0d36ca02bf52a242acd3a47359eae61)._

_AI can be wrong. Always verify the report and the code against the rule._
