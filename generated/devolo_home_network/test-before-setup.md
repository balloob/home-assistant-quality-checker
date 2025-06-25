# devolo_home_network: test-before-setup

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [devolo_home_network](https://www.home-assistant.io/integrations/devolo_home_network/) |
| Rule   | [test-before-setup](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/test-before-setup)                                                     |
| Status | **done**                                                                 |

## Overview

The `test-before-setup` rule is applicable to the `devolo_home_network` integration as it communicates with a local network device that could be offline, have a wrong password, or encounter other connection issues.

The integration fully complies with this rule through a two-part validation process within its `async_setup_entry` function in `__init__.py`:

1.  **Initial Connection Check**: The setup process begins by attempting to connect to the device. It correctly wraps this attempt in a `try...except` block. If the device is not found, the underlying library raises a `DeviceNotFound` exception, which is caught and re-raised as `ConfigEntryNotReady`. This correctly informs Home Assistant that the issue might be temporary (e.g., the device is offline) and that a retry should be scheduled.

    ```python
    # homeassistant/components/devolo_home_network/__init__.py
    try:
        device = Device(
            ip=entry.data[CONF_IP_ADDRESS], zeroconf_instance=zeroconf_instance
        )
        await device.async_connect(session_instance=async_client)
        # ...
    except DeviceNotFound as err:
        raise ConfigEntryNotReady(
            # ...
        ) from err
    ```

2.  **Coordinator First Refresh**: The integration follows the recommended pattern of using data update coordinators. After initializing the necessary coordinators, it calls `await coordinator.async_config_entry_first_refresh()` for each one. This implicitly tests the ability to fetch data.

    ```python
    # homeassistant/components/devolo_home_network/__init__.py
    for coordinator in coordinators.values():
        await coordinator.async_config_entry_first_refresh()
    ```

    The `DevoloDataUpdateCoordinator` in `coordinator.py` is designed to handle API exceptions during data fetching. Its `_async_update_data` method correctly translates library-specific exceptions into Home Assistant exceptions as required by the rule:
    *   `DeviceUnavailable` is caught and raises `UpdateFailed`, which `async_config_entry_first_refresh` converts to `ConfigEntryNotReady`.
    *   `DevicePasswordProtected` is caught and raises `ConfigEntryAuthFailed`, which will trigger the re-authentication flow.

    ```python
    # homeassistant/components/devolo_home_network/coordinator.py
    async def _async_update_data(self) -> _DataT:
        """Fetch the latest data from the source."""
        # ...
            try:
                return await super()._async_update_data()
            except DeviceUnavailable as err:
                raise UpdateFailed(...) from err
            except DevicePasswordProtected as err:
                raise ConfigEntryAuthFailed(...) from err
    ```

This comprehensive approach ensures that both basic connectivity and authenticated API access are verified before the integration setup is finalized, fully satisfying the `test-before-setup` rule.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 19:06:22 using gemini-2.5-pro. Prompt tokens: 18751, Output tokens: 787, Total tokens: 21932._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
