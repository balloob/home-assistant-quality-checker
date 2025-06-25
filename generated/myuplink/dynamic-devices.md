# myuplink: dynamic-devices

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [myuplink](https://www.home-assistant.io/integrations/myuplink/) |
| Rule   | [dynamic-devices](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/dynamic-devices)                                                     |
| Status | **todo**                                                                     |

## Overview

The `dynamic-devices` rule requires that integrations automatically detect and add new devices that become available after the initial Home Assistant setup. This rule applies to `myuplink` as it is a cloud-polling integration where users can add new heat pumps or other devices to their account at any time, and these should appear in Home Assistant without a restart.

The `myuplink` integration currently does not follow this rule. During startup, it correctly fetches all available devices and creates the corresponding device entries (in `__init__.py`) and entities (in platform setup files like `sensor.py`, `switch.py`, etc.). However, this process only runs once.

The integration uses a `DataUpdateCoordinator` to periodically refresh data from the myUplink API, but it lacks the listener mechanism to act on this new data. Specifically, there is no `coordinator.async_add_listener` implementation that checks for new devices or entities in the refreshed data and then calls `device_registry.async_get_or_create` or `async_add_entities` for them.

As a result, if a user adds a new device to their myUplink account, it will not appear in Home Assistant until the integration is reloaded or Home Assistant is restarted.

## Suggestions

To comply with this rule, the integration needs to be refactored to use coordinator listeners for discovering and adding new devices and entities dynamically. This involves changes in `__init__.py` for device creation and in each platform file (e.g., `sensor.py`, `binary_sensor.py`) for entity creation.

### 1. Dynamic Device Creation

In `homeassistant/components/myuplink/__init__.py`, the `create_devices` function should be converted into a listener that is attached to the coordinator. This ensures that new devices reported by the API are added to the device registry automatically.

**Current Code in `__init__.py`:**
```python
async def async_setup_entry(
    hass: HomeAssistant, config_entry: MyUplinkConfigEntry
) -> bool:
    # ...
    await coordinator.async_config_entry_first_refresh()
    config_entry.runtime_data = coordinator

    # Update device registry
    create_devices(hass, config_entry, coordinator)

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    # ...

@callback
def create_devices(
    hass: HomeAssistant,
    config_entry: MyUplinkConfigEntry,
    coordinator: MyUplinkDataCoordinator,
) -> None:
    # ...
```

**Suggested Change in `__init__.py`:**
```python
async def async_setup_entry(
    hass: HomeAssistant, config_entry: MyUplinkConfigEntry
) -> bool:
    # ...
    await coordinator.async_config_entry_first_refresh()
    config_entry.runtime_data = coordinator

    device_registry = dr.async_get(hass)

    @callback
    def _create_or_update_devices() -> None:
        """Create or update devices from coordinator data."""
        for system in coordinator.data.systems:
            devices_in_system = [x.id for x in system.devices]
            for device_id, device in coordinator.data.devices.items():
                if device_id in devices_in_system:
                    device_registry.async_get_or_create(
                        config_entry_id=config_entry.entry_id,
                        identifiers={(DOMAIN, device_id)},
                        name=get_system_name(system),
                        manufacturer=get_manufacturer(device),
                        model=get_model(device),
                        sw_version=device.firmwareCurrent,
                        serial_number=device.product_serial_number,
                    )

    # Run once and then register as a listener
    _create_or_update_devices()
    config_entry.async_on_unload(
        coordinator.async_add_listener(_create_or_update_devices)
    )

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    # ...
```

### 2. Dynamic Entity Creation

A similar pattern must be applied to each platform's `async_setup_entry` function. This will ensure that when a new device appears, its entities are also created. Below is an example for `sensor.py`. This pattern should be replicated for `binary_sensor.py`, `number.py`, `select.py`, `switch.py`, and `update.py`.

**Current Code in `sensor.py`:**
```python
async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyUplinkConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up myUplink sensor."""
    entities: list[SensorEntity] = []
    coordinator = config_entry.runtime_data

    # This loop runs only once at setup
    for device_id, point_data in coordinator.data.points.items():
        for point_id, device_point in point_data.items():
            # ... entity creation logic ...
            entities.append(...)

    async_add_entities(entities)
```

**Suggested Change in `sensor.py`:**
```python
async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyUplinkConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up myUplink sensor."""
    coordinator: MyUplinkDataCoordinator = config_entry.runtime_data
    known_entities: set[str] = set()

    @callback
    def _discover_entities() -> None:
        """Discover and add new sensor entities."""
        new_entities: list[SensorEntity] = []

        for device_id, point_data in coordinator.data.points.items():
            for point_id, device_point in point_data.items():
                if skip_entity(device_point.category, device_point):
                    continue
                if find_matching_platform(device_point) != Platform.SENSOR:
                    continue
                
                # Check for main entity
                main_uid = f"{device_id}-{point_id}"
                if main_uid not in known_entities:
                    # ... (Existing logic to create the main sensor entity)
                    description = get_description(device_point)
                    entity_class = MyUplinkDevicePointSensor
                    # Ignore sensors without a description that provide non-numeric values
                    if description is None and not isinstance(device_point.value, (int, float)):
                        continue
                    
                    if description is not None and description.device_class == SensorDeviceClass.ENUM:
                        entity_class = MyUplinkEnumSensor
                        
                        # Check for associated raw entity
                        raw_uid = f"{main_uid}-raw"
                        if raw_uid not in known_entities:
                             new_entities.append(
                                 MyUplinkEnumRawSensor(...)
                             )
                             known_entities.add(raw_uid)

                    new_entities.append(
                        entity_class(...)
                    )
                    known_entities.add(main_uid)

        if new_entities:
            async_add_entities(new_entities)

    # Initial discovery and listener registration
    _discover_entities()
    config_entry.async_on_unload(coordinator.async_add_listener(_discover_entities))
```

By implementing these changes, the `myuplink` integration will become fully dynamic, providing a much better user experience when devices are added to their account.

---

_Created at 2025-06-25 18:52:38 using gemini-2.5-pro-preview-06-05. Prompt tokens: 17242, Output tokens: 1865, Total tokens: 22766._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
