# geocaching: has-entity-name

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [geocaching](https://www.home-assistant.io/integrations/geocaching/) |
| Rule   | [has-entity-name](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/has-entity-name)                                                     |
| Status | **done**                                                                 |
| Reason |                                                                          |

## Overview

The `has-entity-name` rule applies to this integration because it creates sensor entities. The integration fully complies with this rule.

The `GeocachingSensor` entity class, defined in `homeassistant/components/geocaching/sensor.py`, correctly sets the class attribute `_attr_has_entity_name = True`.

```python
# homeassistant/components/geocaching/sensor.py

class GeocachingSensor(
    CoordinatorEntity[GeocachingDataUpdateCoordinator], SensorEntity
):
    """Representation of a Sensor."""

    entity_description: GeocachingSensorEntityDescription
    _attr_has_entity_name = True
...
```

This ensures that the entity's name will be combined with its device's name for a better user experience. For example, if the device is named "Geocaching johndoe", an entity with the name "Total finds" will be displayed as "Geocaching johndoe Total finds".

The individual name for each sensor is set via the modern entity description pattern. Each `GeocachingSensorEntityDescription` has a `translation_key` which corresponds to an entry in `strings.json`, providing a distinct name for each sensor (e.g., "Total finds", "Favorite points").

This is a complete and correct implementation of the `has-entity-name` pattern.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 18:49:28 using gemini-2.5-pro-preview-06-05. Prompt tokens: 5867, Output tokens: 424, Total tokens: 8410._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
