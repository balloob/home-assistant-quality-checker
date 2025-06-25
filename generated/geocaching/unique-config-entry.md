# geocaching: unique-config-entry

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [geocaching](https://www.home-assistant.io/integrations/geocaching/) |
| Rule   | [unique-config-entry](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/unique-config-entry)                                                     |
| Status | **done**                                                                 |

## Overview

The `unique-config-entry` rule applies to this integration as it uses a configuration flow to set up a connection to a specific user account on the Geocaching service. It is essential to prevent users from accidentally configuring the same account multiple times, which could lead to duplicated entities.

The `geocaching` integration correctly follows this rule by using the user's Geocaching username as a unique identifier for the configuration entry.

In `config_flow.py`, the `async_oauth_create_entry` method is responsible for finalizing the configuration after a successful OAuth2 authentication. The implementation is as follows:

1.  It uses the newly acquired token to fetch the user's profile from the Geocaching API.
2.  It extracts the user's username from the profile data.
3.  It then calls `await self.async_set_unique_id(status.user.username.lower())`. This helper method sets the unique ID for the flow and checks if another entry with the same unique ID already exists.
4.  If an `existing_entry` is found, the flow is treated as a re-authentication. The existing entry's token is updated, and the new flow is aborted with a `reauth_successful` reason. This prevents the creation of a duplicate entry.
5.  If no `existing_entry` is found, a new configuration entry is created.

This implementation perfectly aligns with the "Unique identifier" example provided in the rule's documentation.

```python
# homeassistant/components/geocaching/config_flow.py

    async def async_oauth_create_entry(self, data: dict[str, Any]) -> ConfigFlowResult:
        """Create an oauth config entry or update existing entry for reauth."""
        api = GeocachingApi(
            environment=ENVIRONMENT,
            token=data["token"]["access_token"],
            session=async_get_clientsession(self.hass),
        )
        status = await api.update()
        if not status.user or not status.user.username:
            return self.async_abort(reason="oauth_error")

        # This call sets the unique ID and checks for duplicates.
        if existing_entry := await self.async_set_unique_id(
            status.user.username.lower()
        ):
            self.hass.config_entries.async_update_entry(existing_entry, data=data)
            await self.hass.config_entries.async_reload(existing_entry.entry_id)
            return self.async_abort(reason="reauth_successful")
        
        # This only runs if no entry with the unique_id exists.
        return self.async_create_entry(title=status.user.username, data=data)
```

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 18:51:06 using gemini-2.5-pro-preview-06-05. Prompt tokens: 6405, Output tokens: 739, Total tokens: 8530._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
