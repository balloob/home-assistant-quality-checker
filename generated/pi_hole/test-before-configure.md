# pi_hole: test-before-configure

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [pi_hole](https://www.home-assistant.io/integrations/pi_hole/) |
| Rule   | [test-before-configure](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/test-before-configure)                                                     |
| Status | **done**                                                                 |
| Reason |                                                                          |

## Overview

The `test-before-configure` rule requires that integrations test the connection to the device or service during the config flow. If the connection or initial communication fails, an error message should be presented to the user on the configuration form, preventing setup with invalid parameters. This helps catch issues like incorrect IP addresses, credentials, or network problems early.

This rule applies to the `pi_hole` integration because it connects to a Pi-hole device over the local network. It does not fall under exceptions like being a helper integration or relying solely on runtime auto-discovery for setup.

The `pi_hole` integration **follows** this rule.

The connection test is implemented within the `config_flow.py` file, primarily in the `_async_try_connect` method. Let's examine its role:

1.  **Connection Attempt**:
    In `async_step_user` (and also in `async_step_api_key` and `async_step_reauth_confirm`), after gathering user input, the `_async_try_connect` method is called:
    ```python
    # homeassistant/components/pi_hole/config_flow.py
    # async_step_user:
            if not (errors := await self._async_try_connect()):
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=self._config
                )
            # ... further error handling or next step ...
    ```

2.  **Test Call and Error Handling in `_async_try_connect`**:
    This method instantiates the `Hole` client and attempts to fetch data, which serves as the connection test:
    ```python
    # homeassistant/components/pi_hole/config_flow.py
    async def _async_try_connect(self) -> dict[str, str]:
        # ... client setup ...
        pi_hole = Hole(...)
        try:
            await pi_hole.get_data()  # The actual test call
        except HoleError as ex:       # Catches specific library exceptions
            _LOGGER.debug("Connection failed: %s", ex)
            return {"base": "cannot_connect"} # Returns error for the form
        if not isinstance(pi_hole.data, dict): # Additional check for data validity
            return {CONF_API_KEY: "invalid_auth"} # Returns a different error
        return {} # Indicates success (no errors)
    ```
    -   `await pi_hole.get_data()`: This is the call that tests connectivity and API access.
    -   `except HoleError`: The `hole` library raises `HoleError` (or its subclasses like `HoleAuthError`) for various issues such as network problems (wrong host/port, firewall), SSL errors, timeouts, or authentication failures (e.g., API key required but not provided or invalid leading to certain API responses). If this exception occurs, the config flow returns `{"base": "cannot_connect"}`.
    -   `if not isinstance(pi_hole.data, dict)`: This is an additional validation. If `get_data()` "succeeds" without raising `HoleError` but the resulting `pi_hole.data` is not a dictionary (which might indicate an unexpected API response or a state the library doesn't explicitly error on but is problematic for the integration, like some auth issues), it returns `{CONF_API_KEY: "invalid_auth"}`.

3.  **Displaying Errors**:
    The errors returned by `_async_try_connect` (e.g., `{"base": "cannot_connect"}`) are then passed to `self.async_show_form`, which displays the corresponding error message to the user (defined in `strings.json` under `config.error.cannot_connect` or `config.error.invalid_auth`).

This implementation correctly tests the connection and API accessibility before creating the config entry. It handles expected failures from the `hole` library (`HoleError`) and has an additional check for data integrity, mapping these failures to user-facing error messages in the config flow. This fulfills the requirements of the `test-before-configure` rule.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-10 23:12:35. Prompt tokens: 10279, Output tokens: 1053, Total tokens: 19200._

_Report based on [`ab7f6c3`](https://github.com/home-assistant/core/tree/ab7f6c35287f43fe1207b3de4581b3bfabd49399)._

_AI can be wrong. Always verify the report and the code against the rule._
