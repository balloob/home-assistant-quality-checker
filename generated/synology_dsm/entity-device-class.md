```markdown
# synology_dsm: entity-device-class

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [entity-device-class](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-device-class)                                                     |
| Status | **todo**                                                                 |
| Reason |                                                                          |

## Overview

This rule requires that integrations use `device_class` where possible for their entities. This provides semantic context used by Home Assistant for various features like UI representation, unit conversion, voice control, and exposing entities to external ecosystems. The rule applies to the `synology_dsm` integration as it creates several types of entities (`binary_sensor`, `button`, `camera`, `sensor`, `switch`, `update`).

The integration makes good use of `device_class` in many places.

*   **Binary Sensors:** The `SynologyDSMBinarySensorEntityDescription` in `binary_sensor.py` includes `device_class`, and the defined sensors (`SECURITY_BINARY_SENSORS`, `STORAGE_DISK_BINARY_SENSORS`) correctly use `BinarySensorDeviceClass.SAFETY`.
*   **Buttons:** The `SynologyDSMbuttonDescription` in `button.py` includes `device_class`, and the defined buttons (`BUTTONS`) correctly use `ButtonDeviceClass.RESTART`.
*   **Sensors:** Many sensor descriptions in `sensor.py` correctly utilize appropriate device classes like `SensorDeviceClass.TEMPERATURE`, `SensorDeviceClass.DATA_SIZE`, `SensorDeviceClass.DATA_RATE`, and `SensorDeviceClass.TIMESTAMP`.
*   **Switches:** The defined switch (`SURVEILLANCE_SWITCH`) does not have a specific `SwitchDeviceClass` assigned, but there are no standard `SwitchDeviceClass` values that would semantically fit a "Home mode" toggle.
*   **Cameras:** The camera entity in `camera.py` does not explicitly set a `device_class`. However, the entity type itself (`Camera`) implies its role, and there are no generic `CameraDeviceClass` values applicable to a standard camera feed. This is acceptable.
*   **Update:** The update entity in `update.py` does not set a `device_class`. The `UpdateEntity` component supports `UpdateDeviceClass.FIRMWARE` or `UpdateDeviceClass.SOFTWARE`.

While many entities are correctly classified, there are some sensor entities and the update entity where an applicable `device_class` is available but not used. Specifically, sensor entities representing statuses and load averages, and the update entity. Because not all applicable device classes are used, the integration does not fully follow the rule.

## Suggestions

To make the `synology_dsm` integration fully compliant with the `entity-device-class` rule, the following changes are suggested:

1.  **Sensor Entities (`sensor.py`):**
    *   For status sensors (`key` ending in `_status`): Add `device_class=SensorDeviceClass.ENUM` to their `SynologyDSMSensorEntityDescription`. This indicates that the state represents a fixed set of values, which is suitable for status strings like "healthy", "degraded", etc.

    ```python
    STORAGE_VOL_SENSORS: tuple[SynologyDSMSensorEntityDescription, ...] = (
        SynologyDSMSensorEntityDescription(
            api_key=SynoStorage.API_KEY,
            key="volume_status",
            translation_key="volume_status",
            device_class=SensorDeviceClass.ENUM, # Add this
        ),
        # ... other volume sensors
    )
    STORAGE_DISK_SENSORS: tuple[SynologyDSMSensorEntityDescription, ...] = (
        SynologyDSMSensorEntityDescription(
            api_key=SynoStorage.API_KEY,
            key="disk_smart_status",
            translation_key="disk_smart_status",
            entity_registry_enabled_default=False,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.ENUM, # Add this
        ),
        SynologyDSMSensorEntityDescription(
            api_key=SynoStorage.API_KEY,
            key="disk_status",
            translation_key="disk_status",
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.ENUM, # Add this
        ),
        # ... other disk sensors
    )
    EXTERNAL_USB_DISK_SENSORS: tuple[SynologyDSMSensorEntityDescription, ...] = (
        SynologyDSMSensorEntityDescription(
            api_key=SynoCoreExternalUSB.API_KEY,
            key="device_status",
            translation_key="device_status",
            device_class=SensorDeviceClass.ENUM, # Add this
        ),
        # ... other external usb sensors
    )
    ```

    *   For CPU load average sensors (`key` ending in `_load`) which use `ENTITY_UNIT_LOAD`: While they already use `SensorStateClass.MEASUREMENT`, adding `device_class=SensorDeviceClass.MEASUREMENT` explicitly clarifies their type, although `ENTITY_UNIT_LOAD` is a custom unit. Given the unit is custom, `SensorDeviceClass.MEASUREMENT` or leaving it without a specific device class might be acceptable, but explicitly setting `MEASUREMENT` aligns it with other generic measurement sensors.

    ```python
    UTILISATION_SENSORS: tuple[SynologyDSMSensorEntityDescription, ...] = (
        # ... other utilisation sensors
        SynologyDSMSensorEntityDescription(
            api_key=SynoCoreUtilization.API_KEY,
            key="cpu_1min_load",
            translation_key="cpu_1min_load",
            native_unit_of_measurement=ENTITY_UNIT_LOAD,
            entity_registry_enabled_default=False,
            device_class=SensorDeviceClass.MEASUREMENT, # Add this
            state_class=SensorStateClass.MEASUREMENT, # Ensure state_class is also set for consistency
        ),
        SynologyDSMSensorEntityDescription(
            api_key=SynoCoreUtilization.API_KEY,
            key="cpu_5min_load",
            translation_key="cpu_5min_load",
            native_unit_of_measurement=ENTITY_UNIT_LOAD,
            device_class=SensorDeviceClass.MEASUREMENT, # Add this
            state_class=SensorStateClass.MEASUREMENT, # Ensure state_class is also set for consistency
        ),
        SynologyDSMSensorEntityDescription(
            api_key=SynoCoreUtilization.API_KEY,
            key="cpu_15min_load",
            translation_key="cpu_15min_load",
            native_unit_of_measurement=ENTITY_UNIT_LOAD,
            device_class=SensorDeviceClass.MEASUREMENT, # Add this
            state_class=SensorStateClass.MEASUREMENT, # Ensure state_class is also set for consistency
        ),
        # ... rest of utilisation sensors
    )
    ```
    *(Note: `state_class` was added to the load average sensors for consistency with other measurement sensors defined in the same file)*

2.  **Update Entity (`update.py`):**
    *   Add `device_class=UpdateDeviceClass.FIRMWARE` to the `SynologyDSMUpdateEntityEntityDescription`. This clearly indicates that the entity represents a firmware update.

    ```python
    from homeassistant.components.update import (
        UpdateDeviceClass, # Import this
        UpdateEntity,
        UpdateEntityDescription,
    )
    # ... other imports

    @dataclass(frozen=True, kw_only=True)
    class SynologyDSMUpdateEntityEntityDescription(
        UpdateEntityDescription, SynologyDSMEntityDescription
    ):
        """Describes Synology DSM update entity."""


    UPDATE_ENTITIES: Final = [
        SynologyDSMUpdateEntityEntityDescription(
            api_key=SynoCoreUpgrade.API_KEY,
            key="update",
            translation_key="update",
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=UpdateDeviceClass.FIRMWARE, # Add this
        )
    ]
    ```

These changes provide clearer semantic meaning to the entities, potentially improving their representation and usability within Home Assistant and integrated platforms.
```

_Created at 2025-05-25 11:50:44. Prompt tokens: 39480, Output tokens: 1921, Total tokens: 43233_
