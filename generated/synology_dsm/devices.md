```markdown
# synology_dsm: devices

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [devices](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/devices)                                                     |
| Status | **todo**                                                                 |
| Reason |                                                                          |

## Overview

This rule requires integrations to create devices in the Home Assistant device registry to group related entities, providing a better user experience. Devices can represent physical hardware or services. The rule also notes that service-based devices should be marked with `entry_type=DeviceEntryType.SERVICE`.

The `synology_dsm` integration does create devices and effectively uses the device registry to group entities.

*   The core entities related to the main Synology NAS unit (CPU/memory usage, network usage, temperature, uptime, buttons like reboot/shutdown, and the update entity) are grouped under a single device representing the NAS itself. This is handled by the `SynologyDSMBaseEntity` class (`homeassistant/components/synology_dsm/entity.py`), which defines `_attr_device_info` using the NAS serial number (`(DOMAIN, information.serial)`).
*   Entities related to storage components (volumes, disks) and external USB devices are grouped under separate devices for each component (e.g., each disk, each volume, each external device/partition). This is handled by the `SynologyDSMDeviceEntity` class (`homeassistant/components/synology_dsm/entity.py`). These component devices are correctly linked back to the main NAS device using `via_device=(DOMAIN, information.serial)`.
*   Camera entities (`homeassistant/components/synology_dsm/camera.py`) are grouped under devices representing individual cameras. These camera devices are linked back to a "Surveillance Station" device using `via_device=(DOMAIN, f"{information.serial}_{SynoSurveillanceStation.INFO_API_KEY}")`.
*   The Surveillance Station "Home Mode" switch entity (`homeassistant/components/synology_dsm/switch.py`) is grouped under the same "Surveillance Station" device as the cameras, using the identifier `(DOMAIN, f"{self._api.information.serial}_{SynoSurveillanceStation.INFO_API_KEY}")`. This device represents a specific service provided by the NAS rather than the physical NAS unit itself.

The integration successfully creates devices and links related entities. However, the Surveillance Station device, which represents a service rather than a physical piece of hardware like the NAS or a disk, is not marked as a service device using `entry_type=DeviceEntryType.SERVICE` in its `DeviceInfo`. This is a minor deviation from the recommended practice outlined in the rule description for devices representing services.

Because the integration does not explicitly mark the service-based device grouping Surveillance Station entities as `DeviceEntryType.SERVICE`, it does not fully adhere to the rule's best practices for service devices.

## Suggestions

To fully comply with the rule and its recommendations for service-based devices, add `entry_type=DeviceEntryType.SERVICE` to the `DeviceInfo` object created for the Surveillance Station device.

Modify the `device_info` property in the `SynoDSMSurveillanceHomeModeToggle` class (`homeassistant/components/synology_dsm/switch.py`):

```python
    @property
    def device_info(self) -> DeviceInfo:
        """Return the device information."""
        assert self._api.surveillance_station is not None
        assert self._api.information is not None
        assert self._api.network is not None
        return DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    f"{self._api.information.serial}_{SynoSurveillanceStation.INFO_API_KEY}",
                )
            },
            name=f"{self._api.network.hostname} Surveillance Station",
            manufacturer="Synology",
            model=self._api.information.model,
            sw_version=self._version,
            via_device=(DOMAIN, self._api.information.serial),
            # Add the line below
            entry_type=DeviceEntryType.SERVICE,
        )
```

This change will correctly classify the Surveillance Station device in the Home Assistant device registry as a service device, providing clearer context to the user. The cameras linked via this device (`via_device`) will then correctly show that they are connected through the "Surveillance Station" service device, which in turn is linked to the main NAS device.

```

_Created at 2025-05-25 11:49:15. Prompt tokens: 39480, Output tokens: 1030, Total tokens: 41667_
