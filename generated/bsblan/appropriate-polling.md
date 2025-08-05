# bsblan: appropriate-polling

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [bsblan](https://www.home-assistant.io/integrations/bsblan/) |
| Rule   | [appropriate-polling](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/appropriate-polling)                                                     |
| Status | **todo**                                                                 |

## Overview

The `appropriate-polling` rule applies to this integration because `bsblan` is a polling-based integration, as declared by its `"iot_class": "local_polling"` in the `manifest.json` file. It uses a `DataUpdateCoordinator` to periodically fetch data from a BSB-Lan device, which controls a heating system.

While the integration correctly implements a polling interval using the `update_interval` parameter of the `DataUpdateCoordinator`, the chosen interval is not appropriate for the type of device being polled.

The polling interval is defined in `homeassistant/components/bsblan/const.py`:
```python
# homeassistant/components/bsblan/const.py
SCAN_INTERVAL = timedelta(seconds=12)
```

This `SCAN_INTERVAL` is then used in `homeassistant/components/bsblan/coordinator.py` to set the coordinator's update interval, with a small random jitter added:
```python
# homeassistant/components/bsblan/coordinator.py
class BSBLanUpdateCoordinator(DataUpdateCoordinator[BSBLanCoordinatorData]):
    # ...
    def __init__(
        self,
        # ...
    ) -> None:
        """Initialize the BSB-Lan coordinator."""
        super().__init__(
            # ...
            update_interval=self._get_update_interval(),
        )
        # ...
    def _get_update_interval(self) -> timedelta:
        # ...
        return SCAN_INTERVAL + timedelta(seconds=randint(1, 8))
```
This results in a polling frequency of every 13 to 20 seconds. For a heating system, where temperatures and operational states change very slowly, this interval is excessively frequent. It creates unnecessary network traffic and load on both Home Assistant and the BSB-Lan device.

As the rule's documentation states, "we should not poll an air quality sensor every 5 seconds, as the data will not change that often... more than 99% of the users will be fine with a polling interval of a minute or more." This principle applies directly to a heating system, where an interval of 60 seconds or more would be far more appropriate for the default setting.

## Suggestions

To comply with the rule, the default polling interval should be increased to a more reasonable value for a heating system. A value of 60 seconds is recommended as a more appropriate default.

In `homeassistant/components/bsblan/const.py`, change the value of `SCAN_INTERVAL`:

```diff
--- a/homeassistant/components/bsblan/const.py
+++ b/homeassistant/components/bsblan/const.py
@@ -7,7 +7,7 @@
 DOMAIN: Final = "bsblan"
 
 LOGGER = logging.getLogger(__package__)
-SCAN_INTERVAL = timedelta(seconds=12)
+SCAN_INTERVAL = timedelta(seconds=60)
 
 # Services
 DATA_BSBLAN_CLIENT: Final = "bsblan_client"

```

This change will set a default polling interval of approximately one minute, which is sufficient for monitoring a heating system while significantly reducing the load on the device. Users who require more frequent updates can still [define a custom polling interval](https://www.home-assistant.io/common-tasks/general/#defining-a-custom-polling-interval) for their specific needs.

---

_Created at 2025-08-05 09:35:26 using gemini-2.5-pro. Prompt tokens: 11153, Output tokens: 857, Total tokens: 13893._

_Report based on [`ee9ff71`](https://github.com/home-assistant/core/tree/ee9ff717e0d36ca02bf52a242acd3a47359eae61)._

_AI can be wrong. Always verify the report and the code against the rule._
