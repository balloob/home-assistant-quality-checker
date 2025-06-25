# geocaching: test-before-setup

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [geocaching](https://www.home-assistant.io/integrations/geocaching/) |
| Rule   | [test-before-setup](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/test-before-setup)                                                     |
| Status | **done**                                                                 |

## Overview

The `test-before-setup` rule requires that an integration verifies it can successfully connect to the device or service and authenticate before the setup process is considered complete. This provides immediate feedback to the user if something is wrong.

The `geocaching` integration correctly follows this rule by leveraging the `DataUpdateCoordinator` pattern.

In `__init__.py`, the `async_setup_entry` function initializes the coordinator and then immediately calls `await coordinator.async_config_entry_first_refresh()`:

```python
# homeassistant/components/geocaching/__init__.py

async def async_setup_entry(hass: HomeAssistant, entry: GeocachingConfigEntry) -> bool:
    """Set up Geocaching from a config entry."""
    # ...
    coordinator = GeocachingDataUpdateCoordinator(
        hass, entry=entry, session=oauth_session
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True
```

This call blocks the setup process until the first data fetch is attempted. The logic for this fetch is in `coordinator.py`:

```python
# homeassistant/components/geocaching/coordinator.py

async def _async_update_data(self) -> GeocachingStatus:
    """Fetch the latest Geocaching status."""
    try:
        return await self.geocaching.update()
    except GeocachingInvalidSettingsError as error:
        raise UpdateFailed(f"Invalid integration configuration: {error}") from error
    except GeocachingApiError as error:
        raise UpdateFailed(f"Invalid response from API: {error}") from error
```

1.  **Connection Errors**: If the `self.geocaching.update()` call fails due to a network issue or an API error, it raises a `GeocachingApiError`. This is caught and re-raised as `UpdateFailed`. The `DataUpdateCoordinator`'s `async_config_entry_first_refresh` method translates an `UpdateFailed` exception into a `ConfigEntryNotReady` exception, which correctly tells Home Assistant to retry the setup later.

2.  **Authentication Errors**: The integration uses `OAuth2Session`. During the data update, the underlying `geocachingapi` library will use a token refresh method that calls `session.async_ensure_token_valid()`. If the OAuth tokens are invalid and cannot be refreshed, this helper will raise `ConfigEntryAuthFailed`. This exception is not caught within `_async_update_data`, so it propagates up and correctly triggers the re-authentication flow in Home Assistant.

By using this standard coordinator pattern, the integration effectively tests both connectivity and authentication before completing setup, fully satisfying the rule.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 18:50:44 using gemini-2.5-pro-preview-06-05. Prompt tokens: 5831, Output tokens: 746, Total tokens: 8743._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
