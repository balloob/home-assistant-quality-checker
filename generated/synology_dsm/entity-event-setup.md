```markdown
# synology_dsm: entity-event-setup

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [entity-event-setup](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-event-setup)                                                     |
| Status | **done**                                                                 |
| Reason |                                                                          |
```

## Overview

This rule requires that entities needing to subscribe to events (e.g., from the integration library) do so in the `async_added_to_hass` method and unsubscribe in the `async_will_remove_from_hass` method. A common and recommended way to achieve this is by using `self.async_on_remove()` in `async_added_to_hass`, which takes a callable that performs the cleanup (unsubscription).

This integration uses a polling-based approach managed by coordinators (`SynologyDSMCentralUpdateCoordinator`, `SynologyDSMCameraUpdateCoordinator`, `SynologyDSMSwitchUpdateCoordinator`). Entities typically get their data from these coordinators or from the `SynoApi` object, which is updated by the coordinator. Direct event subscriptions from the underlying `py-synologydsm-api` library are not the primary update mechanism for most entities.

However, the integration *does* implement subscription/registration logic tied to the entity lifecycle:

1.  **Base Entity Registration (`homeassistant/components/synology_dsm/entity.py`)**: The `SynologyDSMBaseEntity` class, which is the base for most entities, implements `async_added_to_hass`. Inside this method, it calls `self.async_on_remove(self._api.subscribe(self.entity_description.api_key, self.unique_id))`.
    *   Looking at `homeassistant/components/synology_dsm/common.py`, the `SynoApi.subscribe` method adds the entity's unique ID to an internal set (`_fetching_entities`) based on the API key. This set is used by the `SynoApi`'s `_setup_api_requests` method (called by the coordinator's update) to determine which sections of the DSM API need to be polled.
    *   The `SynoApi.subscribe` method returns a callable function that removes the unique ID from the set.
    *   By wrapping `_api.subscribe` with `self.async_on_remove`, the integration correctly ties the registration for API polling needs to the entity's `async_added_to_hass` and the deregistration to the entity's removal lifecycle. This follows the spirit and mechanism of the rule for managing registrations/subscriptions within entities.

2.  **Camera Signal Subscription (`homeassistant/components/synology_dsm/camera.py`)**: The `SynoDSMCamera` entity specifically subscribes to a Home Assistant dispatcher signal (`SIGNAL_CAMERA_SOURCE_CHANGED`) in its `async_added_to_hass` method using `async_dispatcher_connect`. This signal is dispatched by the `SynologyDSMCameraUpdateCoordinator` when a camera's RTSP source changes.
    *   The `async_dispatcher_connect` function returns a callable that can be used to unsubscribe.
    *   The integration correctly wraps this call in `self.async_on_remove(async_dispatcher_connect(...))`. This ensures that the entity subscribes to the signal when added to Home Assistant and the subscription is automatically cleaned up when the entity is removed, aligning perfectly with the rule's example for event/signal subscriptions.

Both instances where subscriptions or registrations tied to the entity lifecycle are performed (`SynoApi.subscribe` in the base entity and dispatcher signal subscription in the camera entity) correctly use `async_added_to_hass` in conjunction with `self.async_on_remove()` for cleanup, which is the recommended pattern to satisfy this rule.

## Suggestions

No suggestions needed. The integration follows the rule by correctly managing subscriptions/registrations within the required entity lifecycle methods using `async_added_to_hass` and `self.async_on_remove`.
```

_Created at 2025-05-25 11:46:42. Prompt tokens: 39666, Output tokens: 933, Total tokens: 42289_
