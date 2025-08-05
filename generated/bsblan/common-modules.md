# bsblan: common-modules

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [bsblan](https://www.home-assistant.io/integrations/bsblan/) |
| Rule   | [common-modules](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/common-modules)                                                     |
| Status | **done**                                                                 |

## Overview

The `common-modules` rule applies to this integration because it uses a `DataUpdateCoordinator` to manage data fetching and provides multiple entity platforms (`climate`, `sensor`, `water_heater`) which benefit from a common base entity.

The `bsblan` integration fully complies with this rule by structuring its code according to the recommended patterns:

1.  **Coordinator Module**: The `DataUpdateCoordinator` is correctly implemented in its own dedicated file.
    *   The file `coordinator.py` exists.
    *   It contains the `BSBLanUpdateCoordinator` class, which inherits from `DataUpdateCoordinator`.

    ```python
    # homeassistant/components/bsblan/coordinator.py

    class BSBLanUpdateCoordinator(DataUpdateCoordinator[BSBLanCoordinatorData]):
        """The BSB-Lan update coordinator."""
        # ... implementation ...
    ```

2.  **Base Entity Module**: A base entity class is defined in a separate `entity.py` file to reduce code duplication across platforms.
    *   The file `entity.py` exists.
    *   It defines the `BSBLanEntity` class, which inherits from `CoordinatorEntity`.

    ```python
    # homeassistant/components/bsblan/entity.py

    class BSBLanEntity(CoordinatorEntity[BSBLanUpdateCoordinator]):
        """Defines a base BSBLan entity."""
        # ... implementation ...
    ```

3.  **Platform Usage**: The entities in the platform files (`climate.py`, `sensor.py`, `water_heater.py`) correctly inherit from this base `BSBLanEntity`, demonstrating proper use of the common module. For example:

    ```python
    # homeassistant/components/bsblan/climate.py
    from .entity import BSBLanEntity
    # ...
    class BSBLANClimate(BSBLanEntity, ClimateEntity):
        # ...
    ```

This structure enhances code consistency and maintainability, aligning perfectly with the rule's goals.

## Suggestions

No suggestions needed.

---

_Created at 2025-08-05 09:35:43 using gemini-2.5-pro. Prompt tokens: 10914, Output tokens: 558, Total tokens: 12377._

_Report based on [`ee9ff71`](https://github.com/home-assistant/core/tree/ee9ff717e0d36ca02bf52a242acd3a47359eae61)._

_AI can be wrong. Always verify the report and the code against the rule._
