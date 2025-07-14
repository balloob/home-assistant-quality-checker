```markdown
# synology_dsm: entity-category

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [entity-category](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-category)                                                     |
| Status | **todo**                                                                 |

## Overview

This rule requires entities to be assigned an appropriate `EntityCategory` (CONFIG or DIAGNOSTIC) when their default category is inappropriate. The `synology_dsm` integration provides various entity types.

The rule is applied correctly in several places:
-   The `button.py` entities (`reboot`, `shutdown`) correctly use `EntityCategory.CONFIG` in their descriptions (e.g., `homeassistant/components/synology_dsm/button.py`, lines 28 and 34).
-   Some `sensor.py` entities, specifically temperature sensors for volumes and disks, disk status sensors, and main DSM temperature/uptime sensors, correctly use `EntityCategory.DIAGNOSTIC` in their descriptions (e.g., `homeassistant/components/synology_dsm/sensor.py`, lines 112, 119, 143, 149, 156, 201, 208).
-   The `update.py` entity correctly uses `EntityCategory.DIAGNOSTIC` for the DSM update sensor (`homeassistant/components/synology_dsm/update.py`, line 29).
-   Camera entities and most external USB/volume/partition size/usage sensors do not require a specific category, so the default `None` is appropriate (`homeassistant/components/synology_dsm/camera.py`, `homeassistant/components/synology_dsm/sensor.py`).

However, the rule is not fully followed for all relevant entities:
-   The security status binary sensor (`binary_sensor.py`, line 32) provides diagnostic information but does not have `EntityCategory.DIAGNOSTIC` assigned.
-   All utilisation sensors (`sensor.py`, lines 53-98), which provide technical metrics like CPU load, memory usage, and network throughput, expose diagnostic data but lack `EntityCategory.DIAGNOSTIC`.
-   The external USB device status sensor (`sensor.py`, line 174) provides diagnostic information about the device status but lacks `EntityCategory.DIAGNOSTIC`.
-   The Surveillance Station Home Mode switch (`switch.py`, line 27) controls a configuration setting but does not have `EntityCategory.CONFIG` assigned.

Because several entities that represent diagnostic information or configuration settings do not have the appropriate `entity_category` assigned, the integration does not fully follow the rule.

## Suggestions

To comply with the `entity-category` rule, the following `EntityCategory` assignments should be added to the respective entity descriptions:

1.  **Binary Sensor (`binary_sensor.py`)**:
    *   Add `entity_category=EntityCategory.DIAGNOSTIC` to the `SynologyDSMBinarySensorEntityDescription` for the `status` sensor:

    ```python
    # homeassistant/components/synology_dsm/binary_sensor.py
    SECURITY_BINARY_SENSORS: tuple[SynologyDSMBinarySensorEntityDescription, ...] = (
        SynologyDSMBinarySensorEntityDescription(
            api_key=SynoCoreSecurity.API_KEY,
            key="status",
            translation_key="status",
            device_class=BinarySensorDeviceClass.SAFETY,
            entity_category=EntityCategory.DIAGNOSTIC, # Add this line
        ),
    )
    ```

2.  **Sensor (`sensor.py`)**:
    *   Add `entity_category=EntityCategory.DIAGNOSTIC` to all `SynologyDSMSensorEntityDescription` within the `UTILISATION_SENSORS` tuple (lines 53-98):

    ```python
    # homeassistant/components/synology_dsm/sensor.py
    UTILISATION_SENSORS: tuple[SynologyDSMSensorEntityDescription, ...] = (
        SynologyDSMSensorEntityDescription(
            api_key=SynoCoreUtilization.API_KEY,
            key="cpu_other_load",
            translation_key="cpu_other_load",
            native_unit_of_measurement=PERCENTAGE,
            entity_registry_enabled_default=False,
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC, # Add this line
        ),
        SynologyDSMSensorEntityDescription(
            api_key=SynoCoreUtilization.API_KEY,
            key="cpu_user_load",
            translation_key="cpu_user_load",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC, # Add this line
        ),
        # ... similarly for other UTILISATION_SENSORS
    )
    ```
    *   Add `entity_category=EntityCategory.DIAGNOSTIC` to the `SynologyDSMSensorEntityDescription` for the `device_status` sensor within the `EXTERNAL_USB_DISK_SENSORS` tuple (line 174):

    ```python
    # homeassistant/components/synology_dsm/sensor.py
    EXTERNAL_USB_DISK_SENSORS: tuple[SynologyDSMSensorEntityDescription, ...] = (
        SynologyDSMSensorEntityDescription(
            api_key=SynoCoreExternalUSB.API_KEY,
            key="device_status",
            translation_key="device_status",
            entity_category=EntityCategory.DIAGNOSTIC, # Add this line
        ),
        # ...
    )
    ```

3.  **Switch (`switch.py`)**:
    *   Add `entity_category=EntityCategory.CONFIG` to the `SynologyDSMSwitchEntityDescription` for the `home_mode` switch (line 27):

    ```python
    # homeassistant/components/synology_dsm/switch.py
    SURVEILLANCE_SWITCH: tuple[SynologyDSMSwitchEntityDescription, ...] = (
        SynologyDSMSwitchEntityDescription(
            api_key=SynoSurveillanceStation.HOME_MODE_API_KEY,
            key="home_mode",
            translation_key="home_mode",
            entity_category=EntityCategory.CONFIG, # Add this line
        ),
    )
    ```

Implementing these changes will ensure that entities representing diagnostic information and configuration settings are correctly categorized in the Home Assistant UI.

_Created at 2025-05-25 11:50:25. Prompt tokens: 39207, Output tokens: 1548, Total tokens: 42816_
