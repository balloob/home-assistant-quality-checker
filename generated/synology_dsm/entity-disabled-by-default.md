```markdown
# synology_dsm: entity-disabled-by-default

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [entity-disabled-by-default](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-disabled-by-default)                                                     |
| Status | **todo**                                                                 |
| Reason |                                                                          |

## Overview

This rule encourages integrations to disable less popular or noisy entities by default to reduce resource usage, particularly state history size. The `synology_dsm` integration provides a variety of entities, ranging from core metrics like CPU usage and storage space to more diagnostic or detailed information like specific memory pools or disk temperatures.

The integration does follow the rule for some entities. For example, in `binary_sensor.py`, diagnostic storage binary sensors like `disk_exceed_bad_sector_thr` and `disk_below_remain_life_thr` are correctly marked with `entity_registry_enabled_default=False`. In `sensor.py`, certain utilization sensors (`cpu_other_load`, `cpu_system_load`, `cpu_1min_load`, `memory_size`, `memory_cached`), storage total size (`volume_size_total`, `device_size_total`), disk SMART status (`disk_smart_status`), maximum volume temperature (`volume_disk_temp_max`), external USB total size (`device_size_total`), and the uptime sensor (`uptime`) are also appropriately disabled by default.

However, several entities that appear to be less popular or potentially noisy are currently enabled by default (by omitting `entity_registry_enabled_default` or implicitly setting it to `True`). These include detailed memory statistics, average/specific disk temperatures, and device temperature. Disabling these by default would further align the integration with the rule's goal of minimizing the default footprint for typical users while still allowing advanced users to enable them if needed.

Based on the analysis of the provided code, the integration partially implements the rule but could disable more entities by default. Therefore, the status is marked as `todo`.

## Suggestions

To fully comply with the `entity-disabled-by-default` rule, the following entities should be disabled by default by adding `_attr_entity_registry_enabled_default = False` to their respective `SynologyDSMSensorEntityDescription` definitions in `homeassistant/components/synology_dsm/sensor.py`:

1.  **Detailed Memory Sensors:** The `UTILISATION_SENSORS` list contains several detailed memory metrics (`memory_available_swap`, `memory_available_real`, `memory_total_swap`, `memory_total_real`) that are less commonly needed by default compared to the overall usage.
    ```diff
    --- a/homeassistant/components/synology_dsm/sensor.py
    +++ b/homeassistant/components/synology_dsm/sensor.py
    @@ -74,6 +74,7 @@
         suggested_unit_of_measurement=UnitOfInformation.MEGABYTES,
         suggested_display_precision=1,
         device_class=SensorDeviceClass.DATA_SIZE,
+        entity_registry_enabled_default=False,
         state_class=SensorStateClass.MEASUREMENT,
     ),
     SynologyDSMSensorEntityDescription(
@@ -83,6 +84,7 @@
         suggested_unit_of_measurement=UnitOfInformation.MEGABYTES,
         suggested_display_precision=1,
         device_class=SensorDeviceClass.DATA_SIZE,
+        entity_registry_enabled_default=False,
         state_class=SensorStateClass.MEASUREMENT,
     ),
     SynologyDSMSensorEntityDescription(
@@ -100,6 +102,7 @@
         suggested_unit_of_measurement=UnitOfInformation.MEGABYTES,
         suggested_display_precision=1,
         device_class=SensorDeviceClass.DATA_SIZE,
+        entity_registry_enabled_default=False,
         state_class=SensorStateClass.MEASUREMENT,
     ),
     SynologyDSMSensorEntityDescription(
@@ -109,6 +112,7 @@
         suggested_unit_of_measurement=UnitOfInformation.MEGABYTES,
         suggested_display_precision=1,
         device_class=SensorDeviceClass.DATA_SIZE,
+        entity_registry_enabled_default=False,
         state_class=SensorStateClass.MEASUREMENT,
     ),
     SynologyDSMSensorEntityDescription(

    ```

2.  **Temperature Sensors:** Temperature readings (`volume_disk_temp_avg`, `disk_temp`, `temperature`) are often considered diagnostic and can be noisy, similar to the `volume_disk_temp_max` sensor which is already disabled.
    ```diff
    --- a/homeassistant/components/synology_dsm/sensor.py
    +++ b/homeassistant/components/synology_dsm/sensor.py
    @@ -142,6 +142,7 @@
         native_unit_of_measurement=UnitOfTemperature.CELSIUS,
         device_class=SensorDeviceClass.TEMPERATURE,
         entity_category=EntityCategory.DIAGNOSTIC,
+        entity_registry_enabled_default=False,
     ),
     SynologyDSMSensorEntityDescription(
         api_key=SynoStorage.API_KEY,
@@ -168,6 +169,7 @@
         device_class=SensorDeviceClass.TEMPERATURE,
         state_class=SensorStateClass.MEASUREMENT,
         entity_category=EntityCategory.DIAGNOSTIC,
+        entity_registry_enabled_default=False,
     ),
 )
 EXTERNAL_USB_DISK_SENSORS: tuple[SynologyDSMSensorEntityDescription, ...] = (
@@ -205,6 +207,7 @@
         suggested_unit_of_measurement=UnitOfInformation.GIBIBYTES,
         suggested_display_precision=2,
         device_class=SensorDeviceClass.DATA_SIZE,
+        entity_registry_enabled_default=False,
         state_class=SensorStateClass.MEASUREMENT,
     ),
     SynologyDSMSensorEntityDescription(
@@ -229,6 +232,7 @@
         native_unit_of_measurement=UnitOfTemperature.CELSIUS,
         device_class=SensorDeviceClass.TEMPERATURE,
         state_class=SensorStateClass.MEASUREMENT,
+        entity_registry_enabled_default=False,
         entity_category=EntityCategory.DIAGNOSTIC,
     ),
     SynologyDSMSensorEntityDescription(

    ```

3.  **External USB Partition Total Size:** This sensor (`partition_size_total`) seems inconsistent with other "total size" sensors (`volume_size_total`, `device_size_total`) which are already disabled by default.
    ```diff
    --- a/homeassistant/components/synology_dsm/sensor.py
    +++ b/homeassistant/components/synology_dsm/sensor.py
    @@ -195,6 +195,7 @@
         suggested_unit_of_measurement=UnitOfInformation.GIBIBYTES,
         suggested_display_precision=2,
         device_class=SensorDeviceClass.DATA_SIZE,
+        entity_registry_enabled_default=False,
         state_class=SensorStateClass.MEASUREMENT,
     ),
     SynologyDSMSensorEntityDescription(

    ```

Applying these changes will ensure that only the most essential and commonly used entities are enabled by default, providing a better out-of-the-box experience for users who may not need detailed diagnostics or less popular metrics visible and tracked in their Home Assistant history.
```

_Created at 2025-05-25 11:51:03. Prompt tokens: 39545, Output tokens: 1821, Total tokens: 43971_
