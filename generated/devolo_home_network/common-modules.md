# devolo_home_network: common-modules

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [devolo_home_network](https://www.home-assistant.io/integrations/devolo_home_network/) |
| Rule   | [common-modules](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/common-modules)                                                     |
| Status | **done**                                                                 |

## Overview

The `common-modules` rule applies to this integration because it uses both the `DataUpdateCoordinator` pattern to manage data fetching and base entity classes to reduce code duplication across its platforms.

The integration fully complies with this rule.

1.  **Coordinator Module:** The integration correctly centralizes all its `DataUpdateCoordinator` implementations in `coordinator.py`.
    *   It defines a base coordinator, `DevoloDataUpdateCoordinator`, which handles common logic like error handling and device version updates.
    *   It then defines several specialized coordinators (e.g., `DevoloFirmwareUpdateCoordinator`, `DevoloLogicalNetworkCoordinator`, `DevoloWifiConnectedStationsGetCoordinator`) that inherit from this base class. Each coordinator is responsible for a specific API endpoint. This is an excellent implementation of the coordinator pattern.

    ```python
    # homeassistant/components/devolo_home_network/coordinator.py

    class DevoloDataUpdateCoordinator[_DataT](DataUpdateCoordinator[_DataT]):
        """Class to manage fetching data from devolo Home Network devices."""
        # ...

    class DevoloFirmwareUpdateCoordinator(DevoloDataUpdateCoordinator[UpdateFirmwareCheck]):
        """Class to manage fetching data from the UpdateFirmwareCheck endpoint."""
        # ...

    # ... and many other coordinators
    ```

2.  **Base Entity Module:** The integration correctly places its base entity classes in `entity.py`.
    *   `DevoloEntity` serves as the fundamental base class, handling the common `device_info` setup for all entities.
    *   `DevoloCoordinatorEntity` builds upon `DevoloEntity` and `CoordinatorEntity`, creating a convenient base for all entities that subscribe to a coordinator.

    ```python
    # homeassistant/components/devolo_home_network/entity.py

    class DevoloEntity(Entity):
        """Representation of a devolo home network device."""

        _attr_has_entity_name = True

        def __init__(
            self,
            entry: DevoloHomeNetworkConfigEntry,
        ) -> None:
            # ... sets up self._attr_device_info ...

    class DevoloCoordinatorEntity[_DataT: _DataType](
        CoordinatorEntity[DevoloDataUpdateCoordinator[_DataT]], DevoloEntity
    ):
        """Representation of a coordinated devolo home network device."""
        # ...
    ```

All entity platforms (e.g., `sensor.py`, `switch.py`, `update.py`) correctly import from and inherit these base classes from `entity.py`, demonstrating proper adherence to the rule and promoting a clean, consistent, and maintainable codebase.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 19:02:47 using gemini-2.5-pro. Prompt tokens: 18613, Output tokens: 711, Total tokens: 20764._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
