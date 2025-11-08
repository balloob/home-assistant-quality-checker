# bsblan: test-before-setup

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [bsblan](https://www.home-assistant.io/integrations/bsblan/) |
| Rule   | [test-before-setup](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/test-before-setup)                                                     |
| Status | **todo**                                                                 |

## Overview

The `test-before-setup` rule requires that integrations test the connection and authentication to a device during the setup process (`async_setup_entry`) and raise specific exceptions (`ConfigEntryNotReady`, `ConfigEntryAuthFailed`, `ConfigEntryError`) on failure. This rule applies to the `bsblan` integration as it communicates with a local network device.

The integration partially follows this rule. It correctly uses a `DataUpdateCoordinator` and calls `await coordinator.async_config_entry_first_refresh()` at the beginning of `async_setup_entry`. The coordinator's `_async_update_data` method handles `BSBLANAuthError` and `BSBLANConnectionError` from the underlying library, which correctly results in `ConfigEntryAuthFailed` or `ConfigEntryNotReady` being raised, respectively. This is an excellent implementation of the recommended pattern.

However, after the coordinator's first refresh completes successfully, `async_setup_entry` in `__init__.py` proceeds to make three additional, uncaught network calls:

```python
# homeassistant/components/bsblan/__init__.py

    # ...
    await coordinator.async_config_entry_first_refresh()

    # Fetch all required data concurrently
    device = await bsblan.device()
    info = await bsblan.info()
    static = await bsblan.static_values()
    # ...
```

These calls to fetch static device information (`device`, `info`, `static_values`) are not wrapped in a `try...except` block. If a network error or other issue occurs after the coordinator's initial check but before these calls complete, an unhandled exception from the `bsblan` library will be raised. This will cause the setup to fail with a generic traceback in the logs instead of gracefully signaling to Home Assistant that the entry is not ready and should be retried.

## Suggestions

To fully comply with the rule, all network calls made during `async_setup_entry` must be protected. You should wrap the additional API calls in a `try...except` block to catch potential communication errors and raise the appropriate Home Assistant exception.

Here is an example of how to modify `homeassistant/components/bsblan/__init__.py`:

```python
# homeassistant/components/bsblan/__init__.py

# Add required imports
from bsblan import BSBLAN, BSBLANConfig, Device, Info, StaticState, BSBLANConnectionError, BSBLANAuthError, BSBLANError
# ...
from homeassistant.exceptions import ConfigEntryError, ConfigEntryNotReady, ConfigEntryAuthFailed
# ...

async def async_setup_entry(hass: HomeAssistant, entry: BSBLanConfigEntry) -> bool:
    """Set up BSB-Lan from a config entry."""

    # ... (config and coordinator setup remains the same)

    # Create and perform first refresh of the coordinator
    coordinator = BSBLanUpdateCoordinator(hass, entry, bsblan)
    await coordinator.async_config_entry_first_refresh()

    try:
        # Fetch all required data concurrently
        device = await bsblan.device()
        info = await bsblan.info()
        static = await bsblan.static_values()
    except BSBLANConnectionError as err:
        raise ConfigEntryNotReady("Failed to retrieve static device data from BSB-Lan") from err
    except BSBLANAuthError as err:
        # This is less likely if the coordinator succeeded, but it is good practice to handle it.
        raise ConfigEntryAuthFailed("Authentication failed while retrieving static device data") from err
    except BSBLANError as err:
        # Catch other library-specific errors as a permanent failure.
        raise ConfigEntryError("An unknown error occurred while retrieving static device data") from err

    entry.runtime_data = BSBLanData(
        client=bsblan,
        coordinator=coordinator,
        device=device,
        info=info,
        static=static,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True
```

By adding this `try...except` block, you ensure that if any of the static data fetches fail, the integration will correctly report the issue as either a temporary problem (`ConfigEntryNotReady`), an authentication failure (`ConfigEntryAuthFailed`), or a permanent error (`ConfigEntryError`), making the setup process more robust and user-friendly.

---

_Created at 2025-08-05 09:39:22 using gemini-2.5-pro. Prompt tokens: 11052, Output tokens: 1106, Total tokens: 15279._

_Report based on [`ee9ff71`](https://github.com/home-assistant/core/tree/ee9ff717e0d36ca02bf52a242acd3a47359eae61)._

_AI can be wrong. Always verify the report and the code against the rule._
