```markdown
# synology_dsm: entity-unavailable

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [entity-unavailable](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-unavailable)                                                     |
| Status | **done**                                                                 |
| Reason |                                                                          |

## Overview

This rule requires that entities provided by the integration are marked as unavailable when the integration cannot fetch data from the device or service. The rule provides examples for integrations using `DataUpdateCoordinator` and those updating via `async_update`.

The `synology_dsm` integration utilizes `DataUpdateCoordinator` for fetching data, which is the recommended pattern and is covered by the rule's examples. The integration defines several coordinators (`SynologyDSMCentralUpdateCoordinator`, `SynologyDSMCameraUpdateCoordinator`, `SynologyDSMSwitchUpdateCoordinator`) inheriting from `SynologyDSMUpdateCoordinator`, which itself inherits from `DataUpdateCoordinator`.

The core logic for handling availability upon communication failure is implemented within the `async_re_login_on_expired` decorator in `coordinator.py`. This decorator wraps the `_async_update_data` methods of the coordinators. It catches `SynologyDSMNotLoggedInException` and `SYNOLOGY_CONNECTION_EXCEPTIONS` (which include various API and request exceptions from the `py-synologydsm-api` library). When caught, these exceptions are wrapped in a `homeassistant.helpers.update_coordinator.UpdateFailed` exception and re-raised.

According to the Home Assistant documentation and the rule's example, raising `UpdateFailed` in `_async_update_data` is the standard way for a `DataUpdateCoordinator` to signal that an update failed due to communication issues. A `CoordinatorEntity` (which most `synology_dsm` entities inherit from via `SynologyDSMBaseEntity`) automatically sets its `available` property to `False` if the associated coordinator's last update failed (`coordinator.last_update_success` is False).

Furthermore, entities in `synology_dsm` that override the `available` property (e.g., `SynoDSMSecurityBinarySensor`, `SynoDSMSurveillanceHomeModeToggle`, `SynoDSMCamera`, `SynoDSMUtilSensor`, `SynoDSMUpdateEntity`) correctly include `super().available` in their return logic. This ensures that even if their specific condition for availability is met (e.g., the API object exists, the camera is enabled), the entity will still be marked unavailable if the underlying coordinator's data fetch failed.

For example, in `homeassistant/components/synology_dsm/camera.py`, the `SynoDSMCamera.available` property is defined as `return self.camera_data.is_enabled and super().available`. This clearly demonstrates chaining the coordinator's availability status. Similar patterns are found in other entities that override `available`.

The code correctly implements the pattern of marking entities unavailable when the primary data fetching mechanism (the coordinator update) fails due to communication issues with the Synology device, following the recommended `DataUpdateCoordinator` approach.

## Suggestions

No suggestions needed.
```

_Created at 2025-05-25 11:48:25. Prompt tokens: 39740, Output tokens: 732, Total tokens: 41951_
