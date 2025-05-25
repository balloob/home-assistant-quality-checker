# synology_dsm: stale-devices

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [stale-devices](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/stale-devices) |
| Status | **done**                                                                 |

## Overview

This rule requires integrations to handle devices that are no longer available on the connected hub or service. This can be done either by automatically removing the devices from Home Assistant's device registry when detected as stale or by implementing `async_remove_config_entry_device` to allow users to manually remove stale devices from the UI.

The `synology_dsm` integration connects to a Synology NAS device. It registers devices for the NAS itself, storage volumes, disks, external USB devices, and surveillance station cameras.

The integration does not automatically detect and remove stale devices (e.g., removed disks, volumes, or cameras) within its data update coordinators (`SynologyDSMCentralUpdateCoordinator`, `SynologyDSMCameraUpdateCoordinator`). The coordinator update methods primarily fetch the *current* state without comparing it against a previous list of devices to identify removals.

However, the integration **does** implement the `async_remove_config_entry_device` function in its `__init__.py` file. This function is called when a user attempts to remove a device from the Home Assistant device registry UI. The implementation checks if the device identifiers of the device being removed still exist in the data currently fetched by the integration (specifically, the serial number for the main NAS device, and serial combined with the device ID for storage, external USB, and camera devices).

```python
# homeassistant/components/synology_dsm/__init__.py
async def async_remove_config_entry_device(
    hass: HomeAssistant, entry: SynologyDSMConfigEntry, device_entry: dr.DeviceEntry
) -> bool:
    """Remove synology_dsm config entry from a device."""
    data = entry.runtime_data
    api = data.api
    assert api.information is not None
    serial = api.information.serial
    storage = api.storage
    assert storage is not None
    all_cameras: list[SynoCamera] = []
    if api.surveillance_station is not None:
        # get_all_cameras does not do I/O
        all_cameras = api.surveillance_station.get_all_cameras()
    device_ids = chain(
        (camera.id for camera in all_cameras),
        storage.volumes_ids,
        storage.disks_ids,
        storage.volumes_ids,
        (SynoSurveillanceStation.INFO_API_KEY,),  # Camera home/away device
    )
    return not device_entry.identifiers.intersection(
        (
            (DOMAIN, serial),  # Base device
            *(
                (DOMAIN, f"{serial}_{device_id}") for device_id in device_ids
            ),  # Storage and cameras
        )
    )
```

By implementing `async_remove_config_entry_device` in this manner, the integration allows Home Assistant users to manually remove devices that are no longer present on the Synology NAS, fulfilling the rule's requirement to handle stale devices. The check within the function ensures that only devices truly missing from the NAS's current state can be removed manually.

## Suggestions

No suggestions needed.

_Created at 2025-05-25 11:52:35. Prompt tokens: 39907, Output tokens: 796, Total tokens: 41963_
