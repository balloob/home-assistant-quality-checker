```markdown
# synology_dsm: entity-translations

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [entity-translations](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-translations) |
| Status | **todo**                                                                 |

## Overview

This rule requires entities provided by the integration to have translated names using `_attr_has_entity_name = True` and `_attr_translation_key` pointing to a key in the `strings.json` file, or by leveraging `device_class` for certain platforms if the device class name is suitable.

The `synology_dsm` integration largely follows this pattern.

The base entity class `SynologyDSMBaseEntity` in `homeassistant/components/synology_dsm/entity.py` correctly sets `_attr_has_entity_name = True`.

*   **Binary Sensors (`binary_sensor.py`):** The entity descriptions `SynologyDSMBinarySensorEntityDescription` define `translation_key`, and these keys (`status`, `disk_exceed_bad_sector_thr`, `disk_below_remain_life_thr`) exist in the `strings.json` file under `entity.binary_sensor`. This is compliant.
*   **Sensors (`sensor.py`):** The entity descriptions `SynologyDSMSensorEntityDescription` define `translation_key`, and these keys exist in the `strings.json` file under `entity.sensor`. This is compliant. Some sensors also define `device_class`, which is handled correctly alongside `translation_key`.
*   **Switches (`switch.py`):** The entity description `SynologyDSMSwitchEntityDescription` defines `translation_key`, and the key (`home_mode`) exists in the `strings.json` file under `entity.switch`. This is compliant.
*   **Updates (`update.py`):** The entity description `SynologyDSMUpdateEntityEntityDescription` defines `translation_key`, and the key (`update`) exists in the `strings.json` file under `entity.update`. This is compliant.
*   **Cameras (`camera.py`):** The entity description `SynologyDSMCameraEntityDescription` sets `name=None`. Since the base class `SynologyDSMBaseEntity` sets `_attr_has_entity_name = True`, the camera entities will derive their name from the device. The `device_info` for camera entities in `SynoDSMCamera` sets the device name using `self.camera_data.name`. This is compliant with the pattern of naming entities after the device when `_attr_has_entity_name = True` and no `_attr_translation_key` is set.
*   **Buttons (`button.py`):** The `SynologyDSMButton` class does *not* inherit from `SynologyDSMBaseEntity`. It manually constructs the entity name using `self._attr_name = f"{api.network.hostname} {description.name}"`, where `description.name` is a hardcoded English string ("Reboot", "Shutdown") from the `BUTTONS` list. It does not use `_attr_has_entity_name` or `_attr_translation_key`. This violates the rule, as the entity name is not translatable via the standard mechanism.

Due to the button entities not following the required translation pattern, the integration does not fully comply with the rule.

## Suggestions

To make the `synology_dsm` integration fully compliant with the `entity-translations` rule, the button entities need to be updated:

1.  **Modify `homeassistant/components/synology_dsm/button.py`:**
    *   Have the `SynologyDSMButton` class inherit from `SynologyDSMBaseEntity[SynologyDSMCentralUpdateCoordinator]` to automatically gain `_attr_has_entity_name = True` and other base attributes. This might require adjusting the `__init__` signature or passing necessary arguments to the base class constructor (like `api` and a coordinator, although buttons don't typically need a coordinator for state updates, a dummy one or finding a suitable base might be needed, or alternatively, explicitly set `_attr_has_entity_name = True` in `SynologyDSMButton` if inheriting from the main base class isn't straightforward).
    *   Add a `translation_key: str` attribute to the `SynologyDSMbuttonDescription` dataclass.
    *   Update the `BUTTONS` list to use `translation_key` instead of `name` (e.g., `translation_key="reboot"`, `translation_key="shutdown"`).
    *   Remove the line `self._attr_name = f"{api.network.hostname} {description.name}"` from the `SynologyDSMButton.__init__` method. Home Assistant will automatically use the device name (from the inherited `_attr_device_info`) and the entity's translated name (from `translation_key`).

2.  **Modify `homeassistant/components/synology_dsm/strings.json`:**
    *   Add a `button` section under `entity`.
    *   Define the `name` for the new button `translation_key`s.

    ```json
    {
      "entity": {
        ...
        "button": {
          "reboot": {
            "name": "Reboot"
          },
          "shutdown": {
            "name": "Shutdown"
          }
        },
        ...
      },
      ...
    }
    ```

By making these changes, the button entities will use the standard translation mechanism, ensuring their names are translatable like other entities in the integration.

_Created at 2025-05-25 11:51:17. Prompt tokens: 39542, Output tokens: 1299, Total tokens: 42338_
