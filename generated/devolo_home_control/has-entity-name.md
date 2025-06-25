# devolo_home_control: has-entity-name

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [devolo_home_control](https://www.home-assistant.io/integrations/devolo_home_control/) |
| Rule   | [has-entity-name](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/has-entity-name)                                                     |
| Status | **done**                                                                 |

## Overview

The `has-entity-name` rule applies to this integration as it creates entities across multiple platforms, including `sensor`, `switch`, `light`, `cover`, `climate`, `siren`, and `binary_sensor`.

The integration fully complies with this rule. It correctly establishes a base entity class that sets the required attribute, ensuring all entities within the integration adhere to the modern entity naming standard.

The implementation follows best practices in two key ways:

1.  **Base Class Compliance:** The base entity class, `DevoloDeviceEntity`, defined in `homeassistant/components/devolo_home_control/entity.py`, correctly sets `_attr_has_entity_name = True`. Since all other entities in the integration inherit from this class, they all meet the rule's primary requirement.

    ```python
    # homeassistant/components/devolo_home_control/entity.py
    class DevoloDeviceEntity(Entity):
        """Abstract representation of a device within devolo Home Control."""

        _attr_has_entity_name = True # Correctly set in the base class
    ```

2.  **Primary Entity Naming:** For entities that represent the main function of a device (e.g., a switch, a dimmer, a thermostat), the integration correctly sets `_attr_name = None`. This allows the entity to adopt the name of its parent device, which is the desired behavior for primary entities. This pattern is used in classes like `DevoloMultiLevelSwitchDeviceEntity` (the base for lights, covers, etc.) and `DevoloSwitch`.

    ```python
    # homeassistant/components/devolo_home_control/entity.py
    class DevoloMultiLevelSwitchDeviceEntity(DevoloDeviceEntity):
        """Representation of a multi level switch device within devolo Home Control. Something like a dimmer or a thermostat."""

        _attr_name = None # Correctly used for primary entities
    
    # homeassistant/components/devolo_home_control/switch.py
    class DevoloSwitch(DevoloDeviceEntity, SwitchEntity):
        """Representation of a switch."""

        _attr_name = None # Correctly used for primary entities
    ```

Secondary entities, such as individual sensors for a device, do not set `_attr_name`, allowing Home Assistant to correctly form a name like "Device Name Sensor Name".

Because of this well-structured implementation, the integration is fully compliant with the `has-entity-name` rule.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 18:59:38 using gemini-2.5-pro-preview-06-05. Prompt tokens: 13378, Output tokens: 679, Total tokens: 15957._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
