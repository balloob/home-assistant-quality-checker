# playstation_network: stale-devices

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [playstation_network](https://www.home-assistant.io/integrations/playstation_network/) |
| Rule   | [stale-devices](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/stale-devices)                                                     |
| Status | **todo**                                                                 |

## Overview

The `stale-devices` rule applies to the `playstation_network` integration as it creates devices in Home Assistant. Specifically, it creates a main service device for the PlayStation Network account and child devices for each associated gaming platform (e.g., PlayStation 5, PlayStation 4).

The integration currently does not follow this rule. In `media_player.py`, logic exists to dynamically add `MediaPlayer` entities (and their associated devices) for new platforms as they are detected. However, there is no corresponding mechanism to remove these devices if a platform is permanently removed from the user's account (for example, if a console is sold).

This can lead to a cluttered UI with stale, non-functional devices. The integration neither implements automatic removal logic in the coordinator nor provides the `async_remove_config_entry_device` function for manual user removal.

The coordinator in `coordinator.py` fetches all required data but does not track the set of known devices between updates to identify and prune any that have become stale.

## Suggestions

To comply with this rule, the integration should implement automatic stale device removal within the `PlaystationNetworkCoordinator`. The coordinator should track the set of registered platforms and remove devices that are no longer reported by the API.

The `helpers.py` file already retrieves the definitive list of platforms associated with the account into `data.registered_platforms`. This should be used as the source of truth.

Here are the recommended changes for `homeassistant/components/playstation_network/coordinator.py`:

1.  Add necessary imports for the device registry and `PlatformType`.
2.  Initialize a set in the coordinator's `__init__` method to store the platforms from the previous update.
3.  In `_async_update_data`, compare the current list of platforms with the previous list and remove any devices for platforms that are no longer present.

```python
# homeassistant/components/playstation_network/coordinator.py

from __future__ import annotations

from datetime import timedelta
import logging

from psnawp_api.core.psnawp_exceptions import (
    PSNAWPAuthenticationError,
    PSNAWPServerError,
)
from psnawp_api.models.trophies import PlatformType  # Ensure this is imported
from psnawp_api.models.user import User

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import device_registry as dr  # Import device_registry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .helpers import PlaystationNetwork, PlaystationNetworkData

_LOGGER = logging.getLogger(__name__)

type PlaystationNetworkConfigEntry = ConfigEntry[PlaystationNetworkCoordinator]


class PlaystationNetworkCoordinator(DataUpdateCoordinator[PlaystationNetworkData]):
    """Data update coordinator for PSN."""

    config_entry: PlaystationNetworkConfigEntry
    user: User
    previous_platforms: set[PlatformType]  # Add type hint

    def __init__(
        self,
        hass: HomeAssistant,
        psn: PlaystationNetwork,
        config_entry: PlaystationNetworkConfigEntry,
    ) -> None:
        """Initialize the Coordinator."""
        super().__init__(
            hass,
            name=DOMAIN,
            logger=_LOGGER,
            config_entry=config_entry,
            update_interval=timedelta(seconds=30),
        )

        self.psn = psn
        self.previous_platforms = set()  # Initialize the set

    async def _async_setup(self) -> None:
        # ... (no changes needed here)

    async def _async_update_data(self) -> PlaystationNetworkData:
        """Get the latest data from the PSN."""
        try:
            data = await self.psn.get_data()
        except PSNAWPAuthenticationError as error:
            raise ConfigEntryAuthFailed(
                translation_domain=DOMAIN,
                translation_key="not_ready",
            ) from error
        except PSNAWPServerError as error:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="update_failed",
            ) from error

        # ---- Start of suggested addition ----
        # The definitive list of platforms associated with the account.
        current_platforms = data.registered_platforms
        if self.previous_platforms and (stale_platforms := self.previous_platforms - current_platforms):
            device_registry = dr.async_get(self.hass)
            if self.config_entry.unique_id:
                for platform in stale_platforms:
                    # The identifier for the platform's device.
                    device_identifier = f"{self.config_entry.unique_id}_{platform.value}"
                    device = device_registry.async_get_device(
                        identifiers={(DOMAIN, device_identifier)}
                    )
                    if device:
                        # This will orphan the device, allowing HA to clean it up,
                        # which also removes associated entities.
                        device_registry.async_update_device(
                            device_id=device.id,
                            remove_config_entry_id=self.config_entry.entry_id,
                        )
        self.previous_platforms = current_platforms
        # ---- End of suggested addition ----

        return data

```

By implementing this logic, the integration will automatically clean up devices that are no longer part of the user's PlayStation Network account, ensuring Home Assistant stays in sync and fully compliant with the `stale-devices` rule.

---

_Created at 2025-06-25 19:10:29 using gemini-2.5-pro. Prompt tokens: 9890, Output tokens: 1366, Total tokens: 15896._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
