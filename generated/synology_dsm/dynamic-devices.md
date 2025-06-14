```markdown
# synology_dsm: dynamic-devices

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [dynamic-devices](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/dynamic-devices) |
| Status | **todo**                                                                 |
| Reason |                                                                          |

## Overview

This rule requires integrations to automatically create entities for devices that are added to the service *after* the integration has been initially set up. This improves user experience by removing the need for manual re-configuration when, for example, a new disk is added to a NAS or a new camera is connected to Surveillance Station.

The `synology_dsm` integration currently does **not** fully follow this rule. While it uses `DataUpdateCoordinator` to fetch data from the Synology DSM periodically, the logic for creating entities is primarily located within the platform `async_setup_entry` functions (`sensor.py`, `binary_sensor.py`, `camera.py`). These functions iterate over the known devices (disks, volumes, USB devices, cameras) available *at the time the integration or platform is set up* and create entities for them.

There is no mechanism implemented to detect new devices appearing in subsequent coordinator updates after the initial setup and dynamically add corresponding entities to Home Assistant. For instance, if a user adds a new disk to the NAS or connects a new camera to Surveillance Station after the `synology_dsm` integration is already running, the integration will not automatically create entities for these new devices. A Home Assistant restart or integration reload would be required to pick them up.

This is evident in the `async_setup_entry` functions of the platform files:

*   In `homeassistant/components/synology_dsm/sensor.py` and `binary_sensor.py`, entities for storage (disks, volumes) and external USB devices are created by iterating directly over `api.storage.volumes_ids`, `api.storage.disks_ids`, and `external_usb.get_devices.values()` within `async_setup_entry`. This snapshot of devices is taken only during the initial setup.
*   In `homeassistant/components/synology_dsm/camera.py`, camera entities are created by iterating over `coordinator.data["cameras"]` within `async_setup_entry`. Again, this is done only during the initial setup.

The pattern described in the rule's example, which involves adding a listener to the coordinator to check for new devices on each update and dynamically add entities using `async_add_entities` within the listener callback, is not present in the current code.

## Suggestions

To make the `synology_dsm` integration compliant with the `dynamic-devices` rule, the entity creation logic in the relevant platform files (`sensor.py`, `binary_sensor.py`, `camera.py`) needs to be modified.

1.  **Maintain a set of known devices:** In each platform's `async_setup_entry`, initialize a set (or similar structure) to keep track of the unique identifiers of the devices for which entities have already been created.
2.  **Initial Entity Creation:** The initial loop over devices in `async_setup_entry` should populate this set and add the entities.
3.  **Add a Coordinator Listener:** Register a listener callback to the appropriate coordinator (e.g., `coordinator_central` for storage/USB in `sensor.py` and `binary_sensor.py`, `coordinator_cameras` for cameras in `camera.py`) using `entry.async_on_unload(coordinator.async_add_listener(callback))`.
4.  **Implement the Listener Callback:**
    *   Inside the callback function, access the updated device list from the coordinator's data (`coordinator.data` or via `api` if the data is mirrored there).
    *   Compare the current list of devices with the set of known devices.
    *   For each device identifier found in the current list but *not* in the known set, create the corresponding entity instance(s).
    *   Add these new entities to Home Assistant using the `async_add_entities` callback passed to `async_setup_entry`.
    *   Update the set of known devices with the newly added device identifiers.

**Example (Conceptual for `sensor.py`):**

```python
# homeassistant/components/synology_dsm/sensor.py

