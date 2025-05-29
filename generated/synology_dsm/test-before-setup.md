```markdown
# synology_dsm: test-before-setup

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [test-before-setup](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/test-before-setup)                                                     |
| Status | **done**                                       |

## Overview

This rule requires that an integration verifies it can connect and authenticate to the device or service during `async_setup_entry` before proceeding, raising appropriate exceptions (`ConfigEntryNotReady`, `ConfigEntryAuthFailed`, `ConfigEntryError`) on failure.

The `synology_dsm` integration applies this rule. The core connection and authentication logic resides within the `async_setup` method of the `SynoApi` class (`common.py`), which is called directly within the `async_setup_entry` function in `__init__.py`.

The integration demonstrates compliance by wrapping the call to `await api.async_setup()` in a `try...except` block in `homeassistant/components/synology_dsm/__init__.py`:

```python
    api = SynoApi(hass, entry)
    try:
        await api.async_setup()
    except SYNOLOGY_AUTH_FAILED_EXCEPTIONS as err:
        raise_config_entry_auth_error(err)
    except (*SYNOLOGY_CONNECTION_EXCEPTIONS, SynologyDSMNotLoggedInException) as err:
        # ... (error detail extraction) ...
        raise ConfigEntryNotReady(details) from err
```

*   It specifically catches `SYNOLOGY_AUTH_FAILED_EXCEPTIONS`, which is a tuple of exceptions defined in `const.py` that represent various authentication failures (e.g., invalid login, permission denied, 2FA required/failed). For these exceptions, it calls `raise_config_entry_auth_error`, which correctly translates them into a `homeassistant.exceptions.ConfigEntryAuthFailed`.
*   It also catches `SYNOLOGY_CONNECTION_EXCEPTIONS` (network errors, login failed) and `SynologyDSMNotLoggedInException`. These are treated as temporary connection or login session issues, and the code raises `homeassistant.exceptions.ConfigEntryNotReady`.

This pattern correctly identifies different types of failures during the initial setup phase and communicates them to Home Assistant using the required exception types, thereby adhering to the `test-before-setup` rule.

Additionally, the camera and switch coordinators (`SynologyDSMCameraUpdateCoordinator` and `SynologyDSMSwitchUpdateCoordinator`) utilize `await coordinator.async_config_entry_first_refresh()` immediately after initialization in `__init__.py`. As noted in the rule description, this usage also implicitly satisfies the "test before setup" requirement for the data they manage.

## Suggestions

No suggestions needed. The integration correctly implements the `test-before-setup` rule.
```

_Created at 2025-05-25 11:47:40. Prompt tokens: 39550, Output tokens: 671, Total tokens: 41581_
