# devolo_home_network: appropriate-polling

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [devolo_home_network](https://www.home-assistant.io/integrations/devolo_home_network/) |
| Rule   | [appropriate-polling](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/appropriate-polling)                                                     |
| Status | **done**                                                                 |

## Overview

The `appropriate-polling` rule applies to this integration as its `manifest.json` specifies `"iot_class": "local_polling"`. The integration uses the `DataUpdateCoordinator` pattern to poll the devolo devices for data.

The integration fully complies with this rule by implementing a sophisticated polling strategy with multiple coordinators, each with a polling interval specifically tailored to the type of data it fetches. This demonstrates a best-practice approach to responsible polling.

The polling intervals are defined as constants in `homeassistant/components/devolo_home_network/const.py`:

```python
FIRMWARE_UPDATE_INTERVAL = timedelta(hours=5)
LONG_UPDATE_INTERVAL = timedelta(minutes=5)
SHORT_UPDATE_INTERVAL = timedelta(seconds=15)
```

These constants are then applied to different coordinators in `homeassistant/components/devolo_home_network/coordinator.py` based on the data's nature:

1.  **Infrequent Data:** The `DevoloFirmwareUpdateCoordinator` uses `FIRMWARE_UPDATE_INTERVAL` (5 hours), which is a very sensible interval for checking for new firmware.
    ```python
    # homeassistant/components/devolo_home_network/coordinator.py
    class DevoloFirmwareUpdateCoordinator(DevoloDataUpdateCoordinator[UpdateFirmwareCheck]):
        def __init__(
            # ...
            update_interval: timedelta | None = FIRMWARE_UPDATE_INTERVAL,
        ) -> None:
    ```
2.  **Semi-Static Data:** Coordinators for data that does not change often, like the PLC network topology (`DevoloLogicalNetworkCoordinator`) or neighboring Wi-Fi networks (`DevoloWifiNeighborAPsGetCoordinator`), use the `LONG_UPDATE_INTERVAL` of 5 minutes. This prevents unnecessary polling for diagnostic data.
    ```python
    # homeassistant/components/devolo_home_network/coordinator.py
    class DevoloLogicalNetworkCoordinator(DevoloDataUpdateCoordinator[LogicalNetwork]):
        def __init__(
            # ...
            update_interval: timedelta | None = LONG_UPDATE_INTERVAL,
        ) -> None:
    # ...
    class DevoloWifiNeighborAPsGetCoordinator(
        DevoloDataUpdateCoordinator[list[NeighborAPInfo]]
    ):
        def __init__(
            # ...
            update_interval: timedelta | None = LONG_UPDATE_INTERVAL,
        ) -> None:
    ```
3.  **Dynamic Data:** For data that benefits from more frequent updates, such as the status of connected Wi-Fi clients for device tracking (`DevoloWifiConnectedStationsGetCoordinator`) or the state of switches (`DevoloLedSettingsGetCoordinator`, `DevoloWifiGuestAccessGetCoordinator`), the `SHORT_UPDATE_INTERVAL` of 15 seconds is used. This provides good responsiveness for the user without being overly aggressive.
    ```python
    # homeassistant/components/devolo_home_network/coordinator.py
    class DevoloWifiConnectedStationsGetCoordinator(
        DevoloDataUpdateCoordinator[list[ConnectedStationInfo]]
    ):
        def __init__(
            # ...
            update_interval: timedelta | None = SHORT_UPDATE_INTERVAL,
        ) -> None:
    ```
This granular and context-aware assignment of polling intervals shows that the integration is designed to be efficient and responsible, fully adhering to the spirit and letter of the `appropriate-polling` rule.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 19:02:26 using gemini-2.5-pro. Prompt tokens: 18852, Output tokens: 884, Total tokens: 22131._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
