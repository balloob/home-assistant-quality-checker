# bsblan: has-entity-name
| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [bsblan](https://www.home-assistant.io/integrations/bsblan/) |
| Rule   | [has-entity-name](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/has-entity-name)                                                     |
| Status | **done**                                                                 |

## Overview
The `has-entity-name` rule applies to this integration as it creates entities for the `climate`, `sensor`, and `water_heater` platforms. The integration correctly and fully follows this rule.

A base entity class, `BSBLanEntity`, is defined in `homeassistant/components/bsblan/entity.py`. This class sets the required attribute for all inheriting entities:

```python
# homeassistant/components/bsblan/entity.py
class BSBLanEntity(CoordinatorEntity[BSBLanUpdateCoordinator]):
    """Defines a base BSBLan entity."""

    _attr_has_entity_name = True
```

All entities within the integration (`BSBLANClimate`, `BSBLanSensor`, `BSBLANWaterHeater`) inherit from this base class, ensuring `_attr_has_entity_name` is set to `True` by default.

The integration further demonstrates correct implementation of the naming strategy:

1.  **Main Feature Entities:** For the `climate` and `water_heater` entities, which represent the main functions of the device, `_attr_name` is explicitly set to `None`. This correctly results in the entity adopting the device's name.

    ```python
    # homeassistant/components/bsblan/climate.py
    class BSBLANClimate(BSBLanEntity, ClimateEntity):
        _attr_name = None
    
    # homeassistant/components/bsblan/water_heater.py
    class BSBLANWaterHeater(BSBLanEntity, WaterHeaterEntity):
        _attr_name = None
    ```

2.  **Specific Feature Entities:** For `sensor` entities, `_attr_name` is not set, allowing the name to be derived from their `entity_description`. This, combined with `_attr_has_entity_name = True`, produces the desired `"<Device Name> <Entity Name>"` format (e.g., "BSB-Lan Outside Temperature").

This comprehensive and consistent implementation across all platforms demonstrates a full understanding and adherence to the `has-entity-name` rule.

---

_Created at 2025-08-05 09:37:38 using gemini-2.5-pro. Prompt tokens: 11088, Output tokens: 578, Total tokens: 13157._

_Report based on [`ee9ff71`](https://github.com/home-assistant/core/tree/ee9ff717e0d36ca02bf52a242acd3a47359eae61)._

_AI can be wrong. Always verify the report and the code against the rule._
