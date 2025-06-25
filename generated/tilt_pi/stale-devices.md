# tilt_pi: stale-devices

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [tilt_pi](https://www.home-assistant.io/integrations/tilt_pi/) |
| Rule   | [stale-devices](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/stale-devices)                                                     |
| Status | **todo**                                                                 |

## Overview

The `stale-devices` rule applies to this integration because it polls a Tilt Pi instance which reports on one or more Tilt hydrometers. It is possible for these hydrometers to be removed or stop reporting (e.g., battery dies), and in such cases, they should be removed from Home Assistant to avoid cluttering the UI with non-existent devices.

The `tilt_pi` integration currently does not follow this rule. The `TiltPiDataUpdateCoordinator` in `coordinator.py` fetches a complete list of currently available hydrometers via `self._api.get_hydrometers()` in its `_async_update_data` method. However, it does not compare this list with a list of previously seen devices.

When a hydrometer is no longer reported by the API, its corresponding entities will become `unavailable` due to the check in `entity.py`:
```python
# homeassistant/components/tilt_pi/entity.py
@property
def available(self) -> bool:
    """Return True if the hydrometer is available (present in coordinator data)."""
    return super().available and self._mac_id in self.coordinator.data
```
While making entities unavailable is correct, it does not satisfy the rule's requirement to remove the device itself from the device registry. The stale device and its entities will remain in Home Assistant indefinitely.

## Suggestions

To comply with the rule, you should modify the `TiltPiDataUpdateCoordinator` to track devices between updates and remove any that are no longer reported by the Tilt Pi API. Additionally, for robust device lookup, `DeviceInfo` should include the `identifiers` property.

1.  **Update `entity.py` to add `identifiers`:**
    In `homeassistant/components/tilt_pi/entity.py`, add the `identifiers` property to the `DeviceInfo` dictionary. This provides a stable, unique ID for the device within the integration's domain.

    ```python
    # homeassistant/components/tilt_pi/entity.py

    from .const import DOMAIN # Add this import
    
    # ...
    
    class TiltEntity(CoordinatorEntity[TiltPiDataUpdateCoordinator]):
        # ...
        def __init__(
            self,
            coordinator: TiltPiDataUpdateCoordinator,
            hydrometer: TiltHydrometerData,
        ) -> None:
            # ...
            self._attr_device_info = DeviceInfo(
                connections={(CONNECTION_NETWORK_MAC, hydrometer.mac_id)},
                identifiers={(DOMAIN, hydrometer.mac_id)}, # Add this line
                name=f"Tilt {hydrometer.color}",
                manufacturer="Tilt Hydrometer",
                model=f"{hydrometer.color} Tilt Hydrometer",
            )
        # ...
    ```

2.  **Update `coordinator.py` to remove stale devices:**
    Modify the `TiltPiDataUpdateCoordinator` to store the set of previously seen device MAC addresses. In each update, compare the new set of devices with the old set and remove any that have disappeared.

    ```python
    # homeassistant/components/tilt_pi/coordinator.py

    from datetime import timedelta
    from typing import Final

    from tiltpi import TiltHydrometerData, TiltPiClient, TiltPiError

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.const import CONF_HOST, CONF_PORT
    from homeassistant.core import HomeAssistant
    import homeassistant.helpers.device_registry as dr # Add this import
    from homeassistant.helpers.aiohttp_client import async_get_clientsession
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

    from .const import DOMAIN, LOGGER # Add DOMAIN to imports

    SCAN_INTERVAL: Final = timedelta(seconds=60)

    type TiltPiConfigEntry = ConfigEntry[TiltPiDataUpdateCoordinator]


    class TiltPiDataUpdateCoordinator(DataUpdateCoordinator[dict[str, TiltHydrometerData]]):
        """Class to manage fetching Tilt Pi data."""

        config_entry: TiltPiConfigEntry
        previous_devices: set[str] = set() # Add this attribute

        def __init__(
            self,
            hass: HomeAssistant,
            config_entry: TiltPiConfigEntry,
        ) -> None:
            """Initialize the coordinator."""
            super().__init__(
                hass,
                LOGGER,
                config_entry=config_entry,
                name="Tilt Pi",
                update_interval=SCAN_INTERVAL,
            )
            self._api = TiltPiClient(
                host=config_entry.data[CONF_HOST],
                port=config_entry.data[CONF_PORT],
                session=async_get_clientsession(hass),
            )
            self.identifier = config_entry.entry_id

        async def _async_update_data(self) -> dict[str, TiltHydrometerData]:
            """Fetch data from Tilt Pi and return as a dict keyed by mac_id."""
            try:
                hydrometers = await self._api.get_hydrometers()
            except TiltPiError as err:
                raise UpdateFailed(f"Error communicating with Tilt Pi: {err}") from err

            data = {h.mac_id: h for h in hydrometers}
            current_devices = set(data)

            if stale_devices := self.previous_devices - current_devices:
                device_registry = dr.async_get(self.hass)
                for mac_id in stale_devices:
                    device = device_registry.async_get_device(identifiers={(DOMAIN, mac_id)})
                    if device:
                        device_registry.async_update_device(
                            device_id=device.id,
                            remove_config_entry_id=self.config_entry.entry_id,
                        )
            
            self.previous_devices = current_devices
            return data
    ```

These changes ensure that when a Tilt hydrometer is permanently removed from the source, its corresponding device entry and entities are cleanly removed from Home Assistant, fully satisfying the `stale-devices` rule.

---

_Created at 2025-06-25 18:56:50 using gemini-2.5-pro-preview-06-05. Prompt tokens: 4561, Output tokens: 1475, Total tokens: 9006._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
