# pi_hole: test-before-setup

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [pi_hole](https://www.home-assistant.io/integrations/pi_hole/) |
| Rule   | [test-before-setup](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/test-before-setup)                                                     |
| Status | **todo**                                       |
| Reason | (Only include if Status is "exempt". Explain why the rule does not apply.) |

## Overview

The `test-before-setup` rule requires integrations to check during initialization if they can be set up correctly and to raise specific exceptions (`ConfigEntryNotReady`, `ConfigEntryAuthFailed`, `ConfigEntryError`) based on the nature of any failure. This allows Home Assistant to provide immediate and appropriate feedback to the user.

This rule applies to the `pi_hole` integration as it connects to an external device/service (a Pi-hole instance) and needs to verify this connection and authentication during setup.

The `pi_hole` integration utilizes a `DataUpdateCoordinator` and calls `await coordinator.async_config_entry_first_refresh()` within its `async_setup_entry` function (in `homeassistant/components/pi_hole/__init__.py`). This correctly implements the "test before setup" aspect, as the `async_config_entry_first_refresh` method will execute the coordinator's `async_update_data` method. If `async_update_data` raises an exception, the setup process will be halted, and an error will be indicated.

The `async_update_data` method is defined as:
```python
# homeassistant/components/pi_hole/__init__.py
async def async_update_data() -> None:
    """Fetch data from API endpoint."""
    try:
        await api.get_data()
        await api.get_versions()
    except HoleError as err: # Catches all errors from the 'hole' library
        raise UpdateFailed(f"Failed to communicate with API: {err}") from err
    if not isinstance(api.data, dict): # Checks for unexpected data format post-API call
        raise ConfigEntryAuthFailed
```

This implementation handles some cases correctly:
1.  **Temporary/Connection Issues:** If `api.get_data()` or `api.get_versions()` raise a generic `HoleError` (like `HoleConnectionError` from the `hole` library, e.g., device offline), it's caught, and `UpdateFailed` is raised. The `DataUpdateCoordinator` converts this into `ConfigEntryNotReady` during the first refresh, which is correct for temporary issues.
2.  **Auth Issues (Malformed Data):** If the API calls succeed without raising a `HoleError` but `api.data` is not a dictionary (e.g., the API returns an error message as a string due to an invalid or missing API key), the `if not isinstance(api.data, dict):` check correctly raises `ConfigEntryAuthFailed`.

However, there's a scenario where an authentication failure is not handled optimally:
The `hole` library (used for communicating with Pi-hole) defines a specific `HoleAuthError` (in `hole.exceptions`) which can be raised if the API token is explicitly rejected (e.g., "not authorized" response from Pi-hole).
Currently, because `HoleAuthError` is a subclass of `HoleError`, it is caught by the generic `except HoleError as err:` block. This results in `UpdateFailed` being raised, which subsequently leads to `ConfigEntryNotReady`. According to the rule, an authentication failure should result in `ConfigEntryAuthFailed` to prompt the user for re-authentication.

Therefore, while the integration does test before setup, it does not correctly map all authentication-related library exceptions to `ConfigEntryAuthFailed`.

The integration does not currently raise `ConfigEntryError`, which is for unrecoverable errors where retries or re-authentication won't help. Given the nature of Pi-hole communication, most errors would likely fall under temporary connection issues or authentication problems, so the absence of `ConfigEntryError` might be acceptable if no clear, permanent, non-auth failure modes are identifiable from the `hole` library.

## Suggestions

To fully comply with the `test-before-setup` rule, the `async_update_data` method in `homeassistant/components/pi_hole/__init__.py` should be modified to specifically catch `HoleAuthError` and raise `ConfigEntryAuthFailed`. Other `HoleError` types should continue to raise `UpdateFailed` (leading to `ConfigEntryNotReady`).

1.  **Import `HoleAuthError`**:
    Ensure `HoleAuthError` is imported from `hole.exceptions` at the top of `homeassistant/components/pi_hole/__init__.py`:
    ```python
    from hole.exceptions import HoleAuthError, HoleError
    ```

2.  **Modify `async_update_data`**:
    Update the `async_update_data` function to handle `HoleAuthError` separately:
    ```python
    # In homeassistant/components/pi_hole/__init__.py

    async def async_update_data() -> None:
        """Fetch data from API endpoint."""
        try:
            await api.get_data()
            await api.get_versions()
        except HoleAuthError as err:  # Catch specific authentication errors first
            _LOGGER.warning(
                "Authentication failed for Pi-hole at %s: %s", api.host, err
            )
            raise ConfigEntryAuthFailed(f"Authentication failed: {err}") from err
        except HoleError as err:  # Catch other 'hole' library errors (connection, response, etc.)
            _LOGGER.debug(
                "Failed to communicate with Pi-hole API at %s: %s", api.host, err
            )
            raise UpdateFailed(f"Failed to communicate with API: {err}") from err
        
        # This check remains useful as a fallback if no HoleError was raised,
        # but the API returned an unexpected data structure, which might also
        # indicate an authentication issue or an API change.
        if not isinstance(api.data, dict):
            _LOGGER.warning(
                "Pi-hole API at %s returned unexpected data type, possibly due to an authentication issue or API change.",
                api.host
            )
            raise ConfigEntryAuthFailed("API returned unexpected data structure")
    ```

**Reasoning for Suggestions:**

By explicitly catching `HoleAuthError` and raising `ConfigEntryAuthFailed`, the integration will correctly inform Home Assistant that an authentication problem has occurred. This allows Home Assistant to initiate a re-authentication flow if available, rather than just retrying the setup (which is the behavior of `ConfigEntryNotReady`). This change aligns the integration's error handling with the requirements of the `test-before-setup` rule for authentication failures. Other communication errors will still correctly result in `ConfigEntryNotReady` via `UpdateFailed`.

---

_Created at 2025-06-10 23:13:59. Prompt tokens: 10122, Output tokens: 1587, Total tokens: 18108._

_Report based on [`ab7f6c3`](https://github.com/home-assistant/core/tree/ab7f6c35287f43fe1207b3de4581b3bfabd49399)._

_AI can be wrong. Always verify the report and the code against the rule._