# ... (imports)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: SynologyDSMConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Synology NAS Sensor."""
    data = entry.runtime_data
    api = data.api
    coordinator = data.coordinator_central
    storage = api.storage
    external_usb = api.external_usb # Need to check if this is updated by central coordinator

    # Keep track of already added devices
    known_volume_ids: set[str] = set()
    known_disk_ids: set[str] = set()
    known_usb_device_names: set[str] = set()
    known_usb_partition_titles: set[str] = set()

    @callback
    def _add_new_storage_entities() -> None:
        """Check for new storage or USB devices and add entities."""
        new_entities = []

        # Volumes
        if storage is not None and storage.volumes_ids:
            current_volume_ids = set(storage.volumes_ids)
            new_volume_ids = current_volume_ids - known_volume_ids
            if new_volume_ids:
                new_entities.extend(
                    SynoDSMStorageSensor(api, coordinator, description, volume_id)
                    for volume_id in new_volume_ids
                    for description in STORAGE_VOL_SENSORS
                )
                known_volume_ids.update(new_volume_ids)

        # Disks
        if storage is not None and storage.disks_ids:
             current_disk_ids = set(storage.disks_ids)
             new_disk_ids = current_disk_ids - known_disk_ids
             if new_disk_ids:
                # Assuming entry.data.get(CONF_DISKS, ...) filters initial entities
                # For dynamic, we should probably add all new ones found
                disks_to_add = [
                     disk_id for disk_id in new_disk_ids
                     if disk_id in entry.data.get(CONF_DISKS, new_disk_ids) # Re-apply user filter if needed, or add all
                ]
                new_entities.extend(
                    SynoDSMStorageSensor(api, coordinator, description, disk_id)
                    for disk_id in disks_to_add
                    for description in STORAGE_DISK_SENSORS
                )
                known_disk_ids.update(new_disk_ids)


        # External USB Devices and Partitions (assuming external_usb is updated by central coordinator)
        if external_usb is not None and external_usb.get_devices:
            current_usb_device_names = {dev.device_name for dev in external_usb.get_devices.values()}
            new_usb_device_names = current_usb_device_names - known_usb_device_names
            if new_usb_device_names:
                # Filter by user options if applicable
                devices_to_add = [
                    dev_name for dev_name in new_usb_device_names
                    if dev_name in entry.data.get(CONF_DEVICES, new_usb_device_names)
                ]
                new_entities.extend(
                    SynoDSMExternalUSBSensor(api, coordinator, description, device_name)
                    for device_name in devices_to_add
                    for description in EXTERNAL_USB_DISK_SENSORS
                )
                known_usb_device_names.update(new_usb_device_names)

            current_usb_partition_titles = {part.partition_title for dev in external_usb.get_devices.values() for part in dev.device_partitions.values()}
            new_usb_partition_titles = current_usb_partition_titles - known_usb_partition_titles
            if new_usb_partition_titles:
                 # Filter by user options if applicable
                partitions_to_add = [
                    part_title for part_title in new_usb_partition_titles
                    if part_title in entry.data.get(CONF_DEVICES, new_usb_partition_titles) # This filter logic might need refinement depending on how CONF_DEVICES is used
                ]
                new_entities.extend(
                     SynoDSMExternalUSBSensor(api, coordinator, description, partition_title)
                     for partition_title in partitions_to_add
                     for description in EXTERNAL_USB_PARTITION_SENSORS
                )
                known_usb_partition_titles.update(new_usb_partition_titles)


        if new_entities:
            async_add_entities(new_entities)

    # Initial setup - populate known devices and add existing entities
    _add_new_storage_entities()

    # Register listener for future updates
    # Assuming coordinator_central updates storage and external_usb
    entry.async_on_unload(coordinator.async_add_listener(_add_new_storage_entities))

    # ... (rest of setup for other sensors like utilisation, info)
```

Similar logic would be needed in `binary_sensor.py` for storage binary sensors and in `camera.py` for camera entities using the `coordinator_cameras`. The specific API calls to get the list of devices might vary slightly between platforms. The crucial part is the pattern of maintaining a set of known devices and using a coordinator listener to find and add new ones.

```
```

_Created at 2025-05-25 11:50:09. Prompt tokens: 39638, Output tokens: 2261, Total tokens: 44095_
