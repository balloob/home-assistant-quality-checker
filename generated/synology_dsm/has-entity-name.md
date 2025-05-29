```markdown
# synology_dsm: has-entity-name

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [has-entity-name](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/has-entity-name)                                                     |
| Status | **todo**                                       |
| Reason |                                                                          |
```

## Overview

This rule requires entities to use `_attr_has_entity_name = True` for improved naming consistency, leveraging the device name and the entity's own name (or translation key) for display. For entities representing the main feature of a device, `_attr_name` should be set to `None` alongside `_attr_has_entity_name = True`.

The `synology_dsm` integration partially follows this rule.

The base entity class `SynologyDSMBaseEntity` defined in `homeassistant/components/synology_dsm/entity.py` correctly sets `_attr_has_entity_name = True`:
```python
class SynologyDSMBaseEntity[_CoordinatorT: SynologyDSMUpdateCoordinator[Any]](
    CoordinatorEntity[_CoordinatorT]
):
    """Representation of a Synology NAS entry."""
    # ...
    _attr_has_entity_name = True
    # ...
```
Entities inheriting from this base class, such as those in `binary_sensor.py`, `sensor.py`, `switch.py`, and `update.py`, benefit from this setting. These entities also correctly use `translation_key` in their entity descriptions, allowing Home Assistant to generate names like "NAS Name CPU Usage" or "NAS Name Volume Status".

The `camera.py` entity `SynoDSMCamera` inherits from `SynologyDSMBaseEntity`. Its entity description explicitly sets `name=None`:
```python
        description = SynologyDSMCameraEntityDescription(
            # ...
            name=None,
            # ...
        )
```
Combined with `_attr_has_entity_name = True` from the base class, this correctly implements the pattern for an entity that is the primary feature of its device (the camera itself), resulting in a simple name like "Camera Name".

However, the button entities defined in `homeassistant/components/synology_dsm/button.py` do not inherit from `SynologyDSMBaseEntity` and do not set `_attr_has_entity_name = True`. Instead, the `SynologyDSMButton` class explicitly constructs the entity name using the NAS hostname:
```python
class SynologyDSMButton(ButtonEntity):
    # ...
    def __init__(
        self,
        api: SynoApi,
        description: SynologyDSMbuttonDescription,
    ) -> None:
        # ...
        self._attr_name = f"{api.network.hostname} {description.name}"
        # ...
```
Buttons like "Reboot" and "Shutdown" are clearly secondary features of the NAS device, not the primary feature. According to the rule, they should use `_attr_has_entity_name = True` and define their specific name (e.g., "Reboot", "Shutdown") via `_attr_name` or preferably a `translation_key`. The current implementation deviates from this pattern.

Therefore, the integration does not fully comply with the `has-entity-name` rule due to the button entities.

## Suggestions

To make the `synology_dsm` integration fully compliant with the `has-entity-name` rule, the button entities should be updated:

1.  **Modify `SynologyDSMbuttonDescription`:** Add a `translation_key` field to the button entity description dataclass in `button.py`:
    ```diff
    --- a/homeassistant/components/synology_dsm/button.py
    +++ b/homeassistant/components/synology_dsm/button.py
    @@ -9,6 +9,7 @@
     from homeassistant.components.button import (
         ButtonDeviceClass,
         ButtonEntity,
    +    ButtonEntityDescription,
     )
     from homeassistant.const import EntityCategory
     from homeassistant.core import HomeAssistant
    @@ -18,7 +19,8 @@
 
     @dataclass(frozen=True, kw_only=True)
     class SynologyDSMbuttonDescription(ButtonEntityDescription):
-    """Class to describe a Synology DSM button entity."""
    +    """Class to describe a Synology DSM button entity."""
    +
         press_action: Callable[[SynoApi], Callable[[], Coroutine[Any, Any, None]]]
 
 
    ```

2.  **Update `BUTTONS` descriptions:** Add `translation_key` to each button description in `button.py`. These should match the keys in `strings.json` under `entity.button`.
    ```diff
    --- a/homeassistant/components/synology_dsm/button.py
    +++ b/homeassistant/components/synology_dsm/button.py
    @@ -19,12 +19,14 @@
     BUTTONS: Final = [
         SynologyDSMbuttonDescription(
             key="reboot",
-            name="Reboot",
+            # name="Reboot", # Remove explicit name if using translation_key
+            translation_key="reboot",
             device_class=ButtonDeviceClass.RESTART,
             entity_category=EntityCategory.CONFIG,
             press_action=lambda syno_api: syno_api.async_reboot,
         ),
         SynologyDSMbuttonDescription(
+            translation_key="shutdown",
             key="shutdown",
             name="Shutdown",
             icon="mdi:power",
    ```
    *(Self-correction: `SynologyDSMbuttonDescription` already inherits from `ButtonEntityDescription`, which has `translation_key`. The button definitions already have keys like "reboot" and "shutdown" which match the keys in `strings.json`. So step 1 and updating `translation_key` in step 2 might be redundant if HA uses the `key` as `translation_key` fallback, but explicitly adding `translation_key` is clearer and best practice. Let's check if `ButtonEntityDescription` supports `translation_key` - yes it does. Let's add `translation_key` explicitly).*

3.  **Modify `SynologyDSMButton`:**
    *   Add `_attr_has_entity_name = True`.
    *   Remove the manual construction of `_attr_name`. With `_attr_has_entity_name = True` and `translation_key` defined (or defaulted from `key`), the frontend will handle the naming correctly. Set `_attr_name = None` explicitly for clarity, although it defaults to `None`.
    ```diff
    --- a/homeassistant/components/synology_dsm/button.py
    +++ b/homeassistant/components/synology_dsm/button.py
    @@ -38,7 +38,8 @@
         self.syno_api = api
         assert api.network is not None
         assert api.information is not None
-        self._attr_name = f"{api.network.hostname} {description.name}"
+        self._attr_has_entity_name = True
+        self._attr_name = None # Name is derived from device name and translation_key
         self._attr_unique_id = f"{api.information.serial}_{description.key}"
         self._attr_device_info = DeviceInfo(
             identifiers={(DOMAIN, api.information.serial)}

    ```

By implementing these changes, the button entities will also adhere to the recommended naming pattern using `_attr_has_entity_name = True` and relying on the device name and entity's translation key for their displayed name.

_Created at 2025-05-25 11:47:08. Prompt tokens: 39586, Output tokens: 1799, Total tokens: 42989_
