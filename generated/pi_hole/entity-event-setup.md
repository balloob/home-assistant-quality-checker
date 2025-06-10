# pi_hole: entity-event-setup

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [pi_hole](https://www.home-assistant.io/integrations/pi_hole/) |
| Rule   | [entity-event-setup](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-event-setup)                                                     |
| Status | **exempt**                                       |
| Reason | The integration uses a polling mechanism via `DataUpdateCoordinator`, and its entities do not subscribe to external, library-pushed events. |

## Overview

The `entity-event-setup` rule mandates that entities subscribing to events (e.g., from an integration library) should manage these subscriptions within the `async_added_to_hass` and `async_will_remove_from_hass` lifecycle methods. This ensures that subscriptions are active only when the entity is part of Home Assistant and are cleaned up properly to prevent memory leaks.

This rule does **not apply** to the `pi_hole` integration. Here's why:

1.  **Polling Architecture:** The `pi_hole` integration employs a polling architecture centered around the `DataUpdateCoordinator`. As seen in `homeassistant/components/pi_hole/__init__.py`, a `DataUpdateCoordinator` instance is created:
    ```python
    # homeassistant/components/pi_hole/__init__.py
    # ...
    async def async_update_data() -> None:
        """Fetch data from API endpoint."""
        try:
            await api.get_data()
            await api.get_versions()
        # ...

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        config_entry=entry,
        name=name,
        update_method=async_update_data,
        update_interval=MIN_TIME_BETWEEN_UPDATES,
    )
    # ...
    ```
    This coordinator periodically calls `api.get_data()` and `api.get_versions()` to fetch the latest state from the Pi-hole device.

2.  **CoordinatorEntity Usage:** Entities within the `pi_hole` integration (e.g., `PiHoleSensor` in `sensor.py`, `PiHoleSwitch` in `switch.py`) inherit from `PiHoleEntity`, which in turn inherits from `CoordinatorEntity` (from `homeassistant.helpers.update_coordinator`).
    ```python
    # homeassistant/components/pi_hole/entity.py
    class PiHoleEntity(CoordinatorEntity[DataUpdateCoordinator[None]]):
        # ...
    ```
    The `CoordinatorEntity` base class handles the subscription to updates from its `DataUpdateCoordinator`. It uses `async_added_to_hass` to add a listener to the coordinator and `async_on_remove` (which is called by `async_will_remove_from_hass`) to clean up this listener. This is an internal Home Assistant mechanism for entities to react to new data fetched by the coordinator.

3.  **No Direct Library Event Subscription:** The entities in the `pi_hole` integration do not directly subscribe to an event stream provided by the `hole` library. The `hole` library is used to make HTTP requests to the Pi-hole API (polling), not for receiving pushed events. The `iot_class` for `pi_hole` is `local_polling` as specified in `manifest.json`, further confirming this design.

The rule `entity-event-setup` is targeted at integrations where entities subscribe to *external* event sources, such as a library that pushes updates to Home Assistant (e.g., via WebSockets or a callback mechanism). Since `pi_hole` entities rely on the `DataUpdateCoordinator` for state updates and do not manage their own subscriptions to external library events, this rule is not applicable.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-10 23:08:28. Prompt tokens: 10238, Output tokens: 869, Total tokens: 13201._

_Report based on [`ab7f6c3`](https://github.com/home-assistant/core/tree/ab7f6c35287f43fe1207b3de4581b3bfabd49399)._

_AI can be wrong. Always verify the report and the code against the rule._
