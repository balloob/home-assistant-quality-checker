```markdown
# synology_dsm: icon-translations

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [icon-translations](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/icon-translations)                                                     |
| Status | **todo**                                                                 |

## Overview

This rule requires integrations to define entity icons using `_attr_translation_key` and an `icons.json` file, moving away from hardcoding icons in the entity's `icon` property or implementing state-based icon logic within the entity code. Icons provided automatically by the `device_class` are exempt.

The `synology_dsm` integration generally follows this rule by using `_attr_has_entity_name = True` and defining `_attr_translation_key` in most entity descriptions (`binary_sensor.py`, `sensor.py`, `switch.py`, `update.py`). It also utilizes `device_class` where appropriate (`binary_sensor.py`, `sensor.py`, `button.py`, `camera.py`), which provides default icons.

The integration includes an `icons.json` file (`homeassistant/components/synology_dsm/icons.json`) which defines icons based on translation keys. For example, the `switch` entity for `home_mode` uses `_attr_translation_key = "home_mode"` (`switch.py`), and `icons.json` correctly defines an icon under `entity.switch.home_mode`. The `sensor` entities define various `_attr_translation_key`s (e.g., `cpu_total_load`, `memory_real_usage`, `volume_status` in `sensor.py`), and `icons.json` includes entries for these under `entity.sensor`, including a state-based icon for `volume_status`. This is correct usage of the rule.

However, there is an issue with the structure of the `icons.json` file:

1.  **Binary Sensor Icons:** The icons for binary sensors defined with `translation_key` (e.g., `disk_below_remain_life_thr`, `disk_exceed_bad_sector_thr`, `status` in `binary_sensor.py`) are incorrectly defined under the `entity.sensor` key in `icons.json`. They should be under `entity.binary_sensor`.
2.  **Update Entity Icon:** The icon for the update entity defined with `translation_key = "update"` (`update.py`) is also incorrectly defined under the `entity.sensor` key in `icons.json`. It should be under `entity.update`.
3.  **Button Icons:** The button entities explicitly set the `_attr_icon` property (`button.py`, e.g., `icon="mdi:power"`). While the `icons.json` file includes a `services` section with icons for `reboot` and `shutdown`, this applies to the legacy services (`services.yaml`) and not the button *entities*. The `icons.json` file does not currently support an `entity.button` section, meaning icon translations cannot be used for button entities via this mechanism. Therefore, setting `_attr_icon` is currently necessary for custom button icons that are not provided by `device_class` (like `ButtonDeviceClass.RESTART`). While the rule discourages hardcoding `_attr_icon`, the primary focus is on moving *state-dependent* logic and standardizing icons via translations. Since button entities are stateless and `icons.json` doesn't support them, this might be considered a technical limitation rather than a strict violation of the rule's core intent. However, the ideal state would be to use translation keys for all entity types if supported.

The miscategorization of binary sensor and update entity icons in `icons.json` is a clear failure to follow the required structure for icon translations.

## Suggestions

1.  **Correct `icons.json` Structure:**
    *   Create a new key `binary_sensor` under the `entity` key in `icons.json`.
    *   Move the following keys and their definitions from `entity.sensor` to `entity.binary_sensor`:
        *   `disk_below_remain_life_thr`
        *   `disk_exceed_bad_sector_thr`
        *   `status`
    *   Create a new key `update` under the `entity` key in `icons.json`.
    *   Move the `update` key and its definition from `entity.sensor` to `entity.update`.

    Example of the corrected `icons.json` structure snippet:

    ```json
    {
      "entity": {
        "binary_sensor": {
          "disk_below_remain_life_thr": {
            "default": "mdi:checkbox-marked-circle-outline"
          },
          "disk_exceed_bad_sector_thr": {
            "default": "mdi:checkbox-marked-circle-outline"
          },
          "status": {
             "default": "mdi:checkbox-marked-circle-outline"
          }
        },
        "sensor": {
          "cpu_other_load": { /* ... */ },
          "volume_status": { /* ... */ }
          // ... rest of sensor keys ...
        },
        "switch": {
          "home_mode": {
            "default": "mdi:home-account"
          }
        },
        "update": {
          "update": {
            "default": "mdi:package-up"
          }
        }
      },
      "services": {
        "reboot": { /* ... */ },
        "shutdown": { /* ... */ }
      }
    }
    ```

2.  **Button Icons:** While hardcoding `_attr_icon` for buttons is not ideal based on the rule's reasoning, it is understandable given the apparent lack of `entity.button` support in `icons.json`. Confirm if `entity.button` is a supported domain for icon translations. If it is, migrate button icons there. If not, the current approach might be acceptable, but it slightly deviates from the rule's spirit.

_Created at 2025-05-25 11:51:58. Prompt tokens: 40267, Output tokens: 1409, Total tokens: 44228_
