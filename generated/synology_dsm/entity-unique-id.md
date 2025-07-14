```markdown
# synology_dsm: entity-unique-id

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [entity-unique-id](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-unique-id)                                                     |
| Status | **done**                                                                 |

## Overview

This rule requires that all entities provided by the integration have a unique ID. This allows Home Assistant to track entities across restarts and enables user customizations via the entity registry. There are no exceptions to this rule.

The `synology_dsm` integration applies this rule to all its entities, which include binary sensors, buttons, cameras, sensors, switches, and updates.

The base entity class `SynologyDSMBaseEntity` in `homeassistant/components/synology_dsm/entity.py` sets a unique ID using the pattern `f"{information.serial}_{description.api_key}:{description.key}"`. This incorporates the NAS serial number (which is the unique identifier for the configuration entry), the API key the entity belongs to, and a specific key for that entity type.

Derived entity classes build upon or adapt this pattern:

*   `SynologyDSMDeviceEntity` (used for storage and external USB sensors/binary sensors): Inherits from `SynologyDSMBaseEntity` and appends the device ID (disk ID, volume ID, external device name, or partition title) to the unique ID, resulting in a format like `f"{information.serial}_{description.api_key}:{description.key}_{device_id}"`. This correctly distinguishes entities for different hardware components on the same NAS.
*   `SynoDSMSurveillanceHomeModeToggle` (switch): Inherits from `SynologyDSMBaseEntity` and uses the base unique ID pattern with the specific API key and key for the home mode switch.
*   `SynoDSMCamera` (camera): Inherits from `SynologyDSMBaseEntity`. It sets a specific `SynologyDSMCameraEntityDescription` where the `key` is the string representation of the camera ID and the `api_key` is `SynoSurveillanceStation.CAMERA_API_KEY`. The base class constructor then generates the unique ID as `f"{serial}_{SynoSurveillanceStation.CAMERA_API_KEY}:{camera_id}"`, ensuring uniqueness per camera per NAS.
*   `SynologyDSMButton` (reboot, shutdown): This class does not inherit from `SynologyDSMBaseEntity` but directly sets `_attr_unique_id` in its `__init__` method using the pattern `f"{api.information.serial}_{description.key}"`. This uses the NAS serial and the specific button key (`reboot` or `shutdown`) for uniqueness.

In all cases, the unique ID is constructed using the NAS serial number (obtained from `api.information.serial`), ensuring that entities from different NAS devices connected via separate config entries have distinct unique IDs. Within a single NAS, additional identifiers (API key, entity key, device ID, camera ID) are used to guarantee uniqueness for each entity.

Therefore, the integration correctly implements unique IDs for all its entities.

## Suggestions

No suggestions needed.
```

_Created at 2025-05-25 11:46:51. Prompt tokens: 39400, Output tokens: 731, Total tokens: 41130_
