```markdown
# synology_dsm: log-when-unavailable

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [log-when-unavailable](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/log-when-unavailable)                                                     |
| Status | **done**                                                                 |

## Overview

This rule requires integrations to log an `info` level message once when a device or service becomes unavailable and once when it becomes available again, to avoid log spam.

The `synology_dsm` integration uses `DataUpdateCoordinator` classes (`SynologyDSMCentralUpdateCoordinator`, `SynologyDSMCameraUpdateCoordinator`, `SynologyDSMSwitchUpdateCoordinator`) for polling data from the Synology DSM device.

The `DataUpdateCoordinator` base class provided by Home Assistant includes built-in logic to handle this logging requirement. When the `_async_update_data` method of a coordinator raises an `UpdateFailed` exception, the coordinator automatically marks the entities as unavailable and logs an `info` level message once. When a subsequent update is successful, the entities are marked available, and an `info` level message is logged indicating recovery.

In `synology_dsm/coordinator.py`, the `async_re_login_on_expired` decorator is used on the `_async_update_data` methods of the various coordinators. This decorator catches `SynologyDSMNotLoggedInException` and `SYNOLOGY_CONNECTION_EXCEPTIONS` and then explicitly raises `UpdateFailed`.

For example, in `SynologyDSMSwitchUpdateCoordinator._async_update_data`:
```python
    @async_re_login_on_expired
    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch all data from api."""
        surveillance_station = self.api.surveillance_station
        assert surveillance_station is not None
        return {
            "switches": {
                "home_mode": bool(await surveillance_station.get_home_mode_status())
            }
        }
```
Any exceptions caught by `@async_re_login_on_expired` result in `UpdateFailed` being raised. Similarly, in `SynologyDSMCameraUpdateCoordinator._async_update_data`, `SynologyDSMAPIErrorException` is caught and raises `UpdateFailed`.

Since the integration correctly utilizes the `DataUpdateCoordinator` pattern and raises `UpdateFailed` upon communication errors during polling, it leverages Home Assistant's built-in compliance with the `log-when-unavailable` rule.

## Suggestions

No suggestions needed.
```

_Created at 2025-05-25 11:48:39. Prompt tokens: 39789, Output tokens: 620, Total tokens: 41449_
