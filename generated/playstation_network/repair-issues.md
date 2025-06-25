# playstation_network: repair-issues

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [playstation_network](https://www.home-assistant.io/integrations/playstation_network/) |
| Rule   | [repair-issues](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/repair-issues)                                                     |
| Status | **done**                                                                 |

## Overview

The `repair-issues` rule is applicable to the `playstation_network` integration. As a cloud-based service using a token (`npsso`) for authentication, there's a clear scenario where user intervention is required: when the token expires or becomes invalid.

The integration correctly handles this scenario and thus follows the rule. The implementation uses the standard Home Assistant mechanism for signaling authentication failures that require user action.

In `homeassistant/components/playstation_network/coordinator.py`, the `PlaystationNetworkCoordinator` handles data updates. Both the initial setup (`_async_setup`) and subsequent updates (`_async_update_data`) have error handling for authentication issues:

```python
# coordinator.py

class PlaystationNetworkCoordinator(DataUpdateCoordinator[PlaystationNetworkData]):
    # ...
    async def _async_setup(self) -> None:
        """Set up the coordinator."""
        try:
            self.user = await self.psn.get_user()
        except PSNAWPAuthenticationError as error:
            raise ConfigEntryAuthFailed(  # This triggers the repair flow
                translation_domain=DOMAIN,
                translation_key="not_ready",
            ) from error

    async def _async_update_data(self) -> PlaystationNetworkData:
        """Get the latest data from the PSN."""
        try:
            return await self.psn.get_data()
        except PSNAWPAuthenticationError as error:
            raise ConfigEntryAuthFailed(  # This triggers the repair flow
                translation_domain=DOMAIN,
                translation_key="not_ready",
            ) from error
        except PSNAWPServerError as error:
            raise UpdateFailed(...) from error
```

When a `PSNAWPAuthenticationError` is caught, the coordinator raises `homeassistant.exceptions.ConfigEntryAuthFailed`. This is the designated exception in Home Assistant for this purpose. Raising `ConfigEntryAuthFailed` instructs Home Assistant Core to:
1.  Put the configuration entry into a failed state.
2.  Automatically create a repair issue in the Repairs dashboard.
3.  Initiate a re-authentication flow, allowing the user to provide a new, valid `npsso` token.

This behavior perfectly aligns with the rule's requirement to use the repair system for actionable issues. By raising the correct exception, the integration leverages the built-in repair mechanism for authentication problems. Other, non-actionable issues like server errors correctly raise `UpdateFailed`, which does not create a repair issue.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 19:09:31 using gemini-2.5-pro. Prompt tokens: 9440, Output tokens: 669, Total tokens: 12374._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
