# pi_hole: entity-unique-id

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [pi_hole](https://www.home-assistant.io/integrations/pi_hole/) |
| Rule   | [entity-unique-id](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-unique-id)                                                     |
| Status | **done**                                                                 |
| Reason |                                                                          |

## Overview

The `entity-unique-id` rule requires that all entities created by an integration have a unique ID. This is crucial for Home Assistant to track entities across restarts, allowing users to customize them (e.g., rename, change entity ID, assign to areas). The rule applies to all integrations that provide entities, and there are no exceptions.

The `pi_hole` integration creates entities for binary sensors, sensors, switches, and updates. Therefore, this rule applies.

The integration correctly implements unique IDs for all its entities. Each entity's unique ID is typically constructed by combining the config entry's unique ID (`entry.entry_id`, referred to as `_server_unique_id` in the entity classes) with a key specific to that entity type or instance. This ensures that each entity ID is unique across all Pi-hole instances and unique for different entities within a single Pi-hole instance.

**Evidence of Compliance:**

1.  **Base Entity Structure:**
    The `PiHoleEntity` class in `homeassistant/components/pi_hole/entity.py` is the base for all Pi-hole entities. It is initialized with a `server_unique_id`, which corresponds to the `config_entry.entry_id`. This `server_unique_id` forms the common prefix for all entity unique IDs associated with a particular Pi-hole configuration.

    ```python
    # homeassistant/components/pi_hole/entity.py
    class PiHoleEntity(CoordinatorEntity[DataUpdateCoordinator[None]]):
        def __init__(
            self,
            api: Hole,
            coordinator: DataUpdateCoordinator[None],
            name: str,
            server_unique_id: str,  # This is entry.entry_id
        ) -> None:
            super().__init__(coordinator)
            self.api = api
            self._name = name
            self._server_unique_id = server_unique_id
    ```

2.  **Binary Sensor Entities (`binary_sensor.py`):**
    `PiHoleBinarySensor` sets `_attr_unique_id` using the `_server_unique_id` and the `description.key` from its `PiHoleBinarySensorEntityDescription`.
    ```python
    # homeassistant/components/pi_hole/binary_sensor.py
    class PiHoleBinarySensor(PiHoleEntity, BinarySensorEntity):
        def __init__(
            # ...
        ) -> None:
            super().__init__(api, coordinator, name, server_unique_id)
            self.entity_description = description
            self._attr_unique_id = f"{self._server_unique_id}/{description.key}" # e.g., "entry_id/status"
    ```

3.  **Sensor Entities (`sensor.py`):**
    `PiHoleSensor` follows the same pattern, setting `_attr_unique_id` using `_server_unique_id` and `description.key`.
    ```python
    # homeassistant/components/pi_hole/sensor.py
    class PiHoleSensor(PiHoleEntity, SensorEntity):
        def __init__(
            # ...
        ) -> None:
            super().__init__(api, coordinator, name, server_unique_id)
            self.entity_description = description
            self._attr_unique_id = f"{self._server_unique_id}/{description.key}" # e.g., "entry_id/ads_blocked_today"
    ```

4.  **Switch Entity (`switch.py`):**
    `PiHoleSwitch` implements the `unique_id` property, combining `_server_unique_id` with a static string "Switch", as there's only one switch type per Pi-hole instance.
    ```python
    # homeassistant/components/pi_hole/switch.py
    class PiHoleSwitch(PiHoleEntity, SwitchEntity):
        @property
        def unique_id(self) -> str:
            """Return the unique id of the switch."""
            return f"{self._server_unique_id}/Switch" # e.g., "entry_id/Switch"
    ```

5.  **Update Entities (`update.py`):**
    `PiHoleUpdateEntity` also sets `_attr_unique_id` using `_server_unique_id` and `description.key`.
    ```python
    # homeassistant/components/pi_hole/update.py
    class PiHoleUpdateEntity(PiHoleEntity, UpdateEntity):
        def __init__(
            # ...
        ) -> None:
            super().__init__(api, coordinator, name, server_unique_id)
            self.entity_description = description
            self._attr_unique_id = f"{self._server_unique_id}/{description.key}" # e.g., "entry_id/core_update_available"
    ```

Additionally, `homeassistant/components/pi_hole/__init__.py` includes logic to migrate older unique ID formats to the current, more robust format, demonstrating attention to unique ID stability.

The consistent use of `entry.entry_id` (as `_server_unique_id`) ensures uniqueness across multiple Pi-hole devices configured in Home Assistant. The appended entity-specific key (e.g., `description.key` or "Switch") ensures uniqueness for different entities belonging to the same Pi-hole device. This pattern fully satisfies the requirements of the `entity-unique-id` rule.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-10 23:09:08. Prompt tokens: 9972, Output tokens: 1360, Total tokens: 14190._

_Report based on [`ab7f6c3`](https://github.com/home-assistant/core/tree/ab7f6c35287f43fe1207b3de4581b3bfabd49399)._

_AI can be wrong. Always verify the report and the code against the rule._
