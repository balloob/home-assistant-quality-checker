# synology_dsm: common-modules

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [common-modules](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/common-modules) |
| Status | **done**                                                                 |

## Overview

This rule requires common patterns like DataUpdateCoordinators and base entity classes to be placed in dedicated `coordinator.py` and `entity.py` files, respectively.

The `synology_dsm` integration follows this rule.

*   The `homeassistant/components/synology_dsm/coordinator.py` file contains the base data coordinator class `SynologyDSMUpdateCoordinator`, which inherits from `DataUpdateCoordinator`, and specific coordinator implementations like `SynologyDSMCentralUpdateCoordinator`, `SynologyDSMCameraUpdateCoordinator`, and `SynologyDSMSwitchUpdateCoordinator`. This aligns with the rule's requirement for placing coordinators in `coordinator.py`.

    ```python
    # homeassistant/components/synology_dsm/coordinator.py
    class SynologyDSMUpdateCoordinator[_DataT](DataUpdateCoordinator[_DataT]):
        """DataUpdateCoordinator base class for synology_dsm."""
        # ... initialization and methods ...
    ```

*   The `homeassistant/components/synology_dsm/entity.py` file defines the base entity class `SynologyDSMBaseEntity`, which inherits from `CoordinatorEntity`. It also defines `SynologyDSMDeviceEntity`, another base class used for device-specific entities like disks and volumes, inheriting from `SynologyDSMBaseEntity`. This fulfills the requirement for placing base entities in `entity.py`.

    ```python
    # homeassistant/components/synology_dsm/entity.py
    class SynologyDSMBaseEntity[_CoordinatorT: SynologyDSMUpdateCoordinator[Any]](
        CoordinatorEntity[_CoordinatorT]
    ):
        """Representation of a Synology NAS entry."""
        # ... initialization and properties ...

    class SynologyDSMDeviceEntity(
        SynologyDSMBaseEntity[SynologyDSMCentralUpdateCoordinator]
    ):
        """Representation of a Synology NAS disk or volume entry."""
        # ... initialization and properties ...
    ```

Platform files (`binary_sensor.py`, `sensor.py`, `switch.py`, `camera.py`) correctly import and inherit from these base classes (`SynologyDSMBaseEntity`, `SynologyDSMDeviceEntity`) and utilize the coordinator classes, demonstrating the intended use of these common modules.

The integration also uses a `common.py` file to house the `SynoApi` class, which wraps the communication with the underlying Python library and manages API sessions and updates, and a helper function `raise_config_entry_auth_error`. This is a standard and acceptable use of a `common` module for shared utility code that doesn't fit the specific "coordinator" or "base entity" patterns but is used across multiple parts of the integration.

## Suggestions

No suggestions needed. The integration correctly uses `coordinator.py` and `entity.py` for their intended purposes.

_Created at 2025-05-25 11:46:16. Prompt tokens: 39412, Output tokens: 718, Total tokens: 41034_
