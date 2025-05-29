```markdown
# synology_dsm: parallel-updates

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [parallel-updates](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/parallel-updates)                                                     |
| Status | **todo**                                                                 |
| Reason |                                                                          |

## Overview

This rule requires integrations to explicitly define `PARALLEL_UPDATES` in their platform files. The purpose is to control the number of concurrent requests sent to a device or service, which is important for devices sensitive to high request rates.

The `synology_dsm` integration utilizes data update coordinators (`SynologyDSMCentralUpdateCoordinator`, `SynologyDSMSwitchUpdateCoordinator`, `SynologyDSMCameraUpdateCoordinator`) defined in `coordinator.py`. Entities inherit from `SynologyDSMBaseEntity`, which in turn inherits from `CoordinatorEntity` (`entity.py`). When using coordinators, the recommended practice for read-only platforms is to set `PARALLEL_UPDATES = 0`, as the coordinator handles the data fetching and potential limiting.

The provided code does not define the `PARALLEL_UPDATES` constant in any of the platform files (`binary_sensor.py`, `sensor.py`, `camera.py`, `switch.py`, `button.py`, `update.py`). The absence of this constant means Home Assistant defaults to allowing unlimited parallel updates for entities within that platform. While the coordinators manage the rate of requests to the Synology DSM API for data updates, the rule explicitly requires the constant to be set, even when using a coordinator, to clarify that platform-level parallelism for updates is not needed or desired.

Therefore, the integration does not fully follow the rule by not explicitly setting `PARALLEL_UPDATES`.

## Suggestions

To comply with the `parallel-updates` rule, add the line `PARALLEL_UPDATES = 0` at the top of each platform file that creates entities relying on a coordinator for data updates. This explicitly signals that the platform itself does not require entity-level parallelism for updates because the coordinator handles the data source.

The relevant files are:
*   `homeassistant/components/synology_dsm/binary_sensor.py`
*   `homeassistant/components/synology_dsm/sensor.py`
*   `homeassistant/components/synology_dsm/camera.py`
*   `homeassistant/components/synology_dsm/switch.py`
*   `homeassistant/components/synology_dsm/update.py`

For example, add `PARALLEL_UPDATES = 0` to the top of `homeassistant/components/synology_dsm/binary_sensor.py`:

```python
"""Support for Synology DSM binary sensors."""

from __future__ import annotations

from dataclasses import dataclass

from synology_dsm.api.core.security import SynoCoreSecurity
from synology_dsm.api.storage.storage import SynoStorage

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import CONF_DISKS, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SynoApi
from .coordinator import SynologyDSMCentralUpdateCoordinator, SynologyDSMConfigEntry
from .entity import (
    SynologyDSMBaseEntity,
    SynologyDSMDeviceEntity,
    SynologyDSMEntityDescription,
)

# Add this line
PARALLEL_UPDATES = 0

@dataclass(frozen=True, kw_only=True)
... rest of the file
```

Repeat this for `sensor.py`, `camera.py`, `switch.py`, and `update.py`. The `button.py` platform defines buttons that trigger actions, not entities that poll for state updates via a coordinator in the typical sense that `PARALLEL_UPDATES` is applied, so adding it there is not strictly necessary based on the rule's focus on updates, but doing so for consistency across entity platforms might be considered. However, the primary goal is to address the platforms with updating entities.
```

_Created at 2025-05-25 11:48:55. Prompt tokens: 39458, Output tokens: 982, Total tokens: 42425_
